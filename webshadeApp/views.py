from django.shortcuts import render,redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from webshadeApp.models import userDetail,withdrawal_request,bank_account, whatsappConnection
from webshadeAdmin.models import reward_price 
from webshadeApp.functions import is_number
from django.core.cache import cache
import json
import time
from django.utils.timezone import localtime
import traceback
cache.clear()
today_date = localtime().strftime("%d-%m-%Y")
# Create your views here.
def register_account(request,refer_code=''):
      return render(request,'webshadeApp/register.html',{'refer_code':refer_code})

def login_account(request):
      phone_not_exists_error = False
      if request.method == 'POST':
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            user = authenticate(username=phone, password=password)
            if user is not None:
                  login(request,user)
                  return redirect('/')
            else:
                  context = {
                        'phone_not_exists_error':True
                  }
                  return render(request,'webshadeApp/login.html',context)
      return render(request,'webshadeApp/login.html',{'phone_not_exists_error':phone_not_exists_error})

@never_cache
def connect(request):
      if request.user.is_anonymous:
            return redirect('/login')
      server_status = reward_price.objects.all().first().server_status
      user_data = userDetail.objects.get(user_id=request.user)
      withdrawal_record = withdrawal_request.objects.filter(user_id=request.user)
      total_connection_earning = whatsappConnection.objects.filter(user_id=request.user).aggregate(Sum('commission'))['commission__sum'] or 0
      reward_data = reward_price.objects.all().first()
      if user_data.last_login != today_date:
            userDetail.objects.filter(user_id=request.user).update(last_login=today_date)
      amount_dict = {
            "amount_24": reward_data.amount_24,
            "amount_48": reward_data.amount_48,
            "amount_72": reward_data.amount_72,
            "amount_96": reward_data.amount_96,
            "amount_120": reward_data.amount_120,
            "amount_144": reward_data.amount_144,
            "amount_168": reward_data.amount_168,
        }
      context = {
            'user_data':user_data,
            'total_income':total_connection_earning,
            'server_status':server_status,
            'reward_data':reward_data,
            'total_reward':sum(amount_dict.values()),
            'amount_72_plus':sum(amount_dict.values())-(reward_data.amount_24+reward_data.amount_48)
      }
      return render(request,'webshadeApp/connect.html',context)

@never_cache
def invite(request):
      if request.user.is_anonymous:
            return redirect('/login')
      user_data = userDetail.objects.get(user_id=request.user)
      total_refer = userDetail.objects.filter(refer_by=user_data.user_id).count()
      context = {
            'user_data':user_data,
            'total_refer':total_refer,
      }
      return render(request,'webshadeApp/invite.html',context)

@never_cache
def profile(request):
      if request.user.is_anonymous:
            return redirect('/login')
      user_data = userDetail.objects.get(user_id=request.user)
      withdrawal_record = withdrawal_request.objects.filter(user_id=request.user)
      context = {
            'user_data':user_data,
            'processing_withdrawal_amount':withdrawal_record.filter(status='Processing').aggregate(Sum('amount'))['amount__sum'] or 0,
            'success_withdrawal_amount':withdrawal_record.filter(status='Success').aggregate(Sum('amount'))['amount__sum'] or  0,
      }
      return render(request,'webshadeApp/profile.html',context)
      
@never_cache
def withdrawal(request):
      if request.user.is_anonymous:
            return redirect('/login')
      bank_data = bank_account.objects.filter(user_id=request.user).exists()
      user_data = userDetail.objects.get(user_id=request.user)
      if bank_data == True:
            bank_data = bank_account.objects.get(user_id=request.user)
            pass
      context = {
            'bank_data':bank_data,
            'user_data':user_data,
      }
      return render(request,'webshadeApp/withdrawal.html',context)

@never_cache
def withdrawal_record(request):
      if request.user.is_anonymous:
            return redirect('/login')
      withdrawal_record = withdrawal_request.objects.filter(user_id=request.user).order_by('-id')
      context = {
            'withdrawal_record':withdrawal_record,
      }
      return render(request,'webshadeApp/withdrawal-record.html',context)
      
@never_cache
def dashboard(request):
      if request.user.is_anonymous:
            return redirect('/login')
      user_data = userDetail.objects.get(user_id=request.user)
      page_num = request.GET.get('page-number')
      total_referals_info = userDetail.objects.filter(refer_by=user_data.user_id).count()
      total_connections = whatsappConnection.objects.filter(user_id=request.user,status__in=['Online', 'Offline']).order_by('-id')
      total_online = whatsappConnection.objects.filter(user_id=request.user, status='Online').count()
      total_offline = whatsappConnection.objects.filter(user_id=request.user,status='Offline').count()
      total_commision = total_connections.aggregate(Sum('commission'))['commission__sum'] or 0

      context = {
            'user_data':user_data,
            'total_connections':total_connections,
            'total_connected':total_connections.count(), 
            'total_commision':total_commision,
            'total_online':total_online,
            'total_offline':total_offline,
            'total_referals_info':total_referals_info,
      }
      return render(request,'webshadeApp/dashboard.html',context)

def logout_account(request):
      logout(request)
      return redirect('/login')
   

