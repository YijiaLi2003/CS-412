# gaming/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views 
from . import views

app_name = 'gaming'

urlpatterns = [
    # Genre URLs
    path('genres/', views.GenreListView.as_view(), name='genre-list'),
    path('genres/<int:pk>/', views.GenreDetailView.as_view(), name='genre-detail'),
    
    # Game URLs
    path('games/', views.GameListView.as_view(), name='game-list'),
    path('games/<int:pk>/', views.GameDetailView.as_view(), name='game-detail'),
    
    # Progress URLs
    path('progress/', views.ProgressListView.as_view(), name='progress-list'),
    path('progress/<int:pk>/', views.ProgressDetailView.as_view(), name='progress-detail'),
    
    # Social Feature URLs
    path('profiles/', views.ShowAllProfilesView.as_view(), name='show-all-profiles'),
    path('profile/<int:pk>/', views.ShowProfileDetailView.as_view(), name='profile-detail'),
    path('profile/create/', views.CreateProfileView.as_view(), name='create-profile'),
    path('profile/update/', views.UpdateProfileView.as_view(), name='update-profile'),
    path('profile/friend_suggestions/', views.ShowFriendSuggestionsView.as_view(), name='friend-suggestions'),
    path('profile/news_feed/', views.ShowNewsFeedView.as_view(), name='news-feed'),
    path('status/create/', views.CreateStatusMessageView.as_view(), name='create-status'),
    path('status/<int:pk>/update/', views.UpdateStatusMessageView.as_view(), name='update-status'),
    path('status/<int:pk>/delete/', views.DeleteStatusMessageView.as_view(), name='delete-status'),
    path('profile/add_friend/<int:other_pk>/', views.CreateFriendView.as_view(), name='add-friend'),
    path('friends-progress/', views.FriendsProgressListView.as_view(), name='friends-progress-list'),

    # Authentication URLs specific to gaming
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
]
