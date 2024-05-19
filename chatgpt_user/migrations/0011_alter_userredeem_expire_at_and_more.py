# Generated by Django 4.2.4 on 2024-03-24 15:48

import chatgpt_user.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatgpt_user', '0010_alter_userredeem_redeem_dalle_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userredeem',
            name='expire_at',
            field=models.DateTimeField(blank=True, default=chatgpt_user.models.default_expire_at, help_text='兑换卡密过期时间', null=True, verbose_name='兑换卡密过期时间'),
        ),
        migrations.AlterField(
            model_name='userredeem',
            name='redeem_code',
            field=models.CharField(blank=True, default=chatgpt_user.models.default_redeem_code, help_text='兑换卡密', max_length=32, null=True, verbose_name='兑换卡密'),
        ),
    ]
