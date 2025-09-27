"""
Modular Forms System for CrowdFunding Platform

This module provides enhanced form classes that integrate with our modular
template components and provide consistent validation and styling.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
import re

User = get_user_model()


class BaseForm(forms.Form):
    """
    Base form class with common functionality for all forms.
    """
    
    def __init__(self, *args, **kwargs):
        self.ajax_form = kwargs.pop('ajax_form', False)
        super().__init__(*args, **kwargs)
        self.add_form_classes()
    
    def add_form_classes(self):
        """Add consistent CSS classes to form fields"""
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, 
                                       forms.PasswordInput, forms.NumberInput,
                                       forms.URLInput, forms.DateInput)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'file-input'})
    
    def add_error_class(self, field_name):
        """Add error class to field widget"""
        if field_name in self.fields:
            current_classes = self.fields[field_name].widget.attrs.get('class', '')
            if 'is-invalid' not in current_classes:
                self.fields[field_name].widget.attrs['class'] = f"{current_classes} is-invalid".strip()


class BaseModelForm(forms.ModelForm, BaseForm):
    """
    Base model form class with common functionality.
    """
    pass


class EnhancedUserRegistrationForm(UserCreationForm, BaseForm):
    """
    Enhanced user registration form with all required fields and validation.
    """
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your first name',
            'autocomplete': 'given-name'
        }),
        help_text="Your first name as it should appear on your profile."
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your last name',
            'autocomplete': 'family-name'
        }),
        help_text="Your last name as it should appear on your profile."
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        }),
        help_text="We'll use this email for login and important notifications."
    )
    
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your mobile number (e.g., 01012345678)',
            'autocomplete': 'tel',
            'pattern': r'^(\+201|01|1)[0125][0-9]{8}$',
            'data-custom-validation': 'validateEgyptianPhone'
        }),
        help_text="Egyptian mobile number starting with 010, 011, 012, or 015."
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password',
            'minlength': '8'
        }),
        help_text="Password must be at least 8 characters long and contain letters and numbers."
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        }),
        help_text="Enter the same password as before for verification."
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        label="I accept the Terms of Service and Privacy Policy",
        error_messages={
            'required': 'You must accept the terms and conditions to register.'
        }
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field since we use email
        if 'username' in self.fields:
            del self.fields['username']
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            if User.objects.filter(email=email).exists():
                self.add_error('email', "An account with this email already exists.")
        return email
    
    def clean_phone_number(self):
        """Validate Egyptian phone number format"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
            patterns = [
                r'^\+201[0125][0-9]{8}$',
                r'^01[0125][0-9]{8}$',
                r'^1[0125][0-9]{8}$'
            ]
            valid = any(re.match(pattern, phone_clean) for pattern in patterns)
            if not valid:
                self.add_error('phone_number', "Enter a valid Egyptian mobile number. Examples: 01012345678, +201012345678")
            elif User.objects.filter(phone_number=phone_clean).exists():
                self.add_error('phone_number', "An account with this phone number already exists.")
            return phone_clean
        return phone
    
    def clean_password2(self):
        """Validate password confirmation and aggregate errors"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        errors = []
        if password1 and password2:
            if password1 != password2:
                errors.append("The two password fields didn't match.")
            if len(password1) < 8:
                errors.append("Password must be at least 8 characters long.")
            if password1.isdigit():
                errors.append("Password cannot be entirely numeric.")
            if password1.lower() in ['password', '12345678', 'qwerty']:
                errors.append("Password is too common.")
        if errors:
            self.add_error('password2', errors)
        return password2
    
    def save(self, commit=True):
        """Save user with email as username"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower().strip()
        user.username = user.email  # Use email as username
        user.first_name = self.cleaned_data['first_name'].strip()
        user.last_name = self.cleaned_data['last_name'].strip()
        user.phone_number = self.cleaned_data['phone_number']
        
        if commit:
            user.save()
        return user


class EnhancedAuthenticationForm(AuthenticationForm, BaseForm):
    """
    Enhanced login form with email authentication and better UX.
    """
    
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
            'autofocus': True
        }),
        help_text="Enter the email address you used to register."
    )
    
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        }),
        help_text="Enter your account password."
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(),
        label="Remember me on this device",
        help_text="Keep me logged in for 30 days."
    )
    
    def clean_username(self):
        """Allow login with email"""
        email = self.cleaned_data.get('username')
        if email:
            email = email.lower().strip()
            try:
                user = User.objects.get(email=email)
                return user.username
            except User.DoesNotExist:
                raise ValidationError("No account found with this email address.")
        return email


class UserProfileForm(BaseModelForm):
    """
    Form for updating user profile information.
    """
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First name',
                'autocomplete': 'given-name'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last name',
                'autocomplete': 'family-name'
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Egyptian mobile number',
                'autocomplete': 'tel',
                'pattern': r'^(\+201|01|1)[0125][0-9]{8}$'
            })
        }
        help_texts = {
            'first_name': 'Your first name as it appears on your profile',
            'last_name': 'Your last name as it appears on your profile',
            'phone_number': 'Egyptian mobile number for account verification'
        }
    
    def clean_phone_number(self):
        """Validate Egyptian phone number format"""
        phone = self.cleaned_data.get('phone_number')
        
        if phone:
            # Remove spaces, dashes, and parentheses
            phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
            
            # Egyptian mobile patterns
            patterns = [
                r'^\+201[0125][0-9]{8}$',  # +201xxxxxxxxx
                r'^01[0125][0-9]{8}$',     # 01xxxxxxxxx
                r'^1[0125][0-9]{8}$'       # 1xxxxxxxxx
            ]
            
            if not any(re.match(pattern, phone_clean) for pattern in patterns):
                raise ValidationError(
                    "Enter a valid Egyptian mobile number (e.g., 01012345678)"
                )
            
            # Check if phone number already exists for other users
            existing_user = User.objects.filter(phone_number=phone_clean).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise ValidationError("An account with this phone number already exists.")
        
        return phone_clean


# Custom validation functions for JavaScript integration
def validate_egyptian_phone(phone_value, field):
    """
    Custom JavaScript validation function for Egyptian phone numbers.
    This is called from the form_field.html JavaScript.
    """
    errors = []
    
    if not phone_value:
        return errors
    
    # Remove spaces, dashes, and parentheses
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone_value)
    
    # Egyptian mobile patterns
    patterns = [
        r'^\+201[0125][0-9]{8}$',  # +201xxxxxxxxx
        r'^01[0125][0-9]{8}$',     # 01xxxxxxxxx
        r'^1[0125][0-9]{8}$'       # 1xxxxxxxxx
    ]
    
    if not any(re.match(pattern, phone_clean) for pattern in patterns):
        errors.append("Enter a valid Egyptian mobile number (e.g., 01012345678)")
    
    return errors


# Make validation function available to JavaScript
import json
from django.utils.safestring import mark_safe

def get_validation_functions():
    """Return validation functions for JavaScript"""
    return mark_safe(json.dumps({
        'validateEgyptianPhone': 'validateEgyptianPhone'
    }))