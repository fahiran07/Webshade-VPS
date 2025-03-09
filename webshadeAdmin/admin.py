from django.contrib import admin
from webshadeAdmin.models import reward_price,login_number

# Register your models here.
@admin.register(reward_price)
class reward_priceAdmin(admin.ModelAdmin):
    list_display = ('amount_24','amount_48','amount_72','server_status')

@admin.register(login_number)
class login_numberAdmin(admin.ModelAdmin):
    list_display = ('number','login_by','status')

