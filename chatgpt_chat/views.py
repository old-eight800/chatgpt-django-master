#!usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
Filename         : views.py
Description      : 
Time             : 2023/08/15 22:15:23
Author           : AllenLuo
Version          : 1.0
'''

from django.http import StreamingHttpResponse
from chatgpt_chat.serializers import ChatMessageSerializers
import uuid
import json
import time
from loguru import logger
from openai import OpenAI
from rest_framework import permissions
from utils.json_response import ErrorResponse
from utils.permisson import LimitedAccessPermission
from chatgpt_config.models import Config
import json
from chatgpt_user.models import UserBenefits
from anthropic import Anthropic
from rest_framework.viewsets import ModelViewSet
from django_restql.mixins import QueryArgumentsMixin


class Chat(ModelViewSet, QueryArgumentsMixin):
    serializer_class = ChatMessageSerializers
    permission_classes = [permissions.IsAuthenticated, LimitedAccessPermission]  # 登录授权才可以访问接口


    def create(self, request):
        baseUserId = request.user.id
        logger.info(request.data)
        if request.data['model'] == '':
            request.data['model'] = 'gpt-3.5-turbo'
        chat_serializer = ChatMessageSerializers(data=request.data)
        if chat_serializer.is_valid(raise_exception=True):
            messages = chat_serializer.validated_data['messages']
            frequency_penalty = request.data['frequency_penalty']
            max_tokens = request.data['max_tokens']
            presence_penalty = request.data['presence_penalty']
            temperature = request.data['temperature']
            top_p = request.data['top_p']
            openai_model = request.data['model']

        if request.data['model'].startswith('gpt'):
            openai_api_config = Config.objects.filter(key__contains="OPENAI_API")
            openai_api_config_dict = dict(openai_api_config.values_list('key', 'value'))
            Draw_Chat_TTS_Model = Config.objects.filter(key="Draw_Chat_TTS_Model")
            Draw_Chat_TTS_Model_dict = dict(Draw_Chat_TTS_Model.values_list('key', 'value'))
            logger.info(Draw_Chat_TTS_Model_dict.get("Draw_Chat_TTS_Model", "gpt-4o"))
            client = OpenAI(
                api_key=openai_api_config_dict.get(
                    "OPENAI_API_KEY", 'None'),
                base_url=openai_api_config_dict.get(
                    "OPENAI_API_BASE_URL", 'None')
            )
            if openai_model == Draw_Chat_TTS_Model_dict.get("Draw_Chat_TTS_Model", "gpt-4o") and ( 'image_url' in messages[-1]['content']):
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text",
                             "text": messages[-1]['content'][0]['text']},
                            {
                            "type": "image_url",
                            "image_url": messages[-1]['content'][1]['image_url']['url'],
                            }
                        ]
                    }
                ]
            try:
                completion = client.chat.completions.create(
                    model=openai_model,
                    messages=messages,
                    frequency_penalty=frequency_penalty,
                    max_tokens=max_tokens,
                    presence_penalty=presence_penalty,
                    temperature=temperature,
                    top_p=top_p)
                logger.info(f"completion-{completion}")
                text = completion.choices[0].message.content
                prompt_tokens = completion.usage.prompt_tokens
                completion_tokens = completion.usage.completion_tokens
                total_tokens = completion.usage.total_tokens
                if openai_model.startswith('gpt-4'):
                    prompt_tokens = prompt_tokens * 20
                    completion_tokens = completion_tokens * 20
                    total_tokens = total_tokens * 20
                chat_serializer.save(messages=messages, baseUserId=baseUserId, completion=completion,
                                     completion_message=completion.choices[0].message, chat_model=openai_model,
                                     prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, total_tokens=total_tokens)
            except BaseException as e:
                msg = "请求失败,请稍后再试"
                logger.error(f'{msg}-后台返回-{e}')
                return ErrorResponse(code=500, data={}, msg=f'{e}')

        elif request.data['model'].startswith('claude'):
            # claude 处理逻辑
            claude_api_config = Config.objects.filter(key__contains="CLAUDE_API")
            claude_api_config_dict = dict(claude_api_config.values_list('key', 'value'))
            client = Anthropic(
                api_key=claude_api_config_dict.get(
                    "CLAUDE_API_KEY", 'None'),
                base_url=claude_api_config_dict.get(
                    "CLAUDE_API_BASE", 'None')
            )
            message = client.messages.create(
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": chat_serializer.validated_data['messages'][1]['content'],
                    }
                ],
                model=openai_model,
            )
            logger.info(message)
            text = message.content[0].text
            prompt_tokens = message.usage.input_tokens
            completion_tokens = message.usage.output_tokens
            total_tokens = int(prompt_tokens) + int(completion_tokens)
            prompt_tokens = prompt_tokens * 10
            completion_tokens = completion_tokens * 10
            total_tokens = total_tokens * 10
            chat_serializer.save(messages=messages, baseUserId=request.user.id, completion=message, chat_model=openai_model,
                                 prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, total_tokens=total_tokens)

        res = UserBenefits.objects.filter(
            baseUserId=request.user.id).first()  # 更新用户福利表
        res.left_tokens -= total_tokens
        if res.left_tokens < 0:
            res.left_tokens = 0
        res.save()

        def generate_streaming_text(text=text):
            # 流媒体文本处理方法
            id = str(uuid.uuid4())
            data = {"id": id, "object": "chat.completion.chunk", "created": 0, "model": openai_model, "choices": [
                {"delta": {"role": "assistant"}, "index": 0, "finish_reason": "null"}]}
            yield 'data: ' + f"{json.dumps(data, ensure_ascii=False)}\n\n"
            for i, char in enumerate(text):
                data = {
                    "id": id,
                    "object": "chat.completion.chunk",
                    "created": 0,
                    "model": openai_model,
                    "choices": [{"delta": {"content": text[i]}, "index":0, "finish_reason":"null"}],
                }
                yield 'data: ' + f"{json.dumps(data, ensure_ascii=False)}\n\n"
                time.sleep(0.02)
            data = {"id": id, "object": "chat.completion.chunk", "created": 0,
                    "model": openai_model, "choices": [{"delta": {}, "index": 0, "finish_reason": "stop"}]}
            yield 'data: ' + f"{json.dumps(data, ensure_ascii=False)}\n\n"
            yield 'data: [DONE]\n\n'
        response = StreamingHttpResponse(
            streaming_content=generate_streaming_text(), content_type='text/event-stream')
        return response
