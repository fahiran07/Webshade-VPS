from django.http import JsonResponse
from webshade.celery import app
from django.views.decorators.csrf import csrf_exempt
from webshadeApp.models import userDetail, whatsappConnection
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
import traceback
from datetime import date,datetime
today_date = date.today().strftime("%d-%m-%Y")


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
        print(today_date)
        users = userDetail.objects.all()
        total_users = users.count()
        today_users = users.filter(last_login=today_date).count()
        total_balance = users.aggregate(Sum("balance"))["balance__sum"] or 0
        total_commision = users.aggregate(Sum("commision"))["commision__sum"] or 0
        return JsonResponse({
            "total_users": total_users,
            "today_users": today_users,
            "total_balance": total_balance,
            "total_commision": total_commision
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
        })
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error':True})