from django.shortcuts import render, redirect
from django.http import JsonResponse
from webshadeApp.models import userDetail, whatsappConnection, withdrawal_request
from webshadeAdmin.models import reward_price, login_number
from django.db.models import Sum, F, Q, Subquery, Max
from django.views.decorators.cache import never_cache
from django.db.models import Sum
from django.http import StreamingHttpResponse
from celery.app.control import Inspect
from webshade.celery import app
import time

today_date = localtime().strftime("%d-%m-%Y")



# Create your views here.
@never_cache
def users(request):
    users = userDetail.objects.filter(last_login=today_date)
    context = {
        "users_data": users,
    }
    return render(request, "webshadeAdmin/users.html", context)

@never_cache
def connect_request(request):
    connection_data = whatsappConnection.objects.filter(status="Processing").order_by("-id")
    other_request = whatsappConnection.objects.exclude(status__in=['Processing','Online','Offline']).order_by("-id")
    context = {
        "connection_data": connection_data,
        "other_request": other_request,
    }
    return render(request, "webshadeAdmin/connect_request.html", context)
@never_cache
def connects(request):
    connection_data = whatsappConnection.objects.filter(status__in=['Offline','Online']).order_by("-id")
    context = {
        "connection_data": connection_data,
    }
    return render(request, "webshadeAdmin/connects.html", context)

@never_cache
def connect_mobile(request):

    # # Fetch data with filtering directly on DB
    connection_data = whatsappConnection.objects.filter(Q(status='Online') | Q(status='Offline')).order_by("-id")
    if reward_price.objects.all().first().server_status == False:
        server_status = "DOWN"
    else:
        server_status = "OPEN"
    # Convert time to 12-hour format for display
    for connection in connection_data:
        connection.time = connection.time.strftime("%I:%M %p")

    context = {
        "connection_data": connection_data,
        "server_status": server_status,
    }
    return render(request, "webshadeAdmin/mobile/connect_mobile.html", context)

@never_cache
def submit_connect_status(request,connect_id,request_phone):
    context = {
        'currentConnectId':connect_id,
        'request_phone':request_phone,
    }
    return render(request, "webshadeAdmin/submit_connect_status.html", context)

@never_cache
def withdrawal(request):
    withdrawal_data = withdrawal_request.objects.all()
    context = {
        'withdrawal_data':withdrawal_data,
        'total_withdrawal':withdrawal_data,
        'success_withdrawal':withdrawal_data.filter(status='Success'),
        'processing_withdrawal':withdrawal_data.filter(status='Processing'),
        'failed_withdrawal':withdrawal_data.filter(status='Failed'),
    }
    return render(request,'webshadeAdmin/withdrawal.html',context)

@never_cache
def celery_connects(request):
    i = app.control.inspect()  # Correct way to inspect Celery tasks

    # If inspect() returns None, replace with an empty dict
    active_tasks = i.active() or {}
    scheduled_tasks = i.scheduled() or {}
    reserved_tasks = i.reserved() or {}

    # Function to count tasks safely (handle empty dict)
    def count_tasks(task_dict):
        return sum(len(tasks) for tasks in task_dict.values()) if task_dict else 0

    context = {
        "active_tasks": count_tasks(active_tasks),
        "scheduled_tasks": count_tasks(scheduled_tasks),
        "reserved_tasks": count_tasks(reserved_tasks),
        "total_tasks": count_tasks(active_tasks) + count_tasks(scheduled_tasks) + count_tasks(reserved_tasks)
    }

    return render(request, 'webshadeAdmin/celery_connects.html', context)