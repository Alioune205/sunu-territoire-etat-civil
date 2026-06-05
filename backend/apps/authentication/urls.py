"""
URL configuration for the Authentication app.
"""
from django.urls import path

from .views import LoginView, RegisterView, CustomTokenRefreshView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='auth-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
]
