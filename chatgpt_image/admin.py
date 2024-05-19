from django.contrib import admin
from chatgpt_image.models import ImageMessage
# Register your models here.

class ImageMessageAdmin(admin.ModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('baseUserId', 'uuid', 'prompt', 'size', 'number', 'res_data', 'create_datetime', 'update_datetime',)

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    list_max_show_all = 200 #default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['baseUserId']


    '''默认空值'''
    empty_value_display = 'NA'

admin.site.register(ImageMessage, ImageMessageAdmin)
