#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : serializers.py
Description      : 
Time             : 2023/08/28 09:23:53
Author           : AllenLuo
Version          : 1.0
'''


from utils.serializers import CustomModelSerializer
from rest_framework import serializers
from chatgpt_image.models import ImageMessage, FileList
from django.utils.translation import gettext_lazy as _
from loguru import logger

class ImageMessageSend(CustomModelSerializer):
    """
    序列化器
    """
    uuid = serializers.CharField(required=False)
    number = serializers.IntegerField(default=1, max_value=10)
    size = serializers.CharField(default="512x512")
    prompt = serializers.CharField(
        default="A cyberpunk monkey hacker dreaming of a beautiful bunch of bananas, digital art")
    username = serializers.CharField(required=False)
    draw_model = model = serializers.CharField(default="dall-e-2")
    imageQuality = serializers.CharField(default="standard")

    class Meta:
        model = ImageMessage
        fields = "__all__"


class UpdateImageMessageSend(CustomModelSerializer):
    """
    序列化器
    """
    res_data = serializers.JSONField(required=True)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    
    class Meta:
        model = ImageMessage
        fields = "__all__"



class FileSerializer(CustomModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, instance):
        # 获取本地保存路径
        req_url = str(instance.url).replace('/template', '')
        return req_url

    class Meta:
        model = FileList
        fields = "__all__"

    def create(self, validated_data):
        validated_data['name'] = str(self.initial_data.get('file'))
        validated_data['url'] = self.initial_data.get('file')
        return super().create(validated_data)
