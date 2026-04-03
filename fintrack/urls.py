from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard') if request.user.is_authenticated else redirect('login')),
    path('dashboard/', include('transactions.urls')),
    path('users/', include('users.urls')),
    path('analytics/', include('analytics.urls')),
]
