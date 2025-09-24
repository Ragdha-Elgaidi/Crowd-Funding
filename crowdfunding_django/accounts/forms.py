"""
Simplified forms module - imports from modular forms system

This module provides backward compatibility while using the enhanced modular forms.
"""

# Import enhanced forms as the main forms
from .forms.auth_forms import (
    EnhancedUserRegistrationForm as CustomUserRegistrationForm,
    EnhancedAuthenticationForm as CustomAuthenticationForm,
    UserProfileForm
)

from .forms.project_forms import (
    ProjectForm,
    ProjectSearchForm,
    ProjectFilterForm,
    ContributionForm
)

# Make forms available at package level
__all__ = [
    'CustomUserRegistrationForm',
    'CustomAuthenticationForm', 
    'UserProfileForm',
    'ProjectForm',
    'ProjectSearchForm',
    'ProjectFilterForm',
    'ContributionForm'
]