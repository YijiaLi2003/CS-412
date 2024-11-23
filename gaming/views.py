from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Genre, Game, Progress

class GenreListView(ListView):
    model = Genre
    template_name = 'gaming/genre_list.html'
    context_object_name = 'genres'

class GenreDetailView(DetailView):
    model = Genre
    template_name = 'gaming/genre_detail.html'
    context_object_name = 'genre'

class GameListView(ListView):
    model = Game
    template_name = 'gaming/game_list.html'
    context_object_name = 'games'

class GameDetailView(DetailView):
    model = Game
    template_name = 'gaming/game_detail.html'
    context_object_name = 'game'

class ProgressListView(LoginRequiredMixin, ListView):
    model = Progress
    template_name = 'gaming/progress_list.html'
    context_object_name = 'progress_entries'

    def get_queryset(self):
        return Progress.objects.filter(user=self.request.user)

class ProgressDetailView(LoginRequiredMixin, DetailView):
    model = Progress
    template_name = 'gaming/progress_detail.html'
    context_object_name = 'progress_entry'
