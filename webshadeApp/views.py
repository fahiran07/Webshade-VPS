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
import json
import time
import datetime
import traceback
today_date = datetime.date.today()
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

@login_required(login_url='/login')
def connect(request):
      server_status = reward_price.objects.all().first().server_status
      user_data = userDetail.objects.get(user_id=request.user)
      withdrawal_record = withdrawal_request.objects.filter(user_id=request.user)
      total_connection_earning = whatsappConnection.objects.filter(user_id=request.user).aggregate(Sum('commission'))['commission__sum'] or 0
      reward_data = reward_price.objects.all().first()
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

@login_required(login_url='/login')
@never_cache
def invite(request):
      user_data = userDetail.objects.get(user_id=request.user)
      total_refer = userDetail.objects.filter(refer_by=user_data.user_id).count()
      context = {
            'user_data':user_data,
            'total_refer':total_refer,
      }
      return render(request,'webshadeApp/invite.html',context)

@login_required(login_url='/login')
@never_cache
def profile(request):
      user_data = userDetail.objects.get(user_id=request.user)
      withdrawal_record = withdrawal_request.objects.filter(user_id=request.user)
      context = {
            'user_data':user_data,
            'processing_withdrawal_amount':withdrawal_record.filter(status='Processing').aggregate(Sum('amount'))['amount__sum'] or 0,
            'success_withdrawal_amount':withdrawal_record.filter(status='Success').aggregate(Sum('amount'))['amount__sum'] or  0,
      }
      return render(request,'webshadeApp/profile.html',context)
      
@login_required(login_url='/login')
@never_cache
def withdrawal(request):
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

@login_required(login_url='/login')
def withdrawal_record(request):
      withdrawal_record = withdrawal_request.objects.filter(user_id=request.user).order_by('-id')
      context = {
            'withdrawal_record':withdrawal_record,
      }
      return render(request,'webshadeApp/withdrawal-record.html',context)
      
@login_required(login_url='/login')
@never_cache
def dashboard(request):
      user_data = userDetail.objects.get(user_id=request.user)
      page_num = request.GET.get('page-number')
      total_referals_info = userDetail.objects.filter(refer_by=user_data.user_id).count()
      total_connections = whatsappConnection.objects.filter(user_id=request.user).exclude(status__in=['Processing', 'Rejected','try_again']).order_by('-id')
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
   

