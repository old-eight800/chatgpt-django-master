#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : views.py
Description      : 
Time             : 2023/08/28 09:40:20
Author           : AllenLuo
Version          : 1.0
'''
from utils.viewset import CustomModelViewSet
from chatgpt_image.serializers import ImageMessageSend, FileSerializer
from loguru import logger
from openai import OpenAI
from rest_framework import permissions
from utils.json_response import DetailResponse, ErrorResponse
from django.utils.translation import gettext_lazy as _
from utils.permisson import LimitedAccessPermission
from chatgpt_image.models import FileList, ImageMessage
import os
from chatgpt_bootstrap.settings import BASE_DIR
import uuid
# from chatgpt_image.tasks import put_openai_image_to_superbed
from chatgpt_config.models import Config
from rest_framework.response import Response

class Image(CustomModelViewSet):
    serializer_class = ImageMessageSend
    permission_classes = [permissions.IsAuthenticated, LimitedAccessPermission]


    def generate(self, request):
        """ 返回一个用于创建图片的uuid
        """
        openai_api_config = Config.objects.filter(key__contains="OPENAI_API")
        openai_api_config_dict = dict(openai_api_config.values_list('key', 'value'))
        client = OpenAI(
          api_key = openai_api_config_dict.get("OPENAI_API_KEY", 'None'),
          base_url = openai_api_config_dict.get("OPENAI_API_BASE_URL", 'None')
        )

        serializer = ImageMessageSend(data=request.data)
        logger.info(request.data)
        if serializer.is_valid(raise_exception=True):
            uuid_str = str(uuid.uuid4()).replace("-", "")
            req_data = serializer.validated_data
            serializer.save(number=req_data['number'], size=req_data['size'],
                            prompt=req_data['prompt'], baseUserId=request.user.id, 
                            uuid=uuid_str, imageQuality=req_data['imageQuality'])

        generation_response = client.images.generate(
            model=serializer.data['model'],
            prompt=serializer.data['prompt'],
            n=serializer.data['number'],
            size=serializer.data['size'],
            quality=serializer.data['imageQuality']
          )
        # validated_data = {'drawvalue': serializer.data['model']}
        # serializer.update(imagemessage, validated_data)
        # 将图片资源另存到在线图床
        # url_list = [url["url"] for url in  generation_response["data"] ]
        # put_openai_image_to_superbed.delay(uuid, url_list) 
        # res = UserBenefits.objects.filter(baseUserId=baseUserId).first() # 更新用户福利表
        # res.left_dalle -=1
        # res.save()

        # dt_object = datetime.datetime.fromtimestamp(
        #     generation_response['created'])
        # createTime = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        result = {
            "createTime": generation_response.created,
            "data": [
                      {"url": generation_response.data[0].url}
                    ]
        }
        logger.info(result)
        return Response(data=result)

    def images_list(self, request):
        imagemessage = ImageMessage.objects.filter(baseUserId=request.user.id)[:10]
        logger.debug(imagemessage)
        serializer = ImageMessageSend(imagemessage)
        return Response(serializer.data)

class FileViewSet(CustomModelViewSet):
    """
    文件管理接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = FileList.objects.all()
    serializer_class = FileSerializer
    filter_fields = ['name', ]
    permission_classes = []
