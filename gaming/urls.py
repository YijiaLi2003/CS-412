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
    path('', views.SummaryView.as_view(), name='summary'),
    path('games/<int:pk>/', views.GameDetailView.as_view(), name='game-detail'),
    path('progress/add/', views.ProgressAddView.as_view(), name='progress-add'),
    path('game/create/', views.GameCreateView.as_view(), name='game-create'),
    
    
    # Progress URLs
    path('progress/', views.ProgressListView.as_view(), name='progress-list'),
    path('progress/<int:pk>/', views.ProgressDetailView.as_view(), name='progress-detail'),
    path('progress/update/<int:pk>/', views.ProgressUpdateView.as_view(), name='progress-update'),
    path('progress/create/', views.ProgressCreateView.as_view(), name='progress-create'),
    path('progress/<int:pk>/edit_form/', views.ProgressEditFormView.as_view(), name='progress-edit-form'),
    # Social Feature URLs
    path('profiles/', views.ShowAllProfilesView.as_view(), name='show-all-profiles'),
    path('profile/<int:pk>/', views.ShowProfileDetailView.as_view(), name='profile-detail'),
    path('profile/create/', views.CreateProfileView.as_view(), name='create-profile'),
    path('profile/update/', views.UpdateProfileView.as_view(), name='update-profile'),
    path('profile/friend_suggestions/', views.ShowFriendSuggestionsView.as_view(), name='friend-suggestions'),
    path('profile/add_friend/<int:other_pk>/', views.CreateFriendView.as_view(), name='add-friend'),
    path('friends-progress/', views.FriendsProgressListView.as_view(), name='friends-progress-list'),
    # News Feed URLs
    path('news-feed/', views.ShowNewsFeedView.as_view(), name='news-feed'),
    path('status/create/', views.CreateStatusMessageView.as_view(), name='create-status-message'),
    path('status/update/<int:pk>/', views.UpdateStatusMessageView.as_view(), name='update-status-message'),
    path('status/delete/<int:pk>/', views.DeleteStatusMessageView.as_view(), name='delete-status-message'),

    # Interaction URLs
    path('comment/create/', views.CreateCommentView.as_view(), name='create-comment'),
    path('like/toggle/', views.ToggleLikeView.as_view(), name='toggle-like'),

    # Authentication URLs specific to gaming
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),

    # Summary URL
    path('summary/', views.SummaryView.as_view(), name='summary'),

    path('feed_item/<int:pk>/update/', views.UpdateFeedItemView.as_view(), name='update-feed-item'),
    path('feed_item/<int:pk>/delete/', views.DeleteFeedItemView.as_view(), name='delete-feed-item'),
]
