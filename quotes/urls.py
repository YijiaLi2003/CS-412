
from django.urls import path
from django.conf import settings
from . import views

# all of the URLs that are part of this app
urlpatterns = [
    path('', views.quote, name='quote'),  # Main page
    path('quote/', views.quote, name='quote'),
    path('show_all/', views.show_all, name='show_all'),  # Show all quotes and images
    path('about/', views.about, name='about'),  # About page
]