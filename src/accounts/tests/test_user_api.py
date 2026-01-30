import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistrationAPI:
    """Tests for user registration endpoint."""
    
    def setup_method(self):
        self.client = APIClient()
        self.url = '/api/auth/register/'
    
    def test_register_user_success(self):
        """Test successful user registration."""
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = self.client.post(self.url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['email'] == 'newuser@example.com'
        assert User.objects.filter(email='newuser@example.com').exists()
    
    def test_register_user_password_mismatch(self):
        """Test registration fails when passwords don't match."""
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password2': 'DifferentPass123!',
        }
        response = self.client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(email='newuser@example.com').exists()
    
    def test_register_user_duplicate_email(self):
        """Test registration fails with duplicate email."""
        User.objects.create_user(
            email='existing@example.com',
            password='password123'
        )
        
        data = {
            'email': 'existing@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = self.client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserProfileAPI:
    """Tests for user profile endpoint."""
    
    def setup_method(self):
        self.client = APIClient()
        self.url = '/api/auth/profile/'
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
    
    def test_get_profile_authenticated(self):
        """Test authenticated user can get their profile."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'testuser@example.com'
        assert response.data['first_name'] == 'John'
        assert response.data['full_name'] == 'John Doe'
    
    def test_get_profile_unauthenticated(self):
        """Test unauthenticated user cannot access profile."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile(self):
        """Test user can update their profile."""
        self.client.force_authenticate(user=self.user)
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone_number': '+51987654321',
            'newsletter_subscribed': True
        }
        response = self.client.patch(self.url, data)
        
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.first_name == 'Jane'
        assert self.user.last_name == 'Smith'
        assert self.user.phone_number == '+51987654321'
        assert self.user.newsletter_subscribed is True
    
    def test_cannot_update_email(self):
        """Test user cannot change their email via profile update."""
        self.client.force_authenticate(user=self.user)
        original_email = self.user.email
        data = {'email': 'newemail@example.com'}
        response = self.client.patch(self.url, data)
        
        self.user.refresh_from_db()
        assert self.user.email == original_email


@pytest.mark.django_db
class TestChangePasswordAPI:
    """Tests for password change endpoint."""
    
    def setup_method(self):
        self.client = APIClient()
        self.url = '/api/auth/change-password/'
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='oldpass123'
        )
    
    def test_change_password_success(self):
        """Test successful password change."""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpass123',
            'new_password': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        }
        response = self.client.post(self.url, data)
        
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.check_password('NewSecurePass123!')
    
    def test_change_password_wrong_old_password(self):
        """Test password change fails with wrong old password."""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'wrongpass',
            'new_password': 'NewSecurePass123!',
            'new_password2': 'NewSecurePass123!'
        }
        response = self.client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_change_password_mismatch(self):
        """Test password change fails when new passwords don't match."""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpass123',
            'new_password': 'NewSecurePass123!',
            'new_password2': 'DifferentPass123!'
        }
        response = self.client.post(self.url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
