from django.contrib import admin
from webshadeApp.models import userDetail,withdrawal_request,bank_account, whatsappConnection

# Register your models here.
@admin.register(userDetail)
class userDetailAdmin(admin.ModelAdmin):
    list_display = ('phone','balance','email', 'password','user_id')

@admin.register(withdrawal_request)
class withdrawal_requestAdmin(admin.ModelAdmin):
    list_display = ('amount', 'user_id','account', 'date','status')

@admin.register(bank_account)
class bank_accountAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'holder_name','account_number','ifsc_code')

@admin.register(whatsappConnection)
class whatsappConnectionAdmin(admin.ModelAdmin):
    list_display = ('connect_id', 'user_id','whatsapp', 'date', 'time', 'onlineTime', 'code','status')