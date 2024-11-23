from django.urls import path
from . import views

app_name = 'gaming'

urlpatterns = [
    path('genres/', views.GenreListView.as_view(), name='genre-list'),
    path('genres/<int:pk>/', views.GenreDetailView.as_view(), name='genre-detail'),
    path('games/', views.GameListView.as_view(), name='game-list'),
    path('games/<int:pk>/', views.GameDetailView.as_view(), name='game-detail'),
    path('progress/', views.ProgressListView.as_view(), name='progress-list'),
    path('progress/<int:pk>/', views.ProgressDetailView.as_view(), name='progress-detail'),
]
