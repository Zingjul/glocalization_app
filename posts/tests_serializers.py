import unittest
from rest_framework.test import APIRequestFactory
from posts.serializers import PostSerializer, CategorySerializer, PostImageSerializer
from posts.models import Post, Category, PostImage
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import random
import string

User = get_user_model()

class PostSerializerTests(unittest.TestCase):

    def setUp(self):
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.username = f'testuser_{random_string}'
        self.user = User.objects.create_user(username=self.username, password='testpassword')
        self.category = Category.objects.create(name=f'Test Category{random_string}')
        self.post_data = {
            'author': self.user.id,
            'category': self.category.id,
            'description': 'Test v description',
            'author_phone_number': '+12345678901',
            'author_email': 'vtest@example.com',
            'product_name': 'Test v Product',
        }
        self.factory = APIRequestFactory()

    def test_author_field(self):
        data = {'author': self.user.id, 'category':self.category.id, 'description':'test', 'author_phone_number':'+12345678901'}
        request = self.factory.post('/', data, format='multipart')
        serializer = PostSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        post = serializer.save()
        self.assertEqual(post.author, self.user)

    def test_valid_serialization(self):
        post = Post.objects.create(author=self.user, category=self.category, description='Test v description', author_phone_number='+12345678901', author_email='vtest@example.com', product_name='Test v Product')
        serializer = PostSerializer(post)
        self.assertEqual(serializer.data['description'], 'Test v description')

    def test_valid_deserialization(self):
        print(f"Post Data: {self.post_data}")
        print(f"User Object: {User.objects.get(id=self.post_data['author'])}")
        request = self.factory.post('/', self.post_data, format='multipart')
        serializer = PostSerializer(data=self.post_data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        post = serializer.save()
        self.assertEqual(post.description, 'Test v description')

    def test_invalid_deserialization_description(self):
        invalid_data = self.post_data.copy()
        invalid_data['description'] = ''
        request = self.factory.post('/', invalid_data, format='multipart')
        serializer = PostSerializer(data=invalid_data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_invalid_deserialization_product_name_too_long(self):
        invalid_data = self.post_data.copy()
        invalid_data['product_name'] = 'a' * 256
        request = self.factory.post('/', invalid_data, format='multipart')
        serializer = PostSerializer(data=invalid_data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        print(f"Serializer Errors: {serializer.errors}")
        self.assertIn('Ensure this field has no more than 255 characters.', serializer.errors['product_name'][0])

    def test_invalid_deserialization_invalid_email(self):
        invalid_data = self.post_data.copy()
        invalid_data['author_email'] = 'invalid_email'
        request = self.factory.post('/', invalid_data, format='multipart')
        serializer = PostSerializer(data=invalid_data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('Enter a valid email address.', serializer.errors['author_email'][0])

    def test_image_upload(self):
        image = SimpleUploadedFile("file.jpg", b"file_content", content_type="image/jpg")
        post_data = self.post_data.copy()
        post_data['images'] = [image]
        request = self.factory.post('/', post_data, format='multipart')
        serializer = PostSerializer(data=post_data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        post = serializer.save()
        self.assertEqual(post.images.count(), 1)

    def test_multiple_image_upload_limit(self):
        images = [SimpleUploadedFile(f"file{i}.jpg", b"file_content", content_type="image/jpg") for i in range(7)]
        post_data = self.post_data.copy()
        post_data['images'] = images
        request = self.factory.post('/', post_data, format='multipart')
        serializer = PostSerializer(data=post_data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        print(f"Serializer Errors: {serializer.errors}")
        self.assertIn('Too many images uploaded.', serializer.errors['non_field_errors'][0])

class CategorySerializerTests(unittest.TestCase):
    def test_category_serialization(self):
        category = Category.objects.create(name=f"Test Category {random.randint(1,100000)}")
        serializer = CategorySerializer(category)
        self.assertEqual(serializer.data['name'], category.name)

    def test_category_deserialization(self):
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        category_data = {'name': f'New Category {random_string}'}
        serializer = CategorySerializer(data=category_data)

        is_valid = serializer.is_valid() # Call is_valid() first

        print(f"Serializer initial data: {serializer.initial_data}")
        print(f"Serializer is_valid: {is_valid}")
        print(f"Serializer errors after validation: {serializer.errors}")
        print(f"Serializer validated data: {serializer.validated_data}")

        self.assertTrue(is_valid)

        category = serializer.save()
        self.assertEqual(category.name, f'New Category {random_string}')

    def test_category_model_valid(self):
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        category = Category.objects.create(name=f'Test Category Model {random_string}')
        self.assertEqual(category.name, f'Test Category Model {random_string}')

class PostImageSerializerTests(unittest.TestCase):
    def test_post_image_serialization(self):
        username = f"testuser_{random.randint(1,100000)}"
        post = Post.objects.create(
            author=User.objects.create_user(username=username, password="testpassword"),
            category=Category.objects.create(name=f"test{random.randint(1,100000)}"),
            description="test",
            author_phone_number="+12345678901",
            author_email="test@test.com",
            product_name="test product",
        )
        #... rest of test