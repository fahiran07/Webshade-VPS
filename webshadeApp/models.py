from django.db import models
from webshadeApp.functions import get_date_string,get_time_string
from webshadeAdmin.models import RequestHandlingAdmin
# Create your models here.
class userDetail(models.Model):
    user_id = models.CharField(blank=True,max_length=50)
    phone = models.CharField(max_length=50,blank=True)
    email = models.CharField(max_length=50,default='-')
    password = models.CharField(max_length=50,blank=True)
    balance = models.IntegerField(default=0)
    refer_by = models.CharField(blank=True,max_length=50)
    commision = models.IntegerField(default=0)
    last_login = models.CharField(blank=True,max_length=50)
    telegram_reward = models.BooleanField(default=False)
    telegram_group_reward = models.BooleanField(default=False)

class withdrawal_request(models.Model):
    user_id = models.CharField(max_length=50)
    with_id = models.CharField(max_length=50)
    amount = models.IntegerField(default=0)
    status = models.CharField(max_length=50,default='Processing')
    holder_name = models.CharField(max_length=50)
    account = models.CharField(max_length=50)
    ifsc = models.CharField(max_length=50)
    date = models.CharField(max_length=50)

class bank_account(models.Model):
    user_id = models.CharField(max_length=50)
    holder_name = models.CharField(max_length=50)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=50)

class whatsappConnection(models.Model):
    connect_id = models.CharField(max_length=50)
    user_id = models.CharField(max_length=50)
    whatsapp = models.CharField(max_length=50)
    date = models.CharField(max_length=50)
    time = models.CharField(max_length=50,default=get_time_string)  # Set default value as current time
    onlineTime = models.IntegerField(default=0)
    commission = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='Processing')
    code = models.CharField(max_length=50,blank=True)
    remark = models.CharField(max_length=50,blank=True)
    upper_admin = models.ForeignKey(RequestHandlingAdmin, on_delete=models.CASCADE, related_name='connections', blank=True, null=True)
    admin_id = models.CharField(max_length=50,blank=True)