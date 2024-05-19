#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : task.py
Description      : 
Time             : 2023/09/22 12:56:03
Author           : AllenLuo
Version          : 1.0
'''
# from celery import shared_task
from django.conf import settings
import requests
from chatgpt_image.models import ImageMessage
from chatgpt_image.serializers import UpdateImageMessageSend
from django.http import Http404
from django.conf import settings


superbed_token = settings.SUPERBED_TOKEN

def get_object(uuid):
    try:
        return ImageMessage.objects.get(uuid=uuid)
    except ImageMessage.DoesNotExist:
        raise Http404

# @shared_task
# def put_openai_image_to_superbed(uuid, url_list):
#     image_uplod_url = settings.SUPERBED_URL
#     resp = {}
#     # openai的原始图片上传到图床
#     for openai_res_image_url in url_list:
#       res = requests.post(url = image_uplod_url, data={"token": superbed_token, "src": openai_res_image_url})
#       resp.update(res.json())
#     logger.debug(resp)   
    
#     serializer = UpdateImageMessageSend(
#         instance=get_object(uuid), data={"res_data": resp})
#     serializer.is_valid(raise_exception=True)
#     serializer.update(instance=get_object(uuid),
#                       validated_data={"res_data": resp})
