#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : exception.py
Description      : 
Time             : 2023/09/02 22:00:29
Author           : AllenLuo
Version          : 1.0
'''

from rest_framework.exceptions import PermissionDenied, AuthenticationFailed, NotAuthenticated, APIException
from utils.json_response import ErrorResponse
from loguru import logger
from rest_framework.views import set_rollback

def Custom_exception_handler(ex, context):
  """自定义异常处理
  """
  msg = ''
  code = 400

  if isinstance(ex, AuthenticationFailed):
      code = 401
      msg = '不正确的登录授权,请重新登录'

  elif isinstance(ex, NotAuthenticated):
      code = 401
      msg = '登录凭证不正确,请重新登录'

  elif isinstance(ex, PermissionDenied):
      code = 403
      msg = '额度已用完,请联系管理员,或点击签到领取额度'

  elif isinstance(ex, APIException):
      code = 400
      set_rollback()
      msg = ex.detail
      if isinstance(msg,dict):
          for k, v in msg.items():
              for i in v:
                  if i == "This field may not be blank.":
                    msg = "%s:%s" % (k, "不能为空")
                  elif i == "This field is required.":
                     msg = "%s:%s" % (k, "不能为空")
                  else:
                    msg = "%s:%s" % (k, i)

  elif isinstance(ex, BaseException):
      msg = str(ex)

  return ErrorResponse(msg=msg, code=code, status=code)

