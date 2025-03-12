from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_username', 'text', 'created_at', 'updated_at', 'parent', 'replies']
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_replies(self, obj):
        replies = Comment.objects.filter(parent=obj)
        serializer = CommentSerializer(replies, many=True)
        return serializer.data

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    # Remove the permission checks from update and delete
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def delete(self, instance):
        instance.delete()