from rest_framework import generics, permissions, filters
from posts.models import Post
from person.models import Person
from posts.serializers import PostSerializer
from person.serializers import PersonSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostSearch(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['category__name', 'product_name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination # add this line

    def get_queryset(self):
        query = self.request.query_params.get('query', None)
        if query is None:
            raise ValidationError({'query': ['This field is required.']})
        return super().get_queryset().filter(
            Q(category__name__icontains=query) | Q(product_name__icontains=query)
        )

class PersonSearch(generics.ListAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['business_name']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination # add this line

    def get_queryset(self):
        query = self.request.query_params.get('query', None)
        if query is None:
            raise ValidationError({'query': ['This field is required.']})
        return super().get_queryset().filter(business_name__icontains=query)