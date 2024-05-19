#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : views.py
Description      : 
Time             : 2023/08/13 14:34:06
Author           : AllenLuo
Version          : 1.0
'''


from chatgpt_user.serializers import (
    LoginSerializer,
    RegisterDetailSerializer,
    UserInfoSerializer,
    ResetPasswordSerializer,
    EmailVerifyCodeSerializer
)
from utils.viewset import CustomModelViewSet
from utils.json_response import DetailResponse, ErrorResponse
from .models import FrontUserExtraEmail, CustomerCaptchaStore, EmailVerifyCode, FrontUserBase
from loguru import logger
from django.utils import timezone
import base64
from rest_framework.decorators import action
from captcha.views import captcha_image
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
import string
import random
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import datetime
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from faker import Faker
import jwt
from rest_framework.permissions import AllowAny
from rest_framework import permissions
from django.shortcuts import render
from chatgpt_config.models import Config, UserConfig
from chatgpt_user.models import CheckIn, UserBenefits, UserRedeem
import json
from apscheduler.schedulers.background import BackgroundScheduler # 使用它可以使你的定时任务在后台运行
from django_apscheduler.jobstores import DjangoJobStore, register_job
from chatgpt_config.models import get_chatModel_list
import os
from chatgpt_bootstrap.settings import BASE_DIR
from utils.request_util import get_request_ip

#开启定时工作
try:
    # 实例化调度器
    scheduler = BackgroundScheduler()
    # 调度器使用DjangoJobStore()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # 每天固定时间执行任务，对应代码为：
    @register_job(scheduler, 'cron', hour='1', minute='56', second='40',id='task', replace_existing=True )
    def my_job():
        res = FrontUserBase.objects.filter(vip_expire_at__lt=timezone.now(), VIP_TYPE=1).values()
        if res:
            logger.info(f"开始重置用户{[id['id'] for id in res]}VIP状态")
            for id in res:
                # 更新会员状态和用户配置表
                baseUserId = id['id']
                update_datetime = datetime.datetime.now()
                FrontUserBase.objects.filter(id=baseUserId).update(VIP_TYPE=0, update_datetime=update_datetime)
                UserConfig.objects.filter(baseUserId=baseUserId).update(chatModel='gpt-3.5-turbo' ,chatModelList=get_chatModel_list(),update_datetime=update_datetime)
                UserBenefits.objects.filter(baseUserId=baseUserId).update(left_tokens=0, left_dalle=0,update_datetime=update_datetime)
            logger.info("已重置vip用户状态")
        
        audio_file_path = os.path.join(BASE_DIR, 'static', 'AudioFiles')
        # 删除音频文件
        file_names = os.listdir(audio_file_path)
        if file_names:
          file_list = [os.path.join(audio_file_path, i) for i in file_names]
          for i in file_list:
            os.remove(i)
          logger.info(f'{file_list}-音频文件已删除')

    scheduler.start()
except Exception as e:
    logger.error(f"定时任务异常-{e}")


def send_verification_email(request, to_email, verify_code,verify_ip, expire_at, template='register_verify_email.html', verificationUrl=None):
    """ 邮件发送方法 
    """
    subject = settings.EMAIL_SUBJECT
    # 使用render_to_string函数将register_verify_email.html渲染为HTML内容
    html_content = render_to_string(template, {'verificationUrl': verificationUrl})
    # 创建EmailMessage对象，并设置相关属性
    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    # 设置邮件内容类型为html
    email.content_subtype = 'html'
    # 发送邮件
    email.send()
    EmailVerifyCode.objects.create(to_email_address=to_email, verify_code=verify_code, verify_ip=verify_ip, expire_at=expire_at).save()
    logger.info(f"邮件发送成功,接收人:{to_email}, 请求人IP:{verify_ip}")


class CaptchaView(APIView):
    @swagger_auto_schema(
        responses={"200": openapi.Response('获取成功')},
        security=[],
        operation_id="captcha-get",
        operation_description="图形验证码获取",
    )
    def get(self, request):
        data = {}
        hashkey = CustomerCaptchaStore.generate_key()
        picCodeSessionId = CustomerCaptchaStore.objects.filter(hashkey=hashkey).first().pic_code_seesion_id
        imgage = captcha_image(request, hashkey)
        # 将图片转换为base64
        image_base = base64.b64encode(imgage.content)
        data = {
            "picCodeSessionId": picCodeSessionId,
            "picCodeBase64": image_base.decode("utf-8"),
        }
        return DetailResponse(data=data, msg='OK')


class RegisterModelViewSet(CustomModelViewSet):
    """
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    serializer_class = [RegisterDetailSerializer, ]

    @swagger_auto_schema(method='post', 
        request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
          'identity': openapi.Schema(type=openapi.TYPE_STRING, description='用户ID，可以为邮箱，可以为手机号'),
          'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码'),
          'picCodeSessionId': openapi.Schema(type=openapi.TYPE_STRING, description='图形验证码会话 ID'),
          'picVerificationCode': openapi.Schema(type=openapi.TYPE_STRING, description='图片验证码'),
          'registerType': openapi.Schema(type=openapi.TYPE_STRING, enum=['email', 'phone'], description='注册类型: email, phone'),
        },
        required=['custom_field'],
        responses={"200": openapi.Response("注册成功")},
    ))
    @action(methods=['POST'],detail=False)
    def create(self, request):
        """ 注册方法
        """
        username = request.data.get('identity',None)
        if not username:
            return ErrorResponse(msg="账号不能为空")
        password = request.data.get('password',None)
        if not password:
            return ErrorResponse(msg="密码不能为空")
        picVerificationCode = request.data.get('picVerificationCode',None)
        if not picVerificationCode:
            return ErrorResponse(msg="验证码不能为空")

        picCodeSessionId = request.data.get('picCodeSessionId',None)
        try:
          self.image_code = CustomerCaptchaStore.objects.filter(pic_code_seesion_id=picCodeSessionId).first()
          self._expiration = CustomerCaptchaStore.objects.get(pic_code_seesion_id=picCodeSessionId).expiration
          if  timezone.now()  > self._expiration:  # 先判断是否过期
            return ErrorResponse(msg="验证码过期,请刷新重试") 
          elif  self.image_code and (self.image_code.response == picVerificationCode or self.image_code.challenge == picVerificationCode):
              self.image_code.delete() # 验证通过将数据库存储的验证码删除
          else:
              return ErrorResponse(msg="验证码错误,请输入正确的验证码")
        except:
              return ErrorResponse(msg="验证码错误,请刷新重试")


        salt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
        record, b = FrontUserExtraEmail.objects.get_or_create(username=username, verified=1, 
            defaults={            
            'password':self.set_password(password,salt),
            'salt': salt,
             'verified': 0
            })
        if not b:
            msg = "该账号已注册,请登录"
            logger.warning(f"{username}-该账号已注册,请登录")
            return ErrorResponse(msg=msg)
        verify_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
        VERIFICATION_REDIRECT_URL = Config.objects.filter(config_Code='email_config', key='VERIFICATION_REDIRECT_URL').first().value
        verificationUrl = VERIFICATION_REDIRECT_URL + verify_code
        logger.debug(f'verificationUrl:{verificationUrl}')
        expire_at = timezone.now() + datetime.timedelta(minutes=int(settings.EMAIL_TIMEOUT))
        verify_ip = get_request_ip(request)


        template = 'register_verify_email.html'
        send_verification_email(request, username, verify_code, verify_ip, expire_at, template, verificationUrl)
        return DetailResponse(data={})


    def set_password(self, raw_password, salt):
        """
        Description: 密码加密方法
        ---------
        Arguments: raw_password： 原始密码
                   salt： 加密盐
        ---------
        Returns:   使用加密盐加密之后的密码
        -------
        """
        salted_password = make_password(raw_password, salt)
        return salted_password


    def check_password(self, password, salted_password) -> bool:
        """ 密码解密方法
        """
        is_valid = check_password(password, salted_password)
        return is_valid

class ResetPassword(CustomModelViewSet):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def reset_password(self, request):
        """ 密码重置方法
        """
        username=request.user.username
        FrontUserBaseInstance = FrontUserBase.objects.filter(username=username).first()
        serializer = ResetPasswordSerializer(data= request.data)
        if serializer.is_valid(raise_exception=True):
          req_data = serializer.validated_data
          salt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
          encode_password = make_password(req_data['password'], salt)
          serializer.update(instance=FrontUserBaseInstance, validated_data={"password": encode_password, "salt": salt})
          return DetailResponse(msg="密码重置成功")

class ResetPasswordNotLogin(CustomModelViewSet):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny, ]

    def reset_password_not_login(self, request):
        """ 密码重置方法
        """
        serializer = ResetPasswordSerializer(data= request.data)
        if serializer.is_valid(raise_exception=True):
          username=request.data['to_email_address']
          FrontUserBaseInstance = FrontUserBase.objects.filter(username=username).first()   
          if not FrontUserBaseInstance:
            return ErrorResponse(msg="邮箱不存在,请确认")

          req_data = serializer.validated_data
          emailVerficationCode = req_data['emailVerficationCode']
          verify_status = EmailVerifyCode.objects.filter(to_email_address=username, verify_code=emailVerficationCode, expire_at__gt=timezone.now()).first()
          if not verify_status:
            return ErrorResponse(msg="邮箱验证码错误,请检查")

          picVerificationCode = request.data.get('picVerificationCode',None)
          if not picVerificationCode:
              return ErrorResponse(msg="验证码不能为空")
          picCodeSessionId = request.data.get('picCodeSessionId',None)
          try:
            self.image_code = CustomerCaptchaStore.objects.filter(pic_code_seesion_id=picCodeSessionId).first()
            self._expiration = CustomerCaptchaStore.objects.get(pic_code_seesion_id=picCodeSessionId).expiration
            if  timezone.now()  > self._expiration:  # 先判断是否过期
              return ErrorResponse(msg="验证码过期,请刷新重试") 
            elif  self.image_code and (self.image_code.response == picVerificationCode or self.image_code.challenge == picVerificationCode):
                self.image_code.delete() # 验证通过将数据库存储的验证码删除
            else:
                return ErrorResponse(msg="验证码错误,请输入正确的验证码")
          except:
                return ErrorResponse(msg="验证码错误,请刷新重试")
       
          salt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
          encode_password = make_password(req_data['password'], salt)
          serializer.update(instance=FrontUserBaseInstance, validated_data={"password": encode_password, "salt": salt})
          return DetailResponse(msg="密码重置成功")

class verifyEmailCodeViewSet(CustomModelViewSet):
    """ 注册校验邮件验证码方法
    """
    serializer_class = UserInfoSerializer

    def list(self, request):
      verifyCode = request.GET.get('code')
      verifyCode_value = EmailVerifyCode.objects.filter(verify_code=verifyCode, expire_at__gt=timezone.now()).first()
      if verifyCode_value:
          username = EmailVerifyCode.objects.filter(verify_code=verifyCode_value.verify_code).first().to_email_address
          # 核销认证通过
          res = FrontUserExtraEmail.objects.filter(username=username).first()
          res.verified = 1 # 先更新认证状态
          res.update_datetime = timezone.now()
          res.save()   

          # 获取最新一次注册时使用的密码及加密盐
          password = res.password
          salt = res.salt

          faker = Faker()
          faker.word()
          nikename = "ChatAI_" + faker.word()
          ip = get_request_ip(request)
          # 邮箱注册验证通过写入用户基础信息表
          FrontUserBase.objects.create(username=username, nickname=nikename, password=password, salt=salt, last_login_ip=ip)
          baseUserId= FrontUserBase.objects.filter(username=username).first().id
          logger.info(baseUserId)
          # 邮箱注册验证通过写入用户配置表
          UserConfig.objects.create(baseUserId=baseUserId)
          # 邮箱注册验证通过写入用户福利表
          UserBenefits.objects.create(baseUserId=baseUserId)

          msg = f"{username}注册邮件核销成功"
          logger.info(msg)
          return DetailResponse(msg)
      else:
          return ErrorResponse(msg='验证码过期或不存在,请重新注册')

class verifyResetPasswordEmailCodeViewSet(CustomModelViewSet):
    """ 密码重置校验邮件验证码方法
    """
    serializer_class = EmailVerifyCodeSerializer
    permission_classes = (AllowAny,)

    def send(self, request, *args, **kwargs):
        serializer = EmailVerifyCodeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
          verify_code = ''.join(random.choice(string.digits) for _ in range(6))
          req_data = serializer.validated_data
          logger.info(req_data)
          to_email_address = req_data['to_email_address']
          if not FrontUserBase.objects.filter(username=to_email_address).first():
              return ErrorResponse(msg="该邮箱未注册,请检查或发起注册")
          
          expire_at = timezone.now() + datetime.timedelta(minutes=int(settings.EMAIL_TIMEOUT))
          verify_ip = get_request_ip(request)
          serializer.save(to_email_address=to_email_address, verify_code=verify_code, verify_ip=verify_ip, expire_at=expire_at, biz_type=11)
          template = 'reset_password_verify_email.html'
          send_verification_email(request, to_email_address, verify_code, verify_ip, expire_at, template, verificationUrl=verify_code)
          return DetailResponse()


class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # 使用自定义用户信息生成Token的逻辑
        # 返回一个唯一标识用户的字符串
        return f"{user.id}{timestamp}"
    


class LoginViewSet(CustomModelViewSet):
    """
    登录接口
    """
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        username = request.data.get('username',None)
        if username is None:
            return ErrorResponse(msg="账号不能为空")
        password = request.data.get('password',None)
        if password is None:
            return ErrorResponse(msg="密码不能为空")
        user = FrontUserExtraEmail.objects.filter(username=username).first()
        res = FrontUserBase.objects.filter(username=username).first()

        if not res:  # 检查账号是否存在及是否验证完成
            logger.warning(f"{username}未注册")
            return ErrorResponse(msg='账号未注册')
        if user.verified != 1:
            logger.warning(f"{username}注册流程未完成")
            return ErrorResponse(msg='注册流程未完成,请完成注册或重新注册')
        
        salted_password = res.password
        if not check_password(password, salted_password):    # 检查密码是否正确
            logger.warning(f"{user}账号/密码不匹配")
            return ErrorResponse(msg='账号/密码不匹配')
        token = LoginSerializer.get_token(res).access_token  # 生成access_token
        baseUserId = res.id
        result = {
            "token": str(token),
            "baseUserId": baseUserId,
        }
        logger.success(f"{username}登录成功")
        update_datetime = datetime.datetime.now()
        FrontUserBase.objects.filter(id=baseUserId).update(last_login_ip=get_request_ip(request), update_datetime=update_datetime)
        return DetailResponse(data=result)


class UserInfoViewSet(CustomModelViewSet):
    serializer_class = UserInfoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        token = request.headers.get('Authorization').split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        customer_id=decoded_token["id"]
        res = FrontUserBase.objects.filter(id=customer_id).first()
        res_user = UserConfig.objects.filter(baseUserId=customer_id).first()
        result = {
                "baseUserId": customer_id,
                "nickname": res.nickname,
                "email": res.username,
                "description": res.description,
                "avatarUrl": res.avatar_version,
                "chatModel": res_user.chatModel,
                "chatModelList": res_user.chatModelList
        }
        return DetailResponse(data=result)


def dashboard(request):
    user_count = FrontUserBase.objects.count()

    context = { 'user_count': user_count, 'task_count': 0 }
    return render(request, 'dashboard.html',context)

def VIP_User_config_list():
    with open ('./VIP_config.json', 'r', encoding='utf-8') as default_config:
      return json.loads(default_config.read())

class Redeem(CustomModelViewSet):
  permission_classes = [permissions.IsAuthenticated]

  def user_redeem_gerenate(self, request):
      baseUserId = request.user.id
      redeem_code = request.data.get('redeemCode', None)
      res = UserRedeem.objects.filter(redeem_code=redeem_code, expire_at__gt=timezone.now(), verified=0).first()
      if res:
        # 更新兑换表
        UserRedeem.objects.filter(redeem_code=redeem_code).update(baseUserId=baseUserId,verified=1)
        # 更新用户表
        expire_at = timezone.now() + datetime.timedelta(days=30)
        FrontUserBase.objects.filter(id=baseUserId).update(VIP_TYPE=1,vip_expire_at=expire_at)

        # 更新福利表
        benefit_res = UserBenefits.objects.filter(baseUserId=baseUserId).first()
        benefit_res.total_benefits_tokens += res.redeem_tokens
        benefit_res.total_benefits_dalle += res.redeem_dalle
        benefit_res.left_tokens += res.redeem_tokens
        benefit_res.left_dalle += res.redeem_dalle
        benefit_res.benefits_source = 1
        benefit_res.save()

        # 更新用户配置表
        UserConfig.objects.filter(baseUserId=baseUserId).update(chatModelList=VIP_User_config_list())

        return DetailResponse()
      else:
        return ErrorResponse(msg='兑换码无效或过期,请检查')


class SignIn(CustomModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def check_in(self, request):
        baseUserId = request.user.id
        if request.method == 'POST':
          res, flag =CheckIn.objects.get_or_create(baseUserId=baseUserId, create_datetime__day=timezone.now().day)
          if flag: 
            # 每天首次签到赠送福利
            res = UserBenefits.objects.filter(baseUserId=baseUserId).first()
            res.total_benefits_tokens +=2000
            res.total_benefits_dalle +=2
            res.left_tokens +=2000
            res.left_dalle +=2
            res.save()

          return DetailResponse(msg='今日已签到成功,快去使用吧')
        elif request.method == 'GET':
          user_check_in_data = CheckIn.objects.filter(baseUserId=baseUserId, create_datetime__month=timezone.now().month)
          data = {"checked_in_date":[f"{date.check_in_date.timetuple().tm_year}-{date.check_in_date.timetuple().tm_mon}-{date.check_in_date.timetuple().tm_mday}" for date in user_check_in_data]} 
          return DetailResponse(data=data)
        



        
