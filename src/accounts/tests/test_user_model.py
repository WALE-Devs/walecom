import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestCustomUserModel:
    """Tests for the CustomUser model."""
    
    def test_create_user_with_email(self):
        """Test creating a user with email."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
    
    def test_create_user_without_email_raises_error(self):
        """Test creating a user without email raises ValueError."""
        with pytest.raises(ValueError, match='The Email field must be set'):
            User.objects.create_user(email='', password='testpass123')
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        assert user.email == 'admin@example.com'
        assert user.is_active
        assert user.is_staff
        assert user.is_superuser
    
    def test_email_normalization(self):
        """Test email is normalized."""
        user = User.objects.create_user(
            email='test@EXAMPLE.COM',
            password='testpass123'
        )
        assert user.email == 'test@example.com'
    
    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        assert str(user) == 'test@example.com'
    
    def test_get_full_name(self):
        """Test get_full_name method."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        assert user.get_full_name() == 'John Doe'
    
    def test_get_full_name_fallback(self):
        """Test get_full_name returns email when names are empty."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        assert user.get_full_name() == 'test@example.com'
    
    def test_get_short_name(self):
        """Test get_short_name method."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John'
        )
        assert user.get_short_name() == 'John'
    
    def test_get_short_name_fallback(self):
        """Test get_short_name returns email username when first_name is empty."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        assert user.get_short_name() == 'test'
    
    def test_user_with_ecommerce_preferences(self):
        """Test user with e-commerce preferences."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            phone_number='+51987654321',
            newsletter_subscribed=True,
            preferred_language='en',
            preferred_currency='USD'
        )
        assert user.phone_number == '+51987654321'
        assert user.newsletter_subscribed is True
        assert user.preferred_language == 'en'
        assert user.preferred_currency == 'USD'
        assert user.phone_verified is False
        assert user.email_verified is False

    def test_phone_number_validation_invalid(self):
        """Test invalid phone number format."""
        from django.core.exceptions import ValidationError
        user = User.objects.create_user(email='phone@example.com', password='pass')
        user.phone_number = 'abc'
        with pytest.raises(ValidationError):
            user.full_clean()

    def test_phone_number_validation_valid(self):
        """Test valid phone number formats."""
        user = User.objects.create_user(email='phone-v@example.com', password='pass')
        valid_phones = ['+51987654321', '123456789', '+18005550199']
        for phone in valid_phones:
            user.phone_number = phone
            user.full_clean()  # Should not raise

    def test_age_calculation(self):
        """Test age property calculation."""
        from datetime import date
        today = date.today()
        # 20 years ago
        user = User(date_of_birth=date(today.year - 20, today.month, today.day))
        assert user.age == 20
        
        # Birthday tomorrow
        if today.month == 12 and today.day == 31: # Handle year end edge case for simplicity in test
            user.date_of_birth = date(today.year - 20, 1, 1)
        else:
            # Check if tomorrow exists in this month
            try:
                user.date_of_birth = date(today.year - 20, today.month, today.day + 1)
            except ValueError:
                # Next month
                user.date_of_birth = date(today.year - 20, today.month + 1, 1)
        
        assert user.age == 19

    def test_is_adult_logic(self):
        """Test is_adult property logic."""
        from datetime import date
        today = date.today()
        user_adult = User(date_of_birth=date(today.year - 18, today.month, today.day))
        assert user_adult.is_adult is True
        
        user_minor = User(date_of_birth=date(today.year - 17, today.month, today.day))
        assert user_minor.is_adult is False

    def test_email_normalization_on_clean(self):
        """Test email is normalized to lowercase in clean()."""
        user = User(email='TEST@Example.Com')
        user.clean()
        assert user.email == 'test@example.com'
