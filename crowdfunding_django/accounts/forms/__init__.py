"""
Forms package for the accounts app.

This package contains modular form classes for authentication and project management.
"""

# Import all forms to make them available from the package
from .auth_forms import (
    BaseForm,
    BaseModelForm,
    EnhancedUserRegistrationForm,
    EnhancedAuthenticationForm,
    UserProfileForm,
    validate_egyptian_phone,
    get_validation_functions
)

# Stub implementations to avoid importing from problematic project_forms.py
from django import forms
from django.forms import ModelForm
from projects.models import Project, ProjectContribution

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "details",
            "total_target",
            "start_date",
            "end_date",
            "image",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "details": forms.Textarea(attrs={"rows": 5}),
        }

class ProjectSearchForm(forms.Form):
    query = forms.CharField(required=False, max_length=200)
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))

class ProjectFilterForm(forms.Form):
    STATUS_CHOICES = (
        ("all", "All"),
        ("active", "Active"),
        ("upcoming", "Upcoming"),
        ("ended", "Ended"),
    )
    status = forms.ChoiceField(required=False, choices=STATUS_CHOICES)

class ContributionForm(ModelForm):
    class Meta:
        model = ProjectContribution
        fields = ["project", "amount", "message"]
        widgets = {"project": forms.HiddenInput()}

# Backward compatibility aliases
CustomUserRegistrationForm = EnhancedUserRegistrationForm
CustomAuthenticationForm = EnhancedAuthenticationForm

__all__ = [
    'BaseForm',
    'BaseModelForm',
    'EnhancedUserRegistrationForm',
    'EnhancedAuthenticationForm',
    'UserProfileForm',
    'ProjectForm',
    'ProjectSearchForm',
    'ProjectFilterForm',
    'ContributionForm',
    'CustomUserRegistrationForm',  # Backward compatibility
    'CustomAuthenticationForm',    # Backward compatibility
    'validate_egyptian_phone',
    'get_validation_functions'
]