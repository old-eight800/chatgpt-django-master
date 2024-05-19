from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from captcha.views import CaptchaStore
from django.contrib.auth.models import AbstractUser
import random
import string
from django.utils import timezone
from django.conf import settings
import datetime

class CustomerCaptchaStore(CaptchaStore):
    pic_code_seesion_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class FrontUserExtraEmail(models.Model):
    
    VERIFIED_STATUS_CHOICES = (
        (0, _('unverified')),
        (1, _('verified')),
    )
    id = models.AutoField(primary_key=True)
    username = models.EmailField(max_length=255, verbose_name="注册用户,暂只支持邮箱", null=True, blank=True, help_text="注册用户,暂只支持邮箱")
    password = models.CharField(max_length=255, verbose_name="登录密码", null=True, blank=True, help_text="密码")
    salt = models.CharField(max_length=255, verbose_name="密码盐值", null=True, blank=True, help_text="加密密码盐值")
    verified = models.IntegerField(verbose_name="是否验证", choices=VERIFIED_STATUS_CHOICES, default=0, help_text="是否验证 0 否 1 是")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间", verbose_name="创建时间")
    

    class Meta:
        db_table = "front_user_extra_email"
        verbose_name = "用户邮箱注册记录表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class EmailVerifyCode(models.Model):
    
    BIZ_TYPE_CHOICES = (
        (10, _('注册认证')),
        (11, _('密码重置认证')),
    )
    id = models.AutoField(primary_key=True)
    to_email_address = models.EmailField(max_length=64, verbose_name="验证码接收邮箱", null=True, blank=True, help_text="验证码接收邮箱")
    verify_code = models.CharField(max_length=64, verbose_name="邮箱验证码", null=True, blank=True, help_text="邮箱验证码")
    verify_ip = models.CharField(max_length=128, verbose_name="验证IP", null=True, blank=True, help_text="验证IP")
    expire_at = models.DateTimeField(verbose_name="验证码过期时间", null=True, blank=True, help_text="验证码过期时间")
    biz_type = models.IntegerField(verbose_name="验证码类型", choices=BIZ_TYPE_CHOICES, default=10, help_text="验证码类型")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间", verbose_name="创建时间")

    class Meta:
        db_table = "email_verify_code"
        verbose_name = "邮箱验证码核销记录表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class FrontUserBase(AbstractUser, models.Model):
  
    VIP_TYPE_CHOICES = (
        (0, _('普通用户')),
        (1, _('vip付费用户')),
    )

    id = models.AutoField(primary_key=True, unique=True, verbose_name="客户唯一编号", help_text="客户唯一编号")
    username = models.EmailField(max_length=255, unique=True, verbose_name="登录邮箱", null=True, blank=True, help_text="登录邮箱")
    nickname = models.CharField(max_length=32, verbose_name="用户昵称", null=True, blank=True, help_text="用户昵称")
    password = models.CharField(max_length=255, verbose_name="登录密码", null=True, blank=True, help_text="密码")
    salt = models.CharField(max_length=255, verbose_name="密码盐值", null=True, blank=True, help_text="密码盐值")
    description = models.CharField(max_length=255, verbose_name="描述", null=True, blank=True, help_text="描述")
    avatar_version = models.CharField(max_length=32, verbose_name="头像版本", null=True, blank=True, help_text="头像版本")
    VIP_TYPE = models.IntegerField(verbose_name="用户类型", choices=VIP_TYPE_CHOICES, default=0, help_text="用户类型")
    last_login_ip = models.CharField(max_length=128, verbose_name="上一次登录IP", null=True, blank=True, help_text="上一次登录IP")
    vip_expire_at = models.DateTimeField(verbose_name="vip过期时间", null=True, blank=True, help_text="vip过期时间")
    call_count = models.IntegerField(verbose_name="接口调用次数", default='0', null=True, blank=True, help_text="接口调用次数")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间", verbose_name="创建时间")
    USERNAME_FIELD = 'username'

    class Meta:
        db_table = "front_user_base"
        verbose_name = "用户基础信息表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


class SysEmailSendLog(models.Model):
    
    BIZ_TYPE_CHOICES = (
        (10, _('注册认证')),
        (11, _('找回密码认证')),
    )

    SEND_STATUS_CHOICES = (
        (1, _('发送成功')),
        (0, _('发送失败')),
    )
    id = models.AutoField(primary_key=True)
    from_email_address = models.EmailField(max_length=64, verbose_name="发件人邮箱", null=True, blank=True, help_text="发件人邮箱")
    to_email_address = models.EmailField(max_length=64, verbose_name="验证码接收邮箱", null=True, blank=True, help_text="验证码接收邮箱")
    biz_type = models.IntegerField(verbose_name="认证类型", choices=BIZ_TYPE_CHOICES, default=10, help_text="认证类型")
    request_ip = models.CharField(max_length=32, verbose_name="请求IP", null=True, blank=True, help_text="请求IP")
    content = models.TextField(verbose_name="发送内容", null=True, blank=True, help_text="发送内容")
    message_id = models.CharField(max_length=128, verbose_name="发送后会返回一个messageId", null=True, blank=True, help_text="发送后会返回一个messageId")
    status = models.IntegerField(verbose_name="发送状态", choices=SEND_STATUS_CHOICES, default=0, help_text="发送状态，0失败，1成功")
    message = models.CharField(max_length=255, verbose_name="发送后的消息，用于记录成功/失败的信息，成功默认为success", null=True, blank=True, help_text="发送后的消息，用于记录成功/失败的信息，成功默认为success")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间", verbose_name="创建时间")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")


    class Meta:
        db_table = "sys_email_send_log"
        verbose_name = "邮箱发送日志"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

  
class CheckIn(models.Model):
    id = models.AutoField(primary_key=True)
    baseUserId = models.IntegerField(verbose_name="用户ID", null=True, blank=True, help_text="签到用户")
    benefits_tokens = models.IntegerField(default=2000, verbose_name="签到赠送tokens", null=True, blank=True, help_text="签到赠送tokens")
    benefits_dalle = models.IntegerField(default=2, verbose_name="签到赠送dalle", null=True, blank=True, help_text="签到赠送dall-e-2,3")
    check_in_date = models.DateField(auto_now_add=True, null=True, blank=True, help_text="签到日期", verbose_name="签到日期")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="签到时间", verbose_name="创建时间")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")

    class Meta:
        db_table = "front_user_check_in"
        verbose_name = "用户签到表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

class UserBenefits(models.Model):
    
    BENEFITS_SOURCE_CHOICES = (
        (1, _('兑换')),
        (0, _('签到')),
    )
        
    id = models.AutoField(primary_key=True)
    baseUserId = models.IntegerField(verbose_name="用户ID", null=True, blank=True, help_text="用户ID")
    total_benefits_tokens = models.IntegerField(default=2000, verbose_name="累计赠送tokens", null=True, blank=True, help_text="累计赠送tokens")
    total_benefits_dalle = models.IntegerField(default=2, verbose_name="累计赠送dalle", null=True, blank=True, help_text="累计dalle-2,3")
    left_tokens = models.IntegerField(default=2000, verbose_name="剩余tokens", null=True, blank=True, help_text="剩余tokens")
    left_dalle = models.IntegerField(default=2, verbose_name="剩余dalle", null=True, blank=True, help_text="剩余dalle-2,3")
    benefits_source = models.IntegerField(verbose_name="福利来源", choices=BENEFITS_SOURCE_CHOICES, default=0, help_text="福利来源,0:签到,1:兑换")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间", verbose_name="创建时间")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")

    class Meta:
        db_table = "front_user_benefits"
        verbose_name = "用户福利表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)


def default_redeem_code():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

def default_expire_at():
    return timezone.now() + datetime.timedelta(minutes=60*12)

class UserRedeem(models.Model):
    
    VERIFIED_STATUS_CHOICES = (
        (0, _('未验证')),
        (1, _('已验证')),
    )

    id = models.AutoField(primary_key=True)
    redeem_code = models.CharField(max_length=32, default=default_redeem_code, verbose_name="兑换卡密", null=True, blank=True, help_text="兑换卡密")
    baseUserId = models.IntegerField(verbose_name="用户ID", null=True, blank=True, help_text="用户ID")
    redeem_tokens = models.IntegerField(default=200000, verbose_name="兑换赠送tokens", null=True, blank=True, help_text="兑换赠送tokens")
    redeem_dalle = models.IntegerField(default=10, verbose_name="兑换赠送dalle", null=True, blank=True, help_text="兑换赠送dall-e-2,3")
    verified = models.IntegerField(verbose_name="是否验证", choices=VERIFIED_STATUS_CHOICES, default=0, help_text="是否验证 0 未验证 1 已验证")
    expire_at = models.DateTimeField(verbose_name="兑换卡密过期时间", default=default_expire_at, null=True, blank=True, help_text="兑换卡密过期时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="签到时间", verbose_name="创建时间")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")

    class Meta:
        db_table = "front_user_redeem"
        verbose_name = "用户卡密兑换表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
    