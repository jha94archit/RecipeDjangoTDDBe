from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingridient
from recipe.serializers import IngridientSerializer

INGRIDIENT_URL = reverse('recipe:ingridient-list')


class PublicIngridientAPITests(TestCase):
    """Test publicly available ingridients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint """
        res = self.client.get(INGRIDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngridientAPITests(TestCase):
    """Test private ingridient API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@mail.com',
            'testpass'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_ingridient_list(self):
        """Test retrieving a list of ingridients"""
        Ingridient.objects.create(user=self.user, name='tomato')
        Ingridient.objects.create(user=self.user, name='potato')

        res = self.client.get(INGRIDIENT_URL)

        ingridients = Ingridient.objects.all().order_by('-name')
        serializer = IngridientSerializer(ingridients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingridients_limited_to_user(self):
        """Test that ingridients for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@mail.com',
            'testpass'
        )
        Ingridient.objects.create(user=user2, name='ketchup')
        ingridient = Ingridient.objects.create(user=self.user, name='Turmeric')

        res = self.client.get(INGRIDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingridient.name)
