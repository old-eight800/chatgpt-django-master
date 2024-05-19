from django.shortcuts import render
from utils.viewset import CustomModelViewSet
from rest_framework import permissions
from chatgpt_config.serializers import Configserializer, ConfigEditserializer, UserConfigserializer
from chatgpt_config.models import UserConfig, Config
from utils.json_response import DetailResponse 
from loguru import logger

class ConfigView(CustomModelViewSet):
  serializer_class = Configserializer
  permission_classes = [permissions.IsAuthenticated]


  def list(self, request):
    baseUserId = request.user.id
    user_config = UserConfig.objects.filter(baseUserId=baseUserId).first()
    serializer = UserConfigserializer(user_config)
    return DetailResponse(data=serializer.data)
  
  def edit(self, request):
    serializer = ConfigEditserializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
      user_config = UserConfig.objects.filter(baseUserId=serializer.validated_data['baseUserId']).first()
      if user_config:
        validated_data = {
                          'secretKey': serializer.validated_data['secretKey'],
                          'proxyAdress': serializer.validated_data['proxyAdress'],
                          'baseUserId': serializer.validated_data['baseUserId'],
                          'chatModel': serializer.validated_data['chatModel'], 
                          'drawvalue': serializer.validated_data['drawvalue']
                          }
        serializer.update(user_config, validated_data)
      else:
        serializer.save(secretKey=serializer.validated_data['secretKey'],
                        proxyAdress=serializer.validated_data['proxyAdress'],
                        baseUserId=serializer.validated_data['baseUserId'], 
                        chatModel=serializer.validated_data['chatModel'], 
                        drawvalue=serializer.validated_data['drawvalue'])
      return DetailResponse()

class initialConfig(CustomModelViewSet):

  def session(self, request):
    demo_account1 = Config.objects.filter(key__contains="demo")
    demo_account_key = [i['key'] for i in demo_account1.values('key')]
    demo_account_value = [i['value'] for i in demo_account1.values('value')]
    demo_account_dict = dict(zip(demo_account_key, demo_account_value))
    if request.user.username == demo_account_dict['demo_account']:
      isShowDemo = 'true'
    else:
      isShowDemo = 'false'
    data = {
            "disableGpt4": "",
            "isWsrv": "",
            "isShowDemo": isShowDemo,
            "demoAccount": demo_account_dict['demo_account'],
            "demoPasswd": demo_account_dict['demo_passwd'],
            "uploadImgSize": "1",
            "theme": "light",
            "isCloseMdPreview": 'false',
            "uploadType": "",
            "notify": "",
            "baiduId": "",
            "googleId": "",
            "isHideServer": 'false',
            "isUpload": 'false',
            "auth": 'true',
            "model": "ChatGPTAPI",
            "amodel": "",
            "isApiGallery": 'false',
            "cmodels": "",
            "isUploadR2": 'false',
            "gptUrl": "",
            "turnstile": ""
          }
    return DetailResponse(data=data, msg="Success")
