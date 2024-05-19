#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : views.py
Description      : 
Time             : 2024/04/09 21:37:38
Author           : AllenLuo
Version          : 1.0
'''


from rest_framework import permissions
from utils.json_response import ErrorResponse, DetailResponse
from utils.permisson import LimitedAccessPermission
from rest_framework.viewsets import ModelViewSet
from django_restql.mixins import QueryArgumentsMixin
from openai import OpenAI
from loguru import logger
from chatgpt_config.models import Config
import openai
from chatgpt_bootstrap.settings import BASE_DIR
import os
import time
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from chatgpt_user.models import UserBenefits
from rest_framework.response import Response
import os

class Audio(ModelViewSet,QueryArgumentsMixin):
  permission_classes = [permissions.IsAuthenticated, LimitedAccessPermission] # 登录授权才可以访问接口

  def create(self, request):
    openai_api_config = Config.objects.filter(key__contains="OPENAI_API")
    openai_api_config_dict = dict(openai_api_config.values_list('key', 'value'))
    client = OpenAI(
      api_key = openai_api_config_dict.get("OPENAI_API_KEY", 'None'),
      base_url = openai_api_config_dict.get("OPENAI_API_BASE_URL", 'None')
    )
    audio_file = request.FILES['file']
    baseUserId = request.user.id
    audio_file_path = os.path.join(BASE_DIR, 'static', 'AudioFiles', f'{baseUserId}-{int(time.time())}.mp3')
    logger.info(audio_file_path)
    with open(audio_file_path,'wb+') as f:
          for chunk in audio_file.chunks():
              f.write(chunk)
    audio_file = open(audio_file_path, "rb")
    transcript = client.audio.transcriptions.create(
      model="whisper-1",
      file=audio_file
    )
    logger.info(transcript.text)
    return Response(data={"text": transcript.text})

  def speech(self, request):
    openai_api_config = Config.objects.filter(key__contains="OPENAI_API")
    openai_api_config_dict = dict(openai_api_config.values_list('key', 'value'))
    client = OpenAI(
      api_key = openai_api_config_dict.get("OPENAI_API_KEY", 'None'),
      base_url = openai_api_config_dict.get("OPENAI_API_BASE_URL", 'None')
    )
    baseUserId = request.user.id
    speech_file_path = os.path.join(BASE_DIR, 'static', 'AudioFiles', f'{baseUserId}-{int(time.time())}.mp3')

    response = client.audio.speech.create(
      model = request.data['model'],
      voice = request.data['voice'],
      input = request.data['input'],
    )
    response.write_to_file(speech_file_path)
    
    wrapper = FileWrapper(open(speech_file_path, 'rb'))
    response = HttpResponse(wrapper, content_type='audio/mpeg')
    response['Content-Length'] = os.path.getsize(speech_file_path)
    return response
