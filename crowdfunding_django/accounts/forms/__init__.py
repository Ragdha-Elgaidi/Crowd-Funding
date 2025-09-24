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

from .project_forms import (
    ProjectForm,
    ProjectSearchForm,
    ProjectFilterForm,
    ContributionForm
)

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