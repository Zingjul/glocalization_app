# posts/filters.py
import django_filters
from django.db.models import Q
from .models import Post

class PostFilter(django_filters.FilterSet):
    # These fields will be used for custom search (e.g., /api/posts/?continent=America&country=USA)
    # The actual filtering logic is handled by the method 'filter_by_location_query'
    continent = django_filters.CharFilter(method='filter_by_location_query')
    country = django_filters.CharFilter(method='filter_by_location_query')
    state = django_filters.CharFilter(method='filter_by_location_query')
    town = django_filters.CharFilter(method='filter_by_location_query')

    class Meta:
        model = Post
        fields = ['continent', 'country', 'state', 'town', 'category'] # Add category if you want to filter by it

    def filter_by_location_query(self, queryset, name, value):
        # This method builds the dynamic Q object for custom location search.
        # It's called for each location parameter (continent, country, state, town)
        # but we need to collect all of them to build one comprehensive Q object.
        
        # We need to get all parameters from the request once to apply the combined logic
        # This approach is a bit tricky with django_filters' per-field method.
        # A more direct approach within the ViewSet's get_queryset might be cleaner
        # for this complex OR logic. Let's adjust views.py for this.
        # For now, we'll keep the filterset simple for basic exact matches,
        # and handle the complex OR logic for "global within scope" directly in the ViewSet.
        # This filter will work for exact matches and be extended in the ViewSet.
        
        # If the parameter is provided, filter for exact match
        if name == 'continent' and value:
            queryset = queryset.filter(post_continent__name__iexact=value)
        elif name == 'country' and value:
            queryset = queryset.filter(post_country__name__iexact=value)
        elif name == 'state' and value:
            queryset = queryset.filter(post_state__name__iexact=value)
        elif name == 'town' and value:
            queryset = queryset.filter(post_town__name__iexact=value)
            
        return queryset