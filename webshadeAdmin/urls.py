from django.contrib import admin
from django.urls import path, include
from webshadeAdmin import views, api, get_api
from django.shortcuts import redirect

urlpatterns = [
    path("", lambda request: redirect('/admin-panel-124432/users/', permanent=True)),
    path("users/", views.users),
    path("connect-request/", views.connect_request),
    path("connect-mobile/", views.connect_mobile),
    path("connects/", views.connects),
    path("withdrawal/", views.withdrawal),
    path("celery-connects/", views.celery_connects),
    path("admins/", views.request_admins),
    path("submit-connect-request/<str:connect_id>/<str:request_phone>/", views.submit_connect_status),
    # API Routes
    path("api/get-user-data/", api.get_user_data),
    path("api/send-code/", api.send_code),
    path("api/accept-request/", api.accept_request),
    path("api/try-again-request/", api.try_again_request),
    path("api/reject-request/", api.reject_request),
    path("api/increase-progress/", api.increase_progress),
    path("api/decrease-progress/", api.decrease_progress),
    path("api/update-withdrawal-status/", api.update_withdrawal_status),
    path("api/update-server-status/", api.update_server_status),
    path("api/search/", api.search),

    # Get Data API
    path("api/get-celery-data/", get_api.get_running_tasks),
    path("api/dashboard-data/", get_api.dashboard_data),
    path("api/connects-request-data/", get_api.connect_request_data),
    path("api/connects-data/", get_api.connects_data),
]
