#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : urls.py
Description      : 
Time             : 2024/04/09 21:37:01
Author           : AllenLuo
Version          : 1.0
'''

from django.urls import path
from chatgpt_audio.views import Audio

urlpatterns = [
    path("transcriptions", Audio.as_view({"post": "create"})),
    path("speech", Audio.as_view({"post": "speech"})),

]
