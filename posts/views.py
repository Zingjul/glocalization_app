from rest_framework import generics, permissions, serializers
from .models import Post, Category
from .serializers import PostSerializer, CategorySerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError

class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        try:
            category_id = self.request.data.get('category')
            if category_id:
                category = Category.objects.get(pk=category_id)
            else:
                category = None
            serializer.save(author=self.request.user, category=category)
        except Category.DoesNotExist:
            raise ValidationError({'category': ['Category does not exist.']})

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        try:
            category_id = self.request.data.get('category')
            if category_id:
                category = Category.objects.get(pk=category_id)
            else:
                category = None
            serializer.save(author=self.request.user, category=category)
        except Category.DoesNotExist:
            raise ValidationError({'category': ['Category does not exist.']})

    def perform_destroy(self, instance):
        if instance.author != self.request.user and not self.request.user.is_staff:
            raise serializers.ValidationError("You do not have permission to delete this post.")
        instance.delete()