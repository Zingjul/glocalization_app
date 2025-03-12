from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from posts.models import Post
from .models import Comment

User = get_user_model()

class CommentAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        self.post = Post.objects.create(author=self.user, description="test post", author_phone_number="+1234567890")
        self.comment = Comment.objects.create(post=self.post, author=self.user, text="test comment")
        self.comment2 = Comment.objects.create(post=self.post, author=self.user2, text="test comment 2")

    def test_comment_list_api(self):
        response = self.client.get(reverse('comment-list'))
        self.assertEqual(response.status_code, 200)

    def test_comment_detail_api(self):
        response = self.client.get(reverse('comment-detail', args=[self.comment.pk]))
        self.assertEqual(response.status_code, 200)

    def test_create_comment_api(self):
        self.client.force_authenticate(user=self.user)
        data = {'post': self.post.pk, 'text': 'new comment'}
        response = self.client.post(reverse('comment-list'), data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Comment.objects.filter(text='new comment').exists())

    def test_update_comment_api(self):
        self.client.force_authenticate(user=self.user)
        data = {'text': 'updated comment', 'post': self.post.pk}
        response = self.client.put(reverse('comment-detail', args=[self.comment.pk]), data)
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'updated comment')

    def test_delete_comment_api(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('comment-detail', args=[self.comment.pk]))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_update_comment_api_permission_denied(self):
        self.client.force_authenticate(user=self.user)
        data = {'text': 'updated comment', 'post': self.post.pk}
        response = self.client.put(reverse('comment-detail', args=[self.comment2.pk]), data)
        self.assertEqual(response.status_code, 403)

    def test_delete_comment_api_permission_denied(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('comment-detail', args=[self.comment2.pk]))
        self.assertEqual(response.status_code, 403)