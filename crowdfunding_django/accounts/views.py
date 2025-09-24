"""
Simplified views module - imports from modular views system

This module provides the main views while using the enhanced modular architecture.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .forms import CustomUserRegistrationForm, CustomAuthenticationForm, UserProfileForm
from .models import User

# Import enhanced views for use
try:
    from .views.auth_views import (
        EnhancedRegistrationView,
        EnhancedLoginView,
        ProfileView,
        ProfileUpdateView
    )
    # Use enhanced views as the main views
    CustomRegistrationView = EnhancedRegistrationView
    CustomLoginView = EnhancedLoginView
except ImportError:
    # Fallback to basic views if enhanced views aren't available
    class CustomRegistrationView(CreateView):
        """Basic registration view"""
        model = User
        form_class = CustomUserRegistrationForm
        template_name = 'accounts/register.html'
        success_url = reverse_lazy('accounts:login')
        
        def form_valid(self, form):
            response = super().form_valid(form)
            messages.success(self.request, 'Registration successful!')
            return response

    class CustomLoginView(LoginView):
        """Basic login view"""
        form_class = CustomAuthenticationForm
        template_name = 'accounts/login.html'
        redirect_authenticated_user = True
        
        def get_success_url(self):
            return reverse_lazy('projects:dashboard')


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('projects:home')


@login_required
def profile_view(request):
    """Basic profile view"""
    context = {
        'user': request.user,
        'title': 'Profile - Crowdfunding Platform'
    }
    return render(request, 'accounts/profile.html', context)


@login_required  
def dashboard_view(request):
    """User dashboard"""
    return redirect('accounts:profile')
