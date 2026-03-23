# apps/listings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.listings, name='listings'),
    path('post/', views.create_listing, name='post_property'),
<<<<<<< HEAD
    path('save-search/', views.save_search, name='save_search'),
    path('save-search/<int:pk>/delete/', views.delete_saved_search, name='delete_saved_search'),
]
=======
    path('property/<uuid:id>/', views.property_detail, name='property_detail'),
]
>>>>>>> main
