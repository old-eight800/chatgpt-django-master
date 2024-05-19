#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : urls.py
Description      : 
Time             : 2024/01/27 16:21:34
Author           : AllenLuo
Version          : 1.0
'''


from django.urls import path
from chatgpt_usage.views import Usage

urlpatterns = [
    path("list", Usage.as_view({"get": "list"})),
    path("userUsage", Usage.as_view({"get": "userUsage"})),
]
