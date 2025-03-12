import unittest
from posts.serializers import PostSerializer
from person.serializers import PersonSerializer
from posts.models import Post, Category
from person.models import Person
from django.contrib.auth import get_user_model

User = get_user_model()

class SearchSerializerTests(unittest.TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name='Test Category')
        self.post = Post.objects.create(author=self.user, category=self.category, product_name='Test Product')
        self.person = Person.objects.create(user=self.user, business_name='Test Business')

    def test_post_search_serializer(self):
        serializer = PostSerializer(self.post)
        self.assertEqual(serializer.data['product_name'], 'Test Product')

    def test_person_search_serializer(self):
        serializer = PersonSerializer(self.person)
        self.assertEqual(serializer.data['business_name'], 'Test Business')