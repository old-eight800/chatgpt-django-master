#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : serializers.py
Description      : 
Time             : 2023/08/14 16:49:52
Author           : AllenLuo
Version          : 1.0
'''

from rest_framework import serializers
from chatgpt_chat.models import ChatMessage


class ChatMessageSerializers(serializers.ModelSerializer):
    """
    序列化器
    """
    baseUserId = serializers.IntegerField(required=False)
    messages = serializers.ListField()
    completion = serializers.CharField(allow_blank=True, required=False)
    completion_message = serializers.CharField(allow_blank=True, required=False)
    prompt_tokens = serializers.IntegerField(required=False)
    total_tokens = serializers.IntegerField(required=False)
    completion_tokens = serializers.IntegerField(required=False)
    chat_model = serializers.CharField(allow_blank=True, required=False)
    # frequency_penalty=serializers.SerializerMethodField(required=False)
    # max_tokens=serializers.SerializerMethodField(required=False)
    # stream=serializers.SerializerMethodField(required=False)
    # temperature=serializers.SerializerMethodField(required=False)
    # top_p=serializers.SerializerMethodField(required=False)

    class Meta:
        model = ChatMessage
        fields = "__all__"