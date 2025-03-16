from django.db import models

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
    admin_id = models.CharField(max_length=50)
    active_task = models.IntegerField(default=0)