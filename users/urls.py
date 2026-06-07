from django.urls import path
from . import views
from .views import switch_role

urlpatterns = [
    path('login/', views.login),
    path('register/', views.register),
    path('switch-role/', switch_role, name='switch-role'),
]