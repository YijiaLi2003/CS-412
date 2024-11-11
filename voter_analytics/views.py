# voter_analytics/views.py

from django.views.generic import ListView, DetailView
from .models import Voter
import plotly.express as px
from plotly.offline import plot
import pandas as pd

class VoterListView(ListView):
    model = Voter
    template_name = 'voter_analytics/voter_list.html'
    context_object_name = 'voters'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['party_list'] = Voter.objects.values_list('party_affiliation', flat=True).distinct()
        context['years'] = range(1900, 2024)
        context['voter_scores'] = range(0, 6)
        context['elections'] = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        context['selected_voted_in'] = self.request.GET.getlist('voted_in')
        context['selected_party_affiliation'] = self.request.GET.get('party_affiliation', '')
        context['selected_min_dob'] = self.request.GET.get('min_dob', '')
        context['selected_max_dob'] = self.request.GET.get('max_dob', '')
        context['selected_voter_score'] = self.request.GET.get('voter_score', '')
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        party_affiliation = self.request.GET.get('party_affiliation')
        min_dob = self.request.GET.get('min_dob')
        max_dob = self.request.GET.get('max_dob')
        voter_score = self.request.GET.get('voter_score')
        voted_in = self.request.GET.getlist('voted_in')

        if party_affiliation:
            queryset = queryset.filter(party_affiliation=party_affiliation)
        if min_dob:
            queryset = queryset.filter(date_of_birth__year__gte=int(min_dob))
        if max_dob:
            queryset = queryset.filter(date_of_birth__year__lte=int(max_dob))
        if voter_score:
            queryset = queryset.filter(voter_score=int(voter_score))
        if voted_in:
            for election in voted_in:
                queryset = queryset.filter(**{election: True})

        return queryset

class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'

class GraphsView(ListView):
    model = Voter
    template_name = 'voter_analytics/graphs.html'
    context_object_name = 'voters'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = self.get_filtered_queryset()

        df = pd.DataFrame(list(queryset.values()))

        graphs = []

        if not df.empty:
            df['date_of_birth'] = pd.to_datetime(df['date_of_birth'])
            df['date_of_registration'] = pd.to_datetime(df['date_of_registration'])
            df['year_of_birth'] = df['date_of_birth'].dt.year

            birth_year_counts = df['year_of_birth'].value_counts().sort_index()
            fig1 = px.bar(
                x=birth_year_counts.index,
                y=birth_year_counts.values,
                labels={'x': 'Year of Birth', 'y': 'Number of Voters'},
                title='Distribution of Voters by Year of Birth'
            )
            plot_div1 = plot(fig1, output_type='div', include_plotlyjs=False)
            graphs.append(plot_div1)

            party_counts = df['party_affiliation'].value_counts()
            fig2 = px.pie(
                names=party_counts.index,
                values=party_counts.values,
                title='Distribution of Voters by Party Affiliation'
            )
            plot_div2 = plot(fig2, output_type='div', include_plotlyjs=False)
            graphs.append(plot_div2)

            elections = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
            participation_counts = df[elections].sum()
            fig3 = px.bar(
                x=elections,
                y=participation_counts.values,
                labels={'x': 'Election', 'y': 'Number of Voters'},
                title='Voter Participation in Elections'
            )
            plot_div3 = plot(fig3, output_type='div', include_plotlyjs=False)
            graphs.append(plot_div3)
        else:
            graphs = ['<p>No data available for the selected filters.</p>']

        context['graphs'] = graphs

        context.update(self.get_filter_context())

        return context

    def get_queryset(self):
        return self.get_filtered_queryset()

    def get_filtered_queryset(self):
        queryset = super().get_queryset()
        # Get filter parameters
        party_affiliation = self.request.GET.get('party_affiliation')
        min_dob = self.request.GET.get('min_dob')
        max_dob = self.request.GET.get('max_dob')
        voter_score = self.request.GET.get('voter_score')
        voted_in = self.request.GET.getlist('voted_in')

        # Apply filters
        if party_affiliation:
            queryset = queryset.filter(party_affiliation=party_affiliation)
        if min_dob:
            queryset = queryset.filter(date_of_birth__year__gte=int(min_dob))
        if max_dob:
            queryset = queryset.filter(date_of_birth__year__lte=int(max_dob))
        if voter_score:
            queryset = queryset.filter(voter_score=int(voter_score))
        if voted_in:
            for election in voted_in:
                queryset = queryset.filter(**{election: True})

        return queryset

    def get_filter_context(self):
        context = {}
        context['party_list'] = Voter.objects.values_list('party_affiliation', flat=True).distinct()
        context['years'] = range(1900, 2024)
        context['voter_scores'] = range(0, 6)
        context['elections'] = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        context['selected_voted_in'] = self.request.GET.getlist('voted_in')
        context['selected_party_affiliation'] = self.request.GET.get('party_affiliation', '')
        context['selected_min_dob'] = self.request.GET.get('min_dob', '')
        context['selected_max_dob'] = self.request.GET.get('max_dob', '')
        context['selected_voter_score'] = self.request.GET.get('voter_score', '')
        return context
