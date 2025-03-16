from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, F, Q, Subquery, Max
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from webshadeApp.models import userDetail , whatsappConnection, withdrawal_request, bank_account,ChromeInstance
from webshadeAdmin.models import reward_price,RequestHandlingAdmin
from webshadeApp.functions import send_telegram_message, new_user_register_message,send_task_to_admin
from webshadeApp.functions import is_number, validate_email
from django.utils import timezone
from webshadeApp.task import get_verification_code,test_task
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult
from django.utils.timezone import now, localtime
from datetime import timedelta
from django.core.cache import cache
import traceback
import json
import os
import uuid
cache.clear()
today_date = localtime().strftime("%d-%m-%Y")
current_time = now()

def login_account(request):
    data = json.loads(request.body)
    phone = data.get('phone')
    password = data.get('password')
    if userDetail.objects.filter(phone=phone).exists():
        user_data = userDetail.objects.get(phone=phone)
        user = authenticate(username=user_data.user_id, password=password)
        if user is not None:
            login(request,user)
            error =  False
            message = "You have logged in successfully ! !"
            return JsonResponse({'message':message,'error':error})
        else:
            error =  True
            message = "Your entered password is incorrect !"
            return JsonResponse({'message':message,'error':error})
    else:
        error =  True
        message = "Your entered Mobile number doesn't exists !"
        return JsonResponse({'message':message,'error':error})

def register_account(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone = data.get('phone')
        email = data.get('email')
        password = data.get('password')  # Hashing the password
        refferal = data.get('refferal')
        print(phone)
        if is_number(phone) == False:
            return JsonResponse({'message':"Your entered phone number is not valid !",'error':True})
        elif userDetail.objects.filter(phone=phone).first():
            return JsonResponse({'message':"Your entered phone number is already exists !",'error':True})
        elif validate_email(email) == False:
            return JsonResponse({'message':"Your entered email address is not valid !",'error':True})
        elif userDetail.objects.filter(email=email).first():
            return JsonResponse({'message':"Your entered email address is already exists !",'error':True})
        elif len(password) < 8:
            return JsonResponse({'message':"Your password was too small or not secure !",'error':True})
        else:
            while True:
                user_id = str(uuid.uuid4().int)[:7]# Next number with leading zeros
                if not userDetail.objects.filter(user_id=user_id).exists():
                     break
                    
            info = userDetail(phone=phone,email=email,password=password,refer_by=refferal,user_id=user_id)
            userid, created = User.objects.get_or_create(username=user_id)
            userid.set_password(password)
            userid.save()
            info.save()
            new_user_register_message(f"🚀 New User Registered!\nUser ID : {user_id}\nPhone : {phone}\nEmail : {email}\n")
            user = authenticate(username=user_id, password=password)
            login(request, user)
            return JsonResponse({'message':'Your account was created successfully !','error':False})
    else:
        return JsonResponse({'message':'Error while creating your account!','error':True})
 
def send_code_request(request):
    try:
        whatsapp = request.GET.get('whatsapp')
        server_data = reward_price.objects.all().first()
        user_id = str(request.user)

        # Server Status Validation
        if server_data.server_status == False:
            if not request.user.is_superuser:
                return JsonResponse({'message': "Server Down", 'error': True})

        # Phone whatsapp Validation
        if not whatsapp:
            return JsonResponse({'message': "Phone number cannot be empty.", 'error': True})
        elif len(whatsapp) != 10:
            return JsonResponse({'message': "Phone number should be 10 digits long.", 'error': True})
        elif not whatsapp.isdigit():
            return JsonResponse({'message': "Phone number should only contain digits.", 'error': True})
        # Whatsapp Connection Validation
        elif whatsappConnection.objects.filter(whatsapp=whatsapp, status='Online').exists():
            return JsonResponse({'message': "Phone number is already connected to webshade.", 'error': True})
        else:
            connect_id = str(uuid.uuid4().int)[:7]
            while whatsappConnection.objects.filter(connect_id=connect_id).exists():
                connect_id = str(uuid.uuid4().int)[:7]

            whatsapp_connect_data = whatsappConnection.objects.filter(whatsapp=whatsapp,user_id=request.user)

            # Geting a free admin ID
            free_admin = RegestHandlingAdmin.objects.annotate(
                task_count=Count('whatsappconnection', filter=Q(whatsappconnection__status="Processing"))
            ).filter(task_count__lte=2).exclude(admin_id="Bot").order_by('task_count').first()

            # Identify the delay time
            previous_task = whatsappConnection.objects.filter(admin_id='Bot').last()
            delay_time = 0
            if previous_task:
                time_diff = (now() - previous_task.created_at).total_seconds()
                if time_diff < 50:  # 10 sec se kam hai to delay add karenge
                    delay_time = 50 - time_diff

            # Sending task to handler Bot or Agent
            if delay_time > 0:
                send_task_to_admin(free_admin.chat_id)
                created_at = now()
                admin_id = free_admin.admin_id
                handlingBy = free_admin.name
                task_id = False
            else:
                result = get_verification_code.delay(whatsapp, connect_id, user_id)
                admin_id = 'Bot'
                created_at = now() + timedelta(seconds=delay_time)
                handlingBy = 'Bot'
                task_id = result.id

            if whatsapp_connect_data.exists():
                whatsapp_connect_data.update(status='Processing', created_at=created_at, code='')
                connect_id = whatsapp_connect_data.first().connect_id
            else:
                whatsappConnection.objects.create(
                    whatsapp=whatsapp, user_id=user_id, connect_id=connect_id, 
                    created_at=created_at,
                )
            send_telegram_message(
                f"🚀 New Connect Request Recieved by {handlingBy}!\n\n"
                f"👤 User: {user_id}\n"
                f"Phone Number: {whatsapp}\n"
                f"Request ID: {connect_id}\n",
                connect_id, whatsapp
            )
            return JsonResponse({'message': "Code request sent successfully.", 'error': False,'connect_id':connect_id,'task_id':task_id})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message': 'Error while sending request', 'error': True})

@csrf_exempt
def check_code_request(request):
    try:
        data = json.loads(request.body)
        connect_id = data.get('connect_id')
        connect_data = whatsappConnection.objects.filter(connect_id=connect_id).first()

        if connect_data and connect_data.code == 'Error':
            return JsonResponse({'message': connect_data.status, 'error': True,})
        elif connect_data and connect_data.code != '':
            return JsonResponse({'message': "Your whatsapp code was received.", 'error': False,'code':connect_data.code})
        else:
            return JsonResponse({'message': "Waiting for verification.", 'error': False,'code':'','connect_id':connect_id})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message': "Error while checking code request.", 'error': True})

@csrf_exempt
def check_code_acceptence(request):
    try:
        data = json.loads(request.body)
        connect_id = data.get('connect_id')
        connect_data = whatsappConnection.objects.get(connect_id=connect_id)
        if connect_data.code == 'Error':
            return JsonResponse({'message': connect_data.status, 'error': True,'acceptence':False})
        elif connect_data.status == 'Online':
            return JsonResponse({'message': "Congrats, Your whatsapp is now online.", 'error': False,'acceptence':True})
        elif connect_data.status == 'Rejected':
            return JsonResponse({'message': "The whatsapp is already connected by other.", 'error': True,'acceptence':False})
        elif connect_data.status == 'Offline' or connect_data.status == 'Processing':
            return JsonResponse({'message': "Waiting for Acceptence.", 'error': False,'acceptence':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message': "Error while checking code request.", 'error': True})

def withdrawal(request):
    try:
        data = json.loads(request.body)
        amount = data.get('amount')
        user_data = userDetail.objects.get(user_id=request.user)
        account_data = bank_account.objects.filter(user_id=request.user).first()
        if int(amount) > int(user_data.balance):
            return JsonResponse({'error':True,'message':'Insufficient balance'})
        elif account_data == None:
            return JsonResponse({'error':True,'message':'Please add bank account first'})
        else:
            while True:
                with_id = str(uuid.uuid4().int)[:7]  # Next number with leading zeros
                if not withdrawal_request.objects.filter(with_id=with_id).exists():
                     break

            info = withdrawal_request(with_id=with_id,user_id=user_data.user_id,amount=amount,date=today_date,holder_name=account_data.holder_name,account=account_data.account_number,ifsc=account_data.ifsc_code)
            user_data.balance = int(user_data.balance) - (int(amount)+((int(amount)/100)*10))
            user_data.save()
            info.save()
            return JsonResponse({'error':False,'message':"Withdrawal request submitted successfully !",'balance':user_data.balance})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error':True,'message':"Something went wrong"})

def add_bank_account(request):
    try:
        data = json.loads(request.body)
        holder_name = data.get('holder_name')
        account_number = data.get('account_number')
        ifsc_code = data.get('ifsc_code')
        if bank_account.objects.filter(user_id=request.user).exists():
            bank_data = bank_account.objects.get(user_id=request.user)
            bank_data.holder_name = holder_name
            bank_data.ifsc_code = ifsc_code
            bank_data.account_number = account_number
            bank_data.save()
        else:
            info = bank_account(user_id=request.user,holder_name=holder_name,account_number=account_number,ifsc_code=ifsc_code)
            info.save()
        return JsonResponse({'error':False,'message':'Bank account added successfully'})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error':True,'message':"Error while adding bank account"})

@csrf_exempt
def send_code_in_backend(request):
    try:
        connect_id = request.GET.get("connect-id")
        code = request.GET.get("code")
        print(f'This is the code:{code}')
        connection_data = whatsappConnection.objects.get(connect_id=connect_id)
        connection_data.code = code
        connection_data.save()
        return JsonResponse({'status':True,'error':False})
    except Exception as e:
        e = traceback.print_exc()
        return JsonResponse({'status':False,'error':True,'e':e})

@csrf_exempt
def set_online_status(request):
    try:
        connect_id = request.GET.get("connect-id")
        code = request.GET.get("code")
        connection_data = whatsappConnection.objects.filter(connect_id=connect_id).update(
        status='Online', 
        date=today_date, 
        successTimestamp=now()  # ✅ Properly closed parenthesis
        )
        return JsonResponse({'status':True,'error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status':False,'error':True})

@csrf_exempt
def update_error(request):
    try:
        connect_id = request.GET.get("connect-id")
        error = request.GET.get("error")
        pid = request.GET.get("pid")
        print(error)
        connection_data = whatsappConnection.objects.filter(connect_id=connect_id).update(
        status=error,
        code='Error'
        )
        os.system(f"kill {pid}")  # Kill Chrome process
        return JsonResponse({'status':True,'error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status':False,'error':True})

@csrf_exempt
def cancel_task(request):
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        user_id = data.get('user_id')
        task = AsyncResult(task_id)
        task.revoke(terminate=True, signal='SIGKILL')
        chrome_instance = ChromeInstance.objects.filter(user_id=user_id)
        for instance in chrome_instance:
            os.system(f"kill {instance.pid}")  # Kill Chrome process
            instance.delete()  # Delete from database
        return JsonResponse({'status':True,'error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status':False,'error':True})
@csrf_exempt
def join_give_telegram_reward(request):
    try:
        user_data = userDetail.objects.get(user_id=request.user)
        if user_data.telegram_reward == False:
            get_reward = True
            user_data.telegram_reward = True
            user_data.balance += 10
            user_data.save()
        return JsonResponse({'error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error':True})
@csrf_exempt
def join_give_telegram_group_reward(request):
    try:
        user_data = userDetail.objects.get(user_id=request.user)
        if user_data.telegram_group_reward == False:
            user_data.telegram_group_reward = True
            user_data.balance += 5
            user_data.save()
        return JsonResponse({'error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error':True})