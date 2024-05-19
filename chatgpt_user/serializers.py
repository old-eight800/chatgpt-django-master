#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : serializers.py
Description      : 
Time             : 2023/08/06 20:52:03
Author           : AllenLuo
Version          : 1.0
'''


from chatgpt_user.models import FrontUserExtraEmail, FrontUserBase, EmailVerifyCode, CheckIn
from utils.serializers import CustomModelSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterDetailSerializer(CustomModelSerializer):
    """
    序列化器
    """
    identity = serializers.CharField()
    password = serializers.CharField()
    picCodeSessionId = serializers.CharField()
    picVerificationCode = serializers.CharField()
    registerType = serializers.CharField()

    class Meta:
        model = FrontUserExtraEmail
        fields = "__all__"


class RegisterDetailCreateUpdateSerializer(CustomModelSerializer):
    """
    创建/更新时的列化器
    """
    identity = serializers.CharField()
    password = serializers.CharField()
    picCodeSessionId = serializers.CharField()
    picVerificationCode = serializers.CharField()
    registerType = serializers.CharField()


    class Meta:
        model = FrontUserExtraEmail
        fields = "__all__"

class LoginSerializer(TokenObtainPairSerializer):
    """
    登录的序列化器:
    重写djangorestframework-simplejwt的序列化器
    """
    @classmethod
    def get_token(cls, user):
        token = super(LoginSerializer, cls).get_token(user)
        # 添加额外信息
        token['id'] = user.id
        return token
    
    class Meta:
        model = FrontUserBase
        fields = ["username", "password"]
        read_only_fields = ["id"]

class EmailVerifyCodeSerializer(CustomModelSerializer):
    """ 密码重置序列化器
    """
    to_email_address = serializers.CharField(required=True)

    class Meta:
        model = EmailVerifyCode
        fields = "__all__"


class CustomerTokenObtainPairSerializer(TokenObtainPairSerializer):

    class Meta:
        model = FrontUserExtraEmail
        fields = "__all__"


class UserInfoSerializer(CustomModelSerializer):


    class Meta:
        model = FrontUserBase
        fields = ("id", "username",  "nickname", "description", "avatar_version",)
      

class ResetPasswordSerializer(CustomModelSerializer):
    username = to_email_address = serializers.CharField(required=False)
    newPassword = password= serializers.CharField(required=False)
    emailVerficationCode = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = FrontUserBase
        fields = ("id", "username", "password", "newPassword", "to_email_address", "emailVerficationCode", )

class CheckInSerializer(CustomModelSerializer):
    baseUserId = serializers.IntegerField(required=False)
    check_in_date = serializers.DateField(required=False)

    class Meta:
        model = CheckIn
        fields = ("baseUserId", "check_in_date",)