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
from chatgpt_config.views import ConfigView, initialConfig

urlpatterns = [
    path("list", ConfigView.as_view({"get": "list"})),
    path("edit", ConfigView.as_view({"post": "edit"})),
    path("session", initialConfig.as_view({"get": "session"})),
]
