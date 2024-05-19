#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : urls.py
Description      : 
Time             : 2023/08/27 19:09:48
Author           : AllenLuo
Version          : 1.0
'''


from django.urls import path
from chatgpt_image.views import Image, FileViewSet
from utils.router_url import StandardRouter

system_url = StandardRouter()
system_url.register(r'upload', FileViewSet)


urlpatterns = [
    path("list", Image.as_view({"get": "images_list"})),
    path("generations", Image.as_view({"post": "generate"})),
    path("edit", Image.as_view({"post": "edit"})),
    path("variation", Image.as_view({"post": "variation"})),
    path("detail/<slug:uuid>", Image.as_view({"get": "image_detail"})),

] + system_url.urls
