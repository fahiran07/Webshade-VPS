from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.db.models.functions import Coalesce
from django.db.models import Value
from django.db.models import Count
from webshadeApp.models import userDetail, whatsappConnection, withdrawal_request
from webshadeAdmin.models import reward_price, login_number, RequestHandlingAdmin, whatsappPayments
from django.db.models import Sum, F, Q, Subquery, Max, ExpressionWrapper, IntegerField
from django.views.decorators.cache import never_cache
from webshadeAdmin.functions import get_date_string, get_time_string
from django.db.models import Sum
from django.http import StreamingHttpResponse
from celery.app.control import Inspect
from django.utils.timezone import now, localtime
from webshade.celery import app
import time

today_date = localtime().strftime("%d-%m-%Y")



# Create your views here.

@never_cache

def login_admin(request):
    return render(request, "webshadeAdmin/login.html")
@never_cache
def users(request):
    if not request.user.is_superuser:
        return redirect('/admin-panel/login/')
    users = userDetail.objects.all()
    context = {
        "users_data": users,
    }
    return render(request, "webshadeAdmin/users.html", context)

@never_cache
def connect_request(request):
    if not request.user.is_superuser:
        return redirect('/admin-panel/login/')
    connection_data = whatsappConnection.objects.filter(status="Processing").order_by("-id")
    other_request = whatsappConnection.objects.exclude(status__in=['Processing','Online','Offline']).order_by("-id")
    context = {
        "connection_data": connection_data,
        "other_request": other_request,
    }
    return render(request, "webshadeAdmin/connect_request.html", context)

@never_cache
def connects(request):
    if not request.user.is_superuser:
        return redirect('/admin-panel/login/')
    connection_data = whatsappConnection.objects.filter(status__in=['Offline','Online']).order_by("-id")
    context = {
        "connection_data": connection_data,
    }
    return render(request, "webshadeAdmin/connects.html", context)

@never_cache
def admin_panel(request):
    # # Fetch data with filtering directly on DB
    if reward_price.objects.all().first().server_status == False:
        server_status = "DOWN"
    else:
        server_status = "OPEN"

    context = {
        "server_status": server_status,
    }
    return render(request, "webshadeAdmin/mobile/admin_panel.html", context)

@never_cache
def withdrawal(request):
    if not request.user.is_superuser:
        return redirect('/admin-panel/login/')
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
def request_admins(request):
    if not request.user.is_superuser:
        return redirect('/admin-panel/login/')
    # First: annotate only counts
    request_admins = RequestHandlingAdmin.objects.annotate(
        active_task=Count('connections', filter=Q(connections__status='Processing'), distinct=True),
        success_task=Count('connections', filter=Q(connections__status__in=['Offline', 'Online']), distinct=True),
        failed_task=Count('connections', filter=Q(connections__status='Rejected'), distinct=True),
    )
    
    # Then annotate revenue separately (optional)
    request_admins = request_admins.annotate(
    total_revenue=ExpressionWrapper(Coalesce(Sum('connections__onlineTime'), Value(0)) * 1,output_field=IntegerField()),
    profit=ExpressionWrapper(Coalesce(Sum('connections__onlineTime'), Value(0)) * 0.4,output_field=IntegerField())
    )
    total_admins = request_admins.count()
    revenue = sum(admin.total_revenue or 0 for admin in request_admins)
    success_connects = whatsappConnection.objects.filter(status='Online').exclude(admin_id='').count()
    failed_connects = whatsappConnection.objects.filter(status='Rejected').exclude(admin_id='').count()
    context = {
        'request_admins':request_admins,
        'total_admins':total_admins,
        'revenue':revenue,
        'success_connects':success_connects,
        'failed_connects':failed_connects,
    }
    return render(request,'webshadeAdmin/request_admin.html',context)

@never_cache
def payment(request):
    if not request.user.is_superuser:
        return redirect('/admin-panel/login/')
    payment_release_data = whatsappPayments.objects.all().order_by('-id')
    today_releases = payment_release_data.filter(date=today_date)
    total_released_amount = payment_release_data.aggregate(Sum('amount'))['amount__sum'] or 0
    total_withdraw_amount = withdrawal_request.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    context = {
        'payment_release_data':payment_release_data,
        'total_releases':payment_release_data.count(),
        'today_releases':today_releases.count(),
        'total_released_amount':total_released_amount,
        'total_withdraw_amount':total_withdraw_amount,
    }
    return render(request,'webshadeAdmin/payment.html',context)

def logout_admin(request):
    logout(request)
    return redirect('/admin-panel/login')