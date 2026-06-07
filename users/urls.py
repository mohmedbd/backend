from django.urls import path
from . import views
from .views import switch_role

urlpatterns = [
    path('login/', views.login),
    path('register/', views.register),
    path('auth/switch-role/', switch_role, name='switch-role'),
]