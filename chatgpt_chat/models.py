from django.db import models

# Create your models here.


class ChatMessage(models.Model):
    

    id = models.AutoField(primary_key=True)
    baseUserId = models.IntegerField(verbose_name="用户ID", null=True, blank=True, help_text="用户ID")
    messages = models.TextField(verbose_name="提示语", null=True, blank=True, help_text="提示语")
    completion = models.TextField(verbose_name="回复词", null=True, blank=True, help_text="回复词")
    completion_message = models.TextField(verbose_name="详细回复词", null=True, blank=True, help_text="详细回复词")
    chat_model = models.CharField(max_length=32, verbose_name="会话模型", null=True, blank=True, help_text="会话模型")
    prompt_tokens = models.IntegerField(verbose_name="提示语消耗tokens",null=True, blank=True, help_text="提示语消耗tokens")
    total_tokens = models.IntegerField(verbose_name="总共消耗tokens",null=True, blank=True, help_text="总共消耗tokens")
    completion_tokens = models.IntegerField(verbose_name="回复词消耗tokens", blank=True, null=True, help_text="回复词消耗tokens")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间", verbose_name="修改时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间", verbose_name="创建时间")
    created = models.DateField(auto_now_add=True, null=True, blank=True, help_text="创建日期", verbose_name="创建日期")

    class Meta:
        db_table = "chat_message"
        verbose_name = "聊天消息表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)