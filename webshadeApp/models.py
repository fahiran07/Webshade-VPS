from django.db import models
from django.utils import timezone

# Create your models here.
class userDetail(models.Model):
    user_id = models.CharField(blank=True,max_length=50)
    phone = models.CharField(max_length=50,blank=True)
    email = models.CharField(max_length=50,default='-')
    password = models.CharField(max_length=50,blank=True)
    balance = models.IntegerField(default=0)
    refer_by = models.CharField(blank=True,max_length=50)
    commision = models.IntegerField(default=0)
    active = models.BooleanField(default=False)

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
    time = models.TimeField(default=timezone.now)  # Set default value as current time
    onlineTime = models.IntegerField(default=0)
    commission = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='Processing')
    code = models.CharField(max_length=50,blank=True)
    remark = models.CharField(max_length=50,blank=True)
    successTimestamp = models.CharField(max_length=50, default='0')