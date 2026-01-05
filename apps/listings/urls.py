# apps/core/urls.py
from django.urls import path
from . import views

urlpatterns = [
     path('', views.listings, name='listings'), 
    
]