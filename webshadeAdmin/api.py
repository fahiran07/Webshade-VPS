from django.shortcuts import render, redirect
from django.db.models import Sum, F, Q, Subquery, Max
from django.db.models import Func, Value as V
from django.db.models.functions import Substr
from django.contrib.auth.models import User
from webshadeApp.models import userDetail, whatsappConnection, withdrawal_request
from webshadeAdmin.models import reward_price
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import random
import traceback
import json
import uuid

today_date = datetime.now().date().strftime("%d-%m-%Y")
current_time = datetime.now()


def login_account(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        admin = authenticate(username=username, password=password)
        if admin is not None and admin.is_superuser:
            admin = User.objects.get(username=username)
            login(request, admin)
            return JsonResponse(
                {"message": "Admin account logged succcessfully", "error": False}
            )
        else:
            return JsonResponse(
                {"message": "Invalid username or password !", "error": True}
            )
    except Exception as e:
        traceback.print_exc()
        return JsonResponse(
            {"message": "Error while logging your account !", "error": True}
        )

def get_user_data(request):
    try:
        data = json.loads(request.body)
        search_term = data.get("search_term")

        # Query the PlatformUser  model to retrieve users matching the search term
        found_result = (
            userDetail.objects.filter(
                Q(user_id=search_term) | Q(phone=search_term) | Q(email=search_term)
            )
            .values()
            .first()
        )
        if found_result:
            return JsonResponse(
                {
                    "result": found_result,
                    "message": "User found successfully",
                    "error": False,
                }
            )
        else:
            return JsonResponse({"message": "User was not found !", "error": True})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse(
            {"message": "Error while retrieving user data!", "error": True}
        )

def update_user_status(request):
    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        active_status = data.get("active")
        user = userDetail.objects.get(user_id=user_id)
        user.active = active_status
        print(user.active)
        user.save()
        return JsonResponse({"error": False})
    except userDetail.DoesNotExist:
        return JsonResponse({"error": True, "message": "User not found"})
    except Exception as e:
        return JsonResponse({"error": True, "message": str(e)})

def send_code(request):
    try:
        data = json.loads(request.body)
        connect_id = data.get("connect_id")
        code = data.get("code")
        connection_data = whatsappConnection.objects.get(connect_id=connect_id) 
        connection_data.code = code
        connection_data.save()
        return JsonResponse({'message':'Code sent successfully','error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message':'Error while sending code','error':True})

def accept_request(request):
    try:
        data = json.loads(request.body)
        connect_id = data.get("connect_id")
        connection_data = whatsappConnection.objects.get(connect_id=connect_id)
        connection_data.status = 'Online'
        connection_data.date = today_date
        connection_data.time = current_time.strftime("%H:%M:%S")
        connection_data.successTimestamp = datetime.strptime("2025-03-05 14:30:00", "%Y-%m-%d %H:%M:%S")
        connection_data.save()
        return JsonResponse({'message':'Request accepted successfully','error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message':'Error while accepting request','error':True})

def reject_request(request):
    try:
        data = json.loads(request.body)
        connect_id = data.get("connect_id")
        connection_data = whatsappConnection.objects.get(connect_id=connect_id)
        if connection_data.status == 'Online' or connection_data.status == 'Offline':
            connection_data.status = 'Offline'
            connection_data.code = ''
        else:
            connection_data.status = 'Rejected'
            connection_data.code = 'Rejected'
        connection_data.save()
        return JsonResponse({'message':'Request rejected successfully','error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message':'Error while rejecting request','error':True})

def try_again_request(request):
    try:
        data = json.loads(request.body)
        connect_id = data.get("connect_id")
        connection_data = whatsappConnection.objects.get(connect_id=connect_id)
        connection_data.status = 'try_again'
        connection_data.code = ''
        connection_data.save()
        return JsonResponse({'message':'Request rejected successfully','error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message':'Error while rejecting request','error':True})

def increase_progress(request):
    try:
        data = json.loads(request.body)
        connect_id = data.get("connect_id")
        connection_data = whatsappConnection.objects.get(connect_id=connect_id)
        user_data = userDetail.objects.get(user_id=connection_data.user_id)
        rewards = reward_price.objects.filter().first()
        if connection_data.onlineTime >= 168:
            return JsonResponse({'error':True,'message':"This whatsapp got it's maximum reward"})
        # Instance ke values dictionary me daal raha hai
        connection_data.onlineTime += 24
        amount_dict = {
            "amount_24": rewards.amount_24,
            "amount_48": rewards.amount_48,
            "amount_72": rewards.amount_72,
            "amount_96": rewards.amount_96,
            "amount_120": rewards.amount_120,
            "amount_144": rewards.amount_144,
            "amount_168": rewards.amount_168,
        }
        
        reward_amount = int(amount_dict[f'amount_{connection_data.onlineTime}'])
        connection_data.commission += reward_amount
        userDetail.objects.filter(user_id=connection_data.user_id).update(balance=F('balance') + reward_amount)
        connection_data.save()
        # Giving commision to refer
        refer_by_user_data = userDetail.objects.filter(user_id=user_data.refer_by)
        if refer_by_user_data.first():
            refer_by_user_data.update(balance=F('balance') + (reward_amount*0.1),commision=F('commision') + (reward_amount*0.1))
        return JsonResponse({'error':False,'onlineTime':connection_data.onlineTime,'earn':connection_data.commission})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message':'Error while increasing progress','error':True})

def decrease_progress(request):
    try:
        data = json.loads(request.body)
        connect_id = data.get("connect_id")
        connection_data = whatsappConnection.objects.get(connect_id=connect_id)
        if connection_data.onlineTime <= 0:
            return JsonResponse({'error':True,'message':"This whatsapp doesn't got any reward"})
        user_data = userDetail.objects.get(user_id=connection_data.user_id)
        rewards = reward_price.objects.filter().first()
        # Instance ke values dictionary me daal raha hai
        connection_data.onlineTime -= 24
        amount_dict = {
            "amount_24": rewards.amount_24,
            "amount_48": rewards.amount_48,
            "amount_72": rewards.amount_72,
            "amount_96": rewards.amount_96,
            "amount_120": rewards.amount_120,
            "amount_144": rewards.amount_144,
            "amount_168": rewards.amount_168,
        }
        
        connection_data.commission -= amount_dict['amount_'+str(connection_data.onlineTime+24)]
        user_data = userDetail.objects.filter(user_id=connection_data.user_id).update(balance=F('balance') - amount_dict[f'amount_{connection_data.onlineTime+24}'])

        connection_data.save()
        return JsonResponse({'error':False,'onlineTime':connection_data.onlineTime,'earn':connection_data.commission})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message':'Error while decreasing progress','error':True})

def update_withdrawal_status(request):
    try:
        data = json.loads(request.body)
        withdrawal_status = data.get("status")
        with_id = data.get("with_id")
        withdrawal_data = withdrawal_request.objects.get(with_id=with_id)
        withdrawal_data.status = withdrawal_status
        withdrawal_data.save()
        return JsonResponse({'message':'Withdrawal status updated successfully','error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message':'Error while updating withdrawal status','error':True})

def update_server_status(request):
    try:
        data = json.loads(request.body)
        updating_status = data.get("updating_status")
        server_data = reward_price.objects.all().first()
        if updating_status == 'DOWN':
            server_data.server_status = False
        else:
            server_data.server_status = True
        server_data.save()
        return JsonResponse({'message':'Server status updated successfully','error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message':'Error while updating server status','error':True})

def search(request):
    data = json.loads(request.body)
    search_term = data.get('search_term')
    search_type = data.get('data_type')
    search_result = False
    if search_type == 'withdrawal':
        search_data =  withdrawal_request.objects.filter(with_id=search_term)
        if search_data.exists():
            search_result = list(search_data.values())

    elif search_type == 'whatsapp':
        search_data =  whatsappConnection.objects.filter(Q(connect_id=search_term) | Q(whatsapp=search_term))
        if search_data.exists():
            search_result = list(search_data.values())

    return JsonResponse({'search_result':search_result})
