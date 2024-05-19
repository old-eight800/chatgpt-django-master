from django.contrib import admin
from chatgpt_config.models import Config, UserConfig
# Register your models here.

class ConfigAdmin(admin.ModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('config_Code', 'key', 'value', 'describtion',)

    '''分页：每页10条'''
    list_per_page = 50

    '''最大条目'''
    list_max_show_all = 200 #default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['config_Code', 'key']


    '''默认空值'''
    empty_value_display = 'NA'

class UserConfigAdmin(admin.ModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('baseUserId', 'secretKey', 'proxyAdress', 'chatModel', 'drawvalue', 'update_datetime',)

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    list_max_show_all = 200 #default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['baseUserId']


    '''默认空值'''
    empty_value_display = 'NA'

admin.site.register(Config, ConfigAdmin)

admin.site.register(UserConfig, UserConfigAdmin)
