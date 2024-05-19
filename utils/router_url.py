#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : router_url.py
Description      : 
Time             : 2023/09/12 19:56:08
Author           : AllenLuo
Version          : 1.0
'''

from rest_framework.routers import SimpleRouter
 
 
class StandardRouter(SimpleRouter):
    def __init__(self, trailing_slash=''):
        super(StandardRouter, self).__init__()
        self.trailing_slash = trailing_slash