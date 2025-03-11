from django.http import JsonResponse
from webshade.celery import app
from django.views.decorators.csrf import csrf_exempt

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
