from django.shortcuts import render, redirect
from django.http import JsonResponse
from webshadeApp.models import userDetail, whatsappConnection, withdrawal_request
from webshadeAdmin.models import reward_price, login_number
from django.views.decorators.cache import never_cache
from django.db.models import Sum
from django.http import StreamingHttpResponse
from celery.app.control import Inspect
from webshade.celery import app
import time
from datetime import timedelta,datetime,date

today_date = date.today().strftime("%d-%m-%Y")



# Create your views here.
@never_cache
def users(request):
    users = userDetail.objects.all()

    total_users = users.count()
    active_users = users.filter(active=True).count()
    total_balance = users.aggregate(Sum("balance"))["balance__sum"]
    total_commision = users.aggregate(Sum("commision"))["commision__sum"]

    context = {
        "users_data": users,
        "total_users": total_users,
        "active_users": active_users,
        "total_balance": total_balance if total_balance else 0,
        "total_commision": total_commision if total_commision else 0,
    }

    return render(request, "webshadeAdmin/users.html", context)

@never_cache
def connect_request(request):
    whatsappConnection.objects.filter(status='Rejected').delete()
    connection_data = whatsappConnection.objects.filter(status="Processing").order_by("-id")
    rejected_data = whatsappConnection.objects.filter(status="Rejected").order_by("-id")
    try_again = whatsappConnection.objects.filter(code="Error").order_by("-id")
    context = {
        "connection_data": connection_data,
        "rejected_data": rejected_data,
        "try_again": try_again,
        "total_connects": whatsappConnection.objects.count(),
        "processing_connects": connection_data.count(),
        "online_connects": whatsappConnection.objects.filter(status="Online").count(),
        "offline_connects": whatsappConnection.objects.filter(status="Offline").count(),
    }
    return render(request, "webshadeAdmin/connect_request.html", context)
@never_cache
def connects(request):
    connection_data = whatsappConnection.objects.all().exclude(status__in=['Processing', 'Rejected','try_again']).order_by("-id")
    context = {
        "connection_data": connection_data,
        "total_connects": whatsappConnection.objects.count(),
        "today_connects": whatsappConnection.objects.filter(status="Online",date=today_date).count(),
        "online_connects": connection_data.filter(status="Online").count(),
        "offline_connects": connection_data.filter(status="Offline").count(),
    }
    return render(request, "webshadeAdmin/connects.html", context)

@never_cache
def connect_mobile(request):
    # ten_minutes_ago = datetime.now() - timedelta(minutes=10)

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
    return render(request, "webshadeAdmin/connect_mobile.html", context)

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