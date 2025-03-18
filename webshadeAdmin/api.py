from django.shortcuts import render, redirect
from django.db.models import Sum, F, Q, Subquery, Max
from django.db.models import Func, Value as V
from django.db.models.functions import Substr
from django.contrib.auth.models import User
from webshadeApp.models import userDetail, whatsappConnection, withdrawal_request
from webshadeAdmin.models import reward_price, RequestHandlingAdmin,whatsappPayments
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from webshadeAdmin.functions import get_date_string, get_time_string
from django.utils.timezone import now, localtime
import math
import random
import traceback
import json
import uuid
import os

today_date = localtime().date().strftime("%d-%m-%Y")

def admin_login(request):
    try:
        data = json.loads(request.body)
        admin_id = data.get("admin_id")
        if RequestHandlingAdmin.objects.filter(admin_id=admin_id).exists():
            return JsonResponse({"message": "Admin account logged succcessfully", "error": False})
        else:
            return JsonResponse({"message": "Invalid Admin ID, please try again !", "error": True})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"message": "Error while logging your account !", "error": True})

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

def superuser_login(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        if username and password:
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                return JsonResponse({'message':'Congrats, admin your account was logged in','error':False})
            else:
                return JsonResponse({'message':'Invalid username or password','error':True})
        return JsonResponse({'message':'Please enter valid username and password','error':True})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message':'Error while logging in admin account','error':True})
        
def send_code(request):
    try:
        data = json.loads(request.body)
        connect_id = data.get("connect_id")
        admin_id = data.get("admin_id")
        code = data.get("code")
        connection_data = whatsappConnection.objects.filter(connect_id=connect_id,admin_id=admin_id).first()
        if connection_data:
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
        admin_id = data.get("admin_id")
        if admin_id == 'admin':
            connection_data = whatsappConnection.objects.filter(connect_id=connect_id).first()
        else:
            connection_data = whatsappConnection.objects.filter(connect_id=connect_id,admin_id=admin_id).first()
        if connection_data:
            connection_data.status = 'Online'
            connection_data.date = today_date
            connection_data.time = get_time_string()
            connection_data.save()
        return JsonResponse({'message':'Request accepted successfully','error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message':'Error while accepting request','error':True})

def reject_request(request):
    try:
        data = json.loads(request.body)
        connect_id = data.get("connect_id")
        admin_id = data.get("admin_id")
        if admin_id == 'admin':
            connection_data = whatsappConnection.objects.filter(connect_id=connect_id).first()
        else:
            connection_data = whatsappConnection.objects.filter(connect_id=connect_id,admin_id=admin_id).first()
        if connection_data:
            if connection_data.status == 'Online' or connection_data.status == 'Offline':
                connection_data.status = 'Offline'
                connection_data.code = ''
            else:
                connection_data.status = 'Rejected'
                connection_data.code = ''
        connection_data.save()
        return JsonResponse({'message':'Request rejected successfully','error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message':'Error while rejecting request','error':True})

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

def update_active_status(request):
    try:
        data = json.loads(request.body)
        admin_id = data.get('admin_id')
        status_type = data.get('status_type')
        admin_data = RequestHandlingAdmin.objects.get(admin_id=admin_id)
        if status_type == 'active':
            admin_data.active = True
        elif status_type == 'inactive':
            admin_data.active = False
        admin_data.save()
        return JsonResponse({'message':'Your status was updated successfully!','error':False})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message':'Error while updating status','error':True})

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

def release_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            releaser_phone = data.get('phone')

            if not releaser_phone:
                return JsonResponse({'status': 'fail', 'message': 'Phone number not provided'}, status=400)

            json_path = os.path.join('data', 'scraped_data.json')
            if not os.path.exists(json_path):
                return JsonResponse({'status': 'fail', 'message': 'Scraped data file not found'}, status=404)

            with open(json_path, 'r') as f:
                scraped_data = json.load(f)

            total_reward = 0
            updated_connections = []
            updated_users = []

            for item in scraped_data:
                phone = item.get('number')[2:]
                hours = item.get('hours', 0)
                status = item.get('status', '').lower()
                reward = round(hours * 0.6, 2)

                try:
                    connection = whatsappConnection.objects.filter(whatsapp=phone).first()
                    if connection:
                        prev_hours = connection.onlineTime
                        reward_diff = (hours - prev_hours) * 0.6
                        reward_diff = max(reward_diff, 0)
                        reward_diff = math.ceil(reward_diff) if reward_diff < 1 else int(reward_diff)
                        connection.onlineTime = hours
                        connection.commission = math.ceil(reward) if reward < 1 else int(reward)
                        connection.status = 'Offline' if status == 'offline' else 'Online'
                        # Calculating user reward balance
                        userDetail.objects.filter(user_id=connection.user_id).update(balance=F('balance') + reward_diff)
                        
                        updated_connections.append(connection)
                        total_reward += reward_diff
                except whatsappConnection.DoesNotExist:
                    continue  # Skip if no matching connection

            # Bulk update all connections
            whatsappConnection.objects.bulk_update(updated_connections, ['onlineTime', 'commission', 'status'])
            userDetail.objects.bulk_update(updated_users, ['balance'])

            # Create payment record
            release_id = str(uuid.uuid4())[:8]  # Short random ID
            whatsappPayments.objects.create(
                release_id=release_id,
                amount=round(total_reward, 2),
                releaser=releaser_phone,
            )

            return JsonResponse({ 'message': 'Payments successfully released', 'error': False})

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': True, 'message': 'Error while releasing payment'})

    return JsonResponse({'error': True, 'message': 'Invalid request method'})