from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField
from loguru import logger
import json

class Config(models.Model):
        
    config_Code_CHOICES = (
        # 业务配置码枚举值
        ('openai_config', _('OpenAI配置项')),
        ('claude_config', _('Claude配置项')),
        ('email_config', _('邮箱服务器配置项')),
        ('customer_config', _('自定义配置项')),
    )
    id = models.AutoField(primary_key=True)
    config_Code = models.CharField(max_length=64, choices=config_Code_CHOICES, default=10, verbose_name="业务配置码", null=True, blank=True, help_text="业务配置码")
    key = models.CharField(max_length=64, verbose_name="配置键", null=True, blank=True, help_text="配置键")
    value = models.CharField(max_length=255, verbose_name="配置值", null=True, blank=True, help_text="配置值")
    describtion = models.CharField(max_length=255, verbose_name="描述", null=True, blank=True, help_text="描述")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间", verbose_name="创建时间")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")

    class Meta:
        db_table = "chatgpt_config"
        verbose_name = "业务配置表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

def get_chatModel_list():
    with open ('./default_config.json', 'r', encoding='utf-8') as default_config:
      return json.loads(default_config.read())

class UserConfig(models.Model):
    id = models.AutoField(primary_key=True)
    baseUserId = models.IntegerField(verbose_name="用户ID", null=True, blank=True, help_text="用户ID")
    secretKey = models.CharField(max_length=64, default='', verbose_name="配置键", null=True, blank=True, help_text="配置键")
    proxyAdress = models.CharField(max_length=255, default='', verbose_name="配置值", null=True, blank=True, help_text="配置值")
    chatModel = models.CharField(max_length=100, default='gpt-3.5-turbo', verbose_name="对话模型", help_text="对话模型")
    drawvalue = models.CharField(max_length=255, default='dall-e-2', verbose_name="绘画模型", null=True, blank=True, help_text="绘画模型")
    chatModelList = JSONField('权限列表', default=get_chatModel_list, help_text='"disabled": "fasle" 则为无权限')
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间", verbose_name="创建时间")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")

    class Meta:
        db_table = "user_config"
        verbose_name = "用户配置表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
