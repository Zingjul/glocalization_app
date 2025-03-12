import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from accounts.models import CustomUser
from accounts.forms import CustomUserCreationForm, CustomPasswordResetForm, CustomPasswordChangeForm
import random
import string

User = get_user_model()

class AccountsViewsTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.api_client = APIClient()
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        self.username = f'testuser_{random_string}'
        self.password = 'testpassword'
        self.email = f'testuser_{random_string}@example.com'
        self.user = User.objects.create_user(username=self.username, password=self.password, email=self.email)

    def test_user_list_api(self):
        response = self.api_client.get(reverse('user-list'))
        self.assertEqual(response.status_code, 200)

    def test_user_detail_api(self):
        response = self.api_client.get(reverse('user-detail', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)

    def test_signup_view(self):
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        form_data = {
            'username': f'newuser{random_string}',
            'email': 'newuser@example.com',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
            'phone_number': '+1234567890',
            'country': 'US',
            'state': 'CA',
            'home_town': 'LA',
        }
        form = CustomUserCreationForm(data=form_data)
        if not form.is_valid():
            print(form.errors)
        response = self.client.post(reverse('signup'), form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username=f'newuser{random_string}').exists())
        self.assertContains(response, "Your account has been created!")

    def test_signup_success_view(self):
        response = self.client.get(reverse('signup_success') + f'?virtual_id={self.user.virtual_id}')
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('_auth_user_id'))

    def test_password_reset_view(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)

    def test_password_change_view(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 200)

    def test_custom_user_creation_form(self):
        form = CustomUserCreationForm(data={'username': 'formuser', 'email': 'formuser@example.com', 'password1': 'formpass', 'password2': 'formpass', 'phone_number': '+1234567890', 'country': 'US', 'state': 'CA', 'home_town': 'LA'})
        self.assertTrue(form.is_valid())

    def test_custom_password_change_form(self):
        self.client.login(username=self.username, password=self.password)
        form = CustomPasswordChangeForm(user=self.user, data={'old_password': self.password, 'new_password1': 'StrongPassword123', 'new_password2': 'StrongPassword123'})
        self.assertTrue(form.is_valid())