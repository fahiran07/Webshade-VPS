from django.contrib import admin
from django.urls import path, include
from webshadeAdmin import views, api, get_api
from django.shortcuts import redirect

urlpatterns = [
    path("", lambda request: redirect('/admin-panel/users/', permanent=True)),
    path("users/", views.users),
    path("connect-request/", views.connect_request),
    path("admin-panel/", views.admin_panel),
    path("connects/", views.connects),
    path("withdrawal/", views.withdrawal),
    path("admins/", views.request_admins),
    path("payments/", views.payment),
    path("login/", views.login_admin),
    path("logout/", views.logout_admin),
    # API Routes
    path("api/get-user-data/", api.get_user_data),
    path("api/send-code/", api.send_code),
    path("api/accept-request/", api.accept_request),
    path("api/reject-request/", api.reject_request),
    path("api/update-withdrawal-status/", api.update_withdrawal_status),
    path("api/update-server-status/", api.update_server_status),
    path("api/search/", api.search),
    path("api/admin-login/", api.admin_login),
    path("api/login/", api.superuser_login),
    path("api/release-payment/", api.release_payment),
    path('api/update-active-status', api.update_active_status),

    # Get Data API
    path("api/get-celery-data/", get_api.get_running_tasks),
    path("api/dashboard-data/", get_api.dashboard_data),
    path("api/connects-request-data/", get_api.connect_request_data),
    path("api/connects-data/", get_api.connects_data),
    path("api/get-admin-whatsapp-request/", get_api.get_admin_requests),
    path("api/get-task-data/", get_api.get_task_data),
]
