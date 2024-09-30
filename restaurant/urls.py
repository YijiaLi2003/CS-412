# restaurant/urls.py
from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.restaurant, name='restaurant'),
    path('restaurant/', views.restaurant, name='restaurant'),
    path('order/', views.order, name='order'),
    path('confirmation/', views.confirmation, name='confirmation'),
]
