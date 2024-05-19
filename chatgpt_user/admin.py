from django.contrib import admin
from chatgpt_user.models import FrontUserBase, EmailVerifyCode, FrontUserExtraEmail
from chatgpt_user.models import CheckIn, UserBenefits, UserRedeem
# Register your models here.

class UserRedeemAdmin(admin.ModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('baseUserId', 'redeem_code', 'redeem_tokens', 'redeem_dalle', 'verified', 'expire_at', 'update_datetime',)

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    list_max_show_all = 200 #default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['baseUserId']


    '''默认空值'''
    empty_value_display = 'NA'
admin.site.register(UserRedeem, UserRedeemAdmin)

class UserBenefitsAdmin(admin.ModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('baseUserId', 'total_benefits_tokens', 'total_benefits_dalle', 'left_tokens', 'left_dalle', 'update_datetime',)

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    list_max_show_all = 200 #default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['baseUserId']


    '''默认空值'''
    empty_value_display = 'NA'


admin.site.register(UserBenefits, UserBenefitsAdmin)

class CheckInAdmin(admin.ModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('baseUserId', 'benefits_tokens', 'benefits_dalle', 'check_in_date', 'update_datetime',  )

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    list_max_show_all = 200 #default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['baseUserId']


    '''默认空值'''
    empty_value_display = 'NA'


admin.site.register(CheckIn, CheckInAdmin)

class FrontUserBaseAdmin(admin.ModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('id', 'username', 'nickname','VIP_TYPE', 'last_login_ip', 'vip_expire_at', 'call_count', 'update_datetime',)

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    list_max_show_all = 200 #default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['username']


    '''默认空值'''
    empty_value_display = 'NA'


class EmailVerifyCodeAdmin(admin.ModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('to_email_address', 'verify_code', 'verify_ip', 'expire_at', 'biz_type', 'create_datetime', 'update_datetime',)

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    list_max_show_all = 200 #default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['to_email_address']


    '''默认空值'''
    empty_value_display = 'NA'


class FrontUserExtraEmailAdmin(admin.ModelAdmin):
    # 定制哪些字段需要展示
    list_display = ('username', 'verified', 'create_datetime', 'update_datetime',)

    '''分页：每页10条'''
    list_per_page = 10

    '''最大条目'''
    list_max_show_all = 200 #default

    '''搜索框 ^, =, @, None=icontains'''
    search_fields = ['username']

    '''默认空值'''
    empty_value_display = 'NA'

admin.site.register(FrontUserBase, FrontUserBaseAdmin)
admin.site.register(EmailVerifyCode, EmailVerifyCodeAdmin)
admin.site.register(FrontUserExtraEmail, FrontUserExtraEmailAdmin)