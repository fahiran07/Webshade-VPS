from django.db import models
from webshadeAdmin.functions import get_date_string, get_time_string


# Create your models here.

class reward_price(models.Model):
    amount_24 = models.IntegerField(default=50)
    amount_48 = models.IntegerField(default=30)
    amount_72 = models.IntegerField(default=20)
    amount_96 = models.IntegerField(default=10)
    amount_120 = models.IntegerField(default=10)
    amount_144 = models.IntegerField(default=10)
    amount_168 = models.IntegerField(default=10)
    server_status = models.BooleanField(default=False)

class login_number(models.Model):
    number = models.CharField(max_length=50)
    login_by = models.CharField(max_length=50,default='',blank=True)
    status = models.CharField(default='no login',max_length=50)

class RequestHandlingAdmin(models.Model):
    name = models.CharField(max_length=50)
    chat_id = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    workon = models.CharField(max_length=50)
    admin_id = models.CharField(max_length=50)
    active = models.BooleanField(default=False)
    special_staff = models.BooleanField(default=False)
    def __str__(self):
        return str(self.admin_id)

class whatsappPayments(models.Model):
    release_id = models.CharField(max_length=50)
    amount = models.IntegerField(default=0)
    releaser = models.CharField(max_length=50)
    date = models.CharField(max_length=50, default=get_date_string)
    time = models.CharField(max_length=50, default=get_time_string)

class revenueRecord(models.Model):
    record_id = models.CharField(max_length=50, blank=True)
    revenue_id = models.CharField(max_length=50)
    admin_id = models.CharField(max_length=50)
    admin_name = models.CharField(max_length=50)
    last_balance = models.IntegerField(default=0)
    withdrawal_amount = models.IntegerField(default=0)
    date = models.CharField(max_length=50, default=get_date_string)