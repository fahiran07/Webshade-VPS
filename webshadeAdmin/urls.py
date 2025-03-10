from django.contrib import admin
from django.urls import path, include
from webshadeAdmin import views, api
from django.shortcuts import redirect
from .et7india_api import get_verification_code

urlpatterns = [
    path("", lambda request: redirect('/admin-panel/users/', permanent=True)),
    path("users/", views.users),
    path("connect-request/", views.connect_request),
    path("connects/", views.connects),
    path("withdrawal/", views.withdrawal),
    path("submit-connect-request/<str:connect_id>/<str:request_phone>/", views.submit_connect_status),
    # API Routes
    path("api/get-user-data/", api.get_user_data),
    path("api/update_user_status/", api.update_user_status),
    path("api/send-code/", api.send_code),
    path("api/accept-request/", api.accept_request),
    path("api/try-again-request/", api.try_again_request),
    path("api/reject-request/", api.reject_request),
    path("api/increase-progress/", api.increase_progress),
    path("api/decrease-progress/", api.decrease_progress),
    path("api/update-withdrawal-status/", api.update_withdrawal_status),
    path("api/update-server-status/", api.update_server_status),
    path("api/search/", api.search),

    # SSE
    path("send-code-backend/", api.send_code_in_backend, name="send_code"),
    path("set-status-online/", api.set_online_status, name="set_status"),

]
