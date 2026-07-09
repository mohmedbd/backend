from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('token/refresh/', views.token_refresh, name='token-refresh'),
    path('switch-role/', views.switch_role, name='switch-role'),
    path('assign-role/', views.assign_role, name='assign-role'),
    path('remove-role/', views.remove_role, name='remove-role'),
]
