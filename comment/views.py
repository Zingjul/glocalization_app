from rest_framework import generics, permissions, serializers
from .models import Comment
from .serializers import CommentSerializer
from rest_framework.response import Response
from rest_framework import status

class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        comment = self.get_object()
        if comment.author != self.request.user:
            raise serializers.ValidationError("You do not have permission to edit this comment.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise serializers.ValidationError("You do not have permission to delete this comment.")
        instance.delete()