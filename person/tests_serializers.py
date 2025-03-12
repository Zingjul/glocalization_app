import unittest
from persons.serializers import PersonSerializer
from persons.models import Person
from django.contrib.auth import get_user_model

User = get_user_model()

class PersonSerializerTests(unittest.TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.person = Person.objects.create(user=self.user, business_name='Test Business')

    def test_person_serializer(self):
        serializer = PersonSerializer(self.person)
        self.assertEqual(serializer.data['business_name'], 'Test Business')

    def test_person_deserialization(self):
      data = {'user': self.user.id, 'business_name': 'New Business'}
      serializer = PersonSerializer(data = data)
      self.assertTrue(serializer.is_valid())
      instance = serializer.save()
      self.assertEqual(instance.business_name, 'New Business')