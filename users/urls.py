from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('manage/', views.user_list, name='user_list'),
    path('manage/new/', views.user_create, name='user_create'),
    path('manage/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('manage/<int:pk>/delete/', views.user_delete, name='user_delete'),
]
