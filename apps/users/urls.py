from django.urls import path
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path('login/', views.auth_entry, name='login'), # Unified Entry
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('complete-profile/', views.complete_profile_view, name='complete_profile'),
    
    # Register URL redirects to login now, as it's a unified flow
    path('register/', lambda r: redirect('login'), name='register'),
    
    # Keep others...
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]