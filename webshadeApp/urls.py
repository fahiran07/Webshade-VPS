
from django.contrib import admin
from django.urls import path, include
from webshadeApp import views, api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.connect),
    path('register', views.register_account),
    path('register/<str:refer_code>/', views.register_account),
    path('login/', views.login_account),
    path('connect/', views.connect),
    path('invite/', views.invite),
    path('account/', views.profile),
    path('withdrawal/', views.withdrawal),
    path('withdrawal-record/', views.withdrawal_record),
    path('dashboard/', views.dashboard),
    path('logout/', views.logout_account),
    
    # API Routes
    path('api/login/', api.login_account),
    path('api/register/', api.register_account),
    path('api/send-code-request/', api.send_code_request),
    path('api/check-code-request/', api.check_code_request),
    path('api/check-code-acceptence/', api.check_code_acceptence),
    path('api/withdrawal/', api.withdrawal),
    path('api/add-bank-account/', api.add_bank_account),

    # SSE
    path("send-code-backend/", api.send_code_in_backend, name="send_code"),
    path("set-status-online/", api.set_online_status, name="set_status"),
    path("update-error/", api.update_error, name="update_error"),

]
