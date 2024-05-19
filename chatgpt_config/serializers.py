#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : serializers.py
Description      : 
Time             : 2024/01/27 16:06:32
Author           : AllenLuo
Version          : 1.0
'''

from utils.serializers import CustomModelSerializer
from rest_framework import serializers
from chatgpt_config.models import Config, UserConfig


class Configserializer(CustomModelSerializer):
    """
    序列化器
    """
    key = serializers.CharField(required=False)
    value = serializers.CharField(required=False)

    class Meta:
        model = Config
        fields = "__all__"

class UserConfigserializer(CustomModelSerializer):
    """
    序列化器
    """

    class Meta:
        model = UserConfig
        fields = ('secretKey', 'proxyAdress', 'chatModel', 'drawvalue', 'chatModelList')

class ConfigEditserializer(CustomModelSerializer):
    """
    序列化器
    """
    secretKey = serializers.CharField(allow_blank=True)
    proxyAdress = serializers.CharField(allow_blank=True)
    baseUserId = serializers.CharField(required=True)
    chatModel = serializers.CharField(required=True)
    drawvalue = serializers.CharField(required=True)

    class Meta:
        model = UserConfig
        fields = "__all__"