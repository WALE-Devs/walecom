from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import date
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for e-commerce platform.
    Uses email as the primary identifier instead of username.
    """
    
    # Authentication
    email = models.EmailField(unique=True, db_index=True)
    
    # Personal Information
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    date_of_birth = models.DateField(null=True, blank=True, help_text="For age verification and birthday promotions")
    
    # Contact Information
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        help_text="For order notifications and 2FA"
    )
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    
    # E-commerce Preferences
    newsletter_subscribed = models.BooleanField(default=False, help_text="Marketing emails consent")
    preferred_language = models.CharField(
        max_length=10,
        default='es',
        choices=[
            ('es', 'Español'),
            ('en', 'English'),
        ],
        help_text="Preferred language for communications"
    )
    preferred_currency = models.CharField(
        max_length=3,
        default='PEN',
        choices=[
            ('PEN', 'Peruvian Sol'),
            ('USD', 'US Dollar'),
        ],
        help_text="Preferred currency for pricing"
    )
    
    # Permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom manager
    objects = CustomUserManager()
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email is already required by USERNAME_FIELD
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['-date_joined']),
        ]
    
    def __str__(self):
        if self.first_name:
            return f"{self.first_name} ({self.email})"
        return self.email
    
    def clean(self):
        super().clean()
        if self.email:
            self.email = self.email.lower()

    @property
    def age(self):
        """
        Calculates the user's age based on date_of_birth.
        """
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def is_adult(self):
        """
        Checks if the user is 18 years or older.
        """
        age = self.age
        return age >= 18 if age is not None else False
    
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email
    
    def get_short_name(self):
        """
        Return the short name for the user.
        """
        return self.first_name or self.email.split('@')[0]
