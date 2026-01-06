# apps/listings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.listings, name='listings'), 
    path('post/', views.create_listing, name='post_property'),
]