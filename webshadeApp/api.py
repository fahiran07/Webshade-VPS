from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum, F, Q, Subquery, Max
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from webshadeApp.models import userDetail , whatsappConnection, withdrawal_request, bank_account
from webshadeAdmin.models import reward_price
from webshadeApp.functions import send_telegram_message, new_user_register_message
from webshadeApp.functions import is_number, validate_email
from django.utils import timezone
import traceback
import json
import datetime
import uuid
today_date = datetime.date.today()

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
        data = json.loads(request.body)
        phone = data.get('phone')
        user_data = userDetail.objects.get(user_id=request.user)
        server_data = reward_price.objects.all().first()

        # Server Status Validation
        if server_data.server_status == False:
            return JsonResponse({'message': "Server Down", 'error': True})

        # Phone Number Validation
        if not phone:
            return JsonResponse({'message': "Phone number cannot be empty.", 'error': True})
        elif len(phone) != 10:
            return JsonResponse({'message': "Phone number should be 10 digits long.", 'error': True})
        elif not phone.isdigit():
            return JsonResponse({'message': "Phone number should only contain digits.", 'error': True})
        # Whatsapp Connection Validation
        elif whatsappConnection.objects.filter(whatsapp=phone, status='Online').exists():
            return JsonResponse({'message': "Phone number is already connected to webshade.", 'error': True})
        else:
            while True:
                connect_id = str(uuid.uuid4().int)[:7] # Next number with leading zeros
                if not whatsappConnection.objects.filter(connect_id=connect_id).exists():
                     break
            
            whatsapp_connect_data = whatsappConnection.objects.filter(whatsapp=phone,user_id=request.user,onlineTime=0)
            if whatsapp_connect_data.exists():
                connect_id = whatsapp_connect_data.first().connect_id
                if whatsapp_connect_data.first().status == 'try_again':
                    remark = 'Other'
                else:
                    remark = 'ET7India'
                whatsapp_connect_data.update(status='Processing',time=datetime.datetime.now(),code='',remark=remark)

            else:
                info = whatsappConnection(whatsapp=phone, user_id=user_data.user_id, connect_id=connect_id, date=today_date, time=datetime.datetime.now(),remark='Goshare')
                info.save()
                remark = 'ET7India'
            send_telegram_message(
                f"🚀 New Connect Request!\n\n"
                f"👤 User: {request.user}\n"
                f"Phone Number: {phone}\n"
                f"Request ID: {connect_id}\n"
                f"Connect With : {remark}\n",
                connect_id,phone
            )
            return JsonResponse({'message': "Code request sent successfully.", 'error': False,'connect_id':connect_id})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message': "Error while sending code request.", 'error': True})
    
def check_code_request(request):
    try:
        data = json.loads(request.body)
        connect_id = data.get('connect_id')
        connect_data = whatsappConnection.objects.filter(connect_id=connect_id).exclude(code="").first()
        if connect_data and connect_data.status == 'Rejected':
            return JsonResponse({'message': "The whatsapp is already connected by other.", 'error': True,'code':'Rejected'})
        elif connect_data:
            return JsonResponse({'message': "Your whatsapp code was received.", 'error': False,'code':connect_data.code})
        else:
            return JsonResponse({'message': "The whatsapp was already connected.", 'error': False,'code':''})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message': "Error while checking code request.", 'error': True})
    
def check_code_acceptence(request):
    try:
        data = json.loads(request.body)
        connect_id = data.get('connect_id')
        connect_data = whatsappConnection.objects.get(connect_id=connect_id)
        if connect_data.status == 'try_again':
            return JsonResponse({'message': "Please try again.", 'error': True,'acceptence':False})
        elif connect_data.status == 'Online':
            return JsonResponse({'message': "Congrats, Your whatsapp is now online.", 'error': False,'acceptence':True})
        elif connect_data.status == 'Rejected':
            return JsonResponse({'message': "The whatsapp is already connected by other.", 'error': True,'acceptence':False})
        elif connect_data.status == 'Offline' or connect_data.status == 'Processing':
            return JsonResponse({'message': "Your whatsapp is not online.", 'error': False,'acceptence':False})
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

 
 
        