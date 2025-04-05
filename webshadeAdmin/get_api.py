from django.http import JsonResponse
from webshade.celery import app
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, F, Q, Subquery, Max, ExpressionWrapper, IntegerField
from django.db.models.functions import Coalesce
from django.db.models import Value
from django.db.models import Count
from webshadeApp.models import userDetail, whatsappConnection
from webshadeAdmin.models import RequestHandlingAdmin, reward_price, revenueRecord
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now, localtime
from webshadeAdmin.functions import get_date_string, get_time_string
from datetime import timedelta
from django.db.models import Sum
import traceback
from datetime import datetime
import json
today_date = localtime().strftime("%d-%m-%Y")


@csrf_exempt
def get_running_tasks(request):
    i = app.control.inspect()  # Celery task inspection

    # Handle None cases to prevent errors
    active_tasks = i.active() or {}
    scheduled_tasks = i.scheduled() or {}
    reserved_tasks = i.reserved() or {}

    # Function to count tasks safely
    def count_tasks(task_dict):
        return sum(len(tasks) for tasks in task_dict.values()) if task_dict else 0

    # Function to extract task details
    def extract_task_details(task_dict):
        task_list = []
        for worker, tasks in (task_dict or {}).items():
            for task in tasks:
                task_list.append({
                    "id": task.get("id", "N/A"),
                    "name": task.get("name", "N/A"),
                    "status": "Active" if task_dict == active_tasks else "Scheduled" if task_dict == scheduled_tasks else "Reserved",
                    "timestamp": task.get("time_start", "N/A"),
                })
        return task_list

    return JsonResponse({
        "active_tasks": count_tasks(active_tasks),
        "scheduled_tasks": count_tasks(scheduled_tasks),
        "reserved_tasks": count_tasks(reserved_tasks),
        "total_tasks": count_tasks(active_tasks) + count_tasks(scheduled_tasks) + count_tasks(reserved_tasks),
        "tasks": extract_task_details(active_tasks) + extract_task_details(scheduled_tasks) + extract_task_details(reserved_tasks)
    })
@csrf_exempt
def dashboard_data(request):
    try:
        users = userDetail.objects.all()
        total_users = users.count()
        today_users = users.filter(last_login=today_date).count()
        total_balance = users.aggregate(Sum("balance"))["balance__sum"] or 0
        total_commision = users.aggregate(Sum("commision"))["commision__sum"] or 0
        return JsonResponse({
            "total_users": total_users,
            "today_users": today_users,
            "total_balance": total_balance,
            "total_commision": total_commision,
        })
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error':True})
@csrf_exempt
def connect_request_data(request):
    try:
        connection_data = whatsappConnection.objects.filter(status__in=['Online','Offline','Processing']).order_by("-id")
        return JsonResponse({
            "total_connects": connection_data.count(),
            "processing_connects": connection_data.filter(status='Processing').count(),
            "online_connects": connection_data.filter(status="Online").count(),
            "offline_connects": connection_data.filter(status="Offline").count(),
        })
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error':True})

@csrf_exempt
def connects_data(request):
    try:
        connection_data = whatsappConnection.objects.filter(status__in=['Online','Offline','Processing']).order_by("-id")
        return JsonResponse({
            "total_connects": connection_data.count(),
            "today_connects": connection_data.filter(date=today_date).count(),
            "online_connects": connection_data.filter(status="Online").count(),
            "offline_connects": connection_data.filter(status="Offline").count(),
            "total_revenue": (whatsappConnection.objects.aggregate(Sum('onlineTime'))['onlineTime__sum'] or 0) * 1,
        })
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error':True})

def get_admin_requests(request):
    try:
        data = json.loads(request.body)
        admin_id = data.get('admin_id')
        admin_data = RequestHandlingAdmin.objects.get(admin_id=admin_id)
        server_status = reward_price.objects.all().first().server_status
        existing_connect_ids = data.get('existing_connect_ids')
        request_admins = list(whatsappConnection.objects.filter(status='Processing',admin_id=admin_id).exclude(connect_id__in=existing_connect_ids).order_by("-id").values())
        for obj in request_admins:
            if obj['time']:
                # Convert string to time object
                time_obj = datetime.strptime(obj['time'], '%H:%M:%S').time()
                # Now convert to 12-hour format
                obj['time'] = time_obj.strftime('%I:%M %p')  # e.g., '04:45 PM'
        return JsonResponse({"request_admins": request_admins,'active':admin_data.active,'server_status':server_status,'error':False,'special_staff':admin_data.special_staff})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error':True,'message':'Error while loading admin requests'})

def request_admin_data(request):
    try:
        request_admins = RequestHandlingAdmin.objects.annotate(
            active_task=Count('connections', filter=Q(connections__status='Processing'), distinct=True),
            success_task=Count('connections', filter=Q(connections__status__in=['Offline', 'Online']), distinct=True),
            failed_task=Count('connections', filter=Q(connections__status='Rejected'), distinct=True),
            online_task=Count('connections', filter=Q(connections__status='Online'), distinct=True),
        )

        admin_list = list(request_admins.values())
        total_revenue = 0

        for admin_dict in admin_list:
            admin_id = admin_dict['admin_id']
            revenue_sum = revenueRecord.objects.filter(admin_id=admin_id).aggregate(total=Sum('withdrawal_amount'))['total'] or 0
            online_time_sum = whatsappConnection.objects.filter(admin_id=admin_id).aggregate(total=Sum('onlineTime'))['total'] or 0
            # Geting Last balance
            last_record = revenueRecord.objects.filter(admin_id=admin_id).order_by('-id').first()
            last_balance = last_record.last_balance if last_record else 0

            profit = int(revenue_sum - (online_time_sum * 0.6)) + last_balance
            payment = ((revenue_sum * 0.4) + last_balance) / 2.5
            admin_dict['total_revenue'] = revenue_sum + last_balance
            admin_dict['profit'] = profit
            admin_dict['payment'] = payment
            total_revenue += revenue_sum + last_balance

        total_admins = len(admin_list)

        success_connects = whatsappConnection.objects.filter(status='Online').exclude(admin_id='').count()
        failed_connects = whatsappConnection.objects.filter(status='Rejected').exclude(admin_id='').count()

        context = {
            'request_admins': admin_list,
            'total_admins': total_admins,
            'revenue': total_revenue,
            'success_connects': success_connects,
            'failed_connects': failed_connects,
            'error': False,
            'message': 'Admin data loaded successfully'
        }
        return JsonResponse(context)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': True, 'message': 'Error while loading admin data'})

def get_task_data(request):
    try:
        admin_id = request.GET.get('admin-id')
        success_connects = whatsappConnection.objects.filter(admin_id=admin_id,status__in=['Online','Offline']).count()
        failed_connects = whatsappConnection.objects.filter(admin_id=admin_id).exclude(status__in=['Online','Offline','Processing']).count()
        return JsonResponse({"success_connects": success_connects,'failed_connects':failed_connects,'total_connects':success_connects+failed_connects})
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error':True})

@csrf_exempt
def get_revenue_data(request):
    try:
        today = localtime().strftime("%d-%m-%Y")
        yesterday = (localtime() - timedelta(days=1)).strftime("%d-%m-%Y")
        total = revenueRecord.objects.aggregate(total=Sum('withdrawal_amount'))['total'] or 0
        today_total = revenueRecord.objects.filter(date=today).aggregate(total=Sum('withdrawal_amount'))['total'] or 0
        yest_total = revenueRecord.objects.filter(date=yesterday).aggregate(total=Sum('withdrawal_amount'))['total'] or 0
        # Getting latest balance
        records = revenueRecord.objects.only('revenue_id', 'last_balance').order_by('-id')
        seen_ids = set()
        latest_balance = 0

        for record in records:
            if record.revenue_id not in seen_ids:
                latest_balance += record.last_balance
                seen_ids.add(record.revenue_id)
        print(latest_balance)
        return JsonResponse({
            'total_revenue': total + latest_balance,
            'today_revenue': today_total,
            'yesterday_revenue': yest_total,
            'profit': int((total+latest_balance)-(whatsappConnection.objects.aggregate(Sum('onlineTime'))['onlineTime__sum'] * 0.6)),
            'error': False,
        })

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message': str(e), 'error': True})