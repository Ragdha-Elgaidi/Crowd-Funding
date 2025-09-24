from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    Includes Egyptian phone validation and additional fields
    """
    
    # Egyptian phone number validator
    phone_validator = RegexValidator(
        regex=r'^(\+201|01|1)[0125][0-9]{8}$',
        message="Enter a valid Egyptian mobile number (e.g., 01012345678)"
    )
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(
        max_length=15, 
        validators=[phone_validator],
        help_text="Egyptian mobile number (e.g., 01012345678)"
    )
    is_email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone_number']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def clean(self):
        """Custom validation for the User model"""
        super().clean()
        
        # Validate phone number format
        if self.phone_number:
            phone_patterns = [
                r'^\+201[0125][0-9]{8}$',  # +201xxxxxxxxx
                r'^01[0125][0-9]{8}$',     # 01xxxxxxxxx
                r'^1[0125][0-9]{8}$'       # 1xxxxxxxxx
            ]
            
            phone_clean = re.sub(r'[\s-]', '', self.phone_number)
            if not any(re.match(pattern, phone_clean) for pattern in phone_patterns):
                raise ValidationError({
                    'phone_number': 'Enter a valid Egyptian mobile number'
                })
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)
