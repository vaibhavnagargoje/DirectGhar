from django.urls import path
from . import views

urlpatterns = [
    # ... other auth urls ...
    path('dashboard/', views.dashboard, name='dashboard'),
]