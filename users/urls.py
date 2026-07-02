from django.urls import path
from . import views
from .views import switch_role, token_refresh

urlpatterns = [
    path('login/', views.login),
    path('register/', views.register),
    path('token/refresh/', token_refresh, name='token-refresh'),
    path('switch-role/', switch_role, name='switch-role'),
]
