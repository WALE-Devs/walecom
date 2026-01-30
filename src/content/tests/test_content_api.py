import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from content.models import Content, ContentBlock

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(username='admin', email='admin@test.com', password='password123')

@pytest.fixture
def normal_user(db):
    return User.objects.create_user(username='user', email='user@test.com', password='password123')

@pytest.mark.django_db
class TestContentAPI:
    def test_content_list_public(self, api_client):
        Content.objects.create(identifier='about', title='About', language='es')
        url = reverse('content-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_content_retrieve_public(self, api_client):
        content = Content.objects.create(identifier='terms', title='Terms', language='es')
        url = reverse('content-detail', kwargs={'identifier': 'terms'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Terms'

    def test_content_language_filtering(self, api_client):
        Content.objects.create(identifier='about', title='Sobre Nosotros', language='es')
        Content.objects.create(identifier='about', title='About Us', language='en')
        
        url = reverse('content-list')
        
        # Test Spanish
        response = api_client.get(f"{url}?lang=es")
        assert len(response.data) == 1
        assert response.data[0]['title'] == 'Sobre Nosotros'
        
        # Test English
        response = api_client.get(f"{url}?lang=en")
        assert len(response.data) == 1
        assert response.data[0]['title'] == 'About Us'

    def test_content_create_admin_only(self, api_client, admin_user, normal_user):
        url = reverse('content-list')
        data = {'identifier': 'new-page', 'title': 'New Page', 'language': 'es'}
        
        # Unauthorized (Anonymous)
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Normal User
        api_client.force_authenticate(user=normal_user)
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Admin User
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
class TestContentBlockAPI:
    def test_block_admin_only(self, api_client, admin_user):
        content = Content.objects.create(identifier='home', title='Home', language='es')
        url = reverse('contentblock-list')
        data = {
            'content': content.id,
            'identifier': 'intro',
            'title': 'Intro',
            'language': 'es'
        }
        
        # Public (Anonymous)
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Admin
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
