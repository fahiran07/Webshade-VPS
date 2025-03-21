from django.contrib import admin
from webshadeAdmin.models import reward_price,login_number,RequestHandlingAdmin,whatsappPayments, revenueRecord

# Register your models here.
@admin.register(reward_price)
class reward_priceAdmin(admin.ModelAdmin):
    list_display = ('amount_24','amount_48','amount_72','server_status')

@admin.register(login_number)
class login_numberAdmin(admin.ModelAdmin):
    list_display = ('number','login_by','status')


@admin.register(RequestHandlingAdmin)
class RequestHandlingAdminAdminAdmin(admin.ModelAdmin):
    list_display = ('admin_id','name','chat_id','phone','active','special_staff')


@admin.register(whatsappPayments)
class whatsappPaymentsAdmin(admin.ModelAdmin):
    list_display = ('release_id','amount','releaser','date','time')

@admin.register(revenueRecord)
class revenueRecordAdmin(admin.ModelAdmin):
    list_display = ('revenue_id','admin_id','admin_name','last_balance','withdrawal_amount','date')

