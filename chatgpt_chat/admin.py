from django.contrib import admin
from chatgpt_chat.models import ChatMessage
# Register your models here.

admin.site.site_header = 'chatgpt-django管理后台'  # 设置header
admin.site.site_title = 'chatgpt-django管理后台'   # 设置title
admin.site.index_title = 'chatgpt-django管理后台'

class ChatMessageAdmin(admin.ModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('baseUserId', 'messages', 'completion', 'prompt_tokens', 'completion_tokens', 'total_tokens', 'create_datetime',)

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    list_max_show_all = 200 #default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['baseUserId']


    '''默认空值'''
    empty_value_display = 'NA'

admin.site.register(ChatMessage, ChatMessageAdmin)

