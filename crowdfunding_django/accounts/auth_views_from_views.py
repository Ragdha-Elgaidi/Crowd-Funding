"""
Temporary copy of auth_views to move it out of the views/ subpackage.
"""

from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.utils import timezone

from .forms import (
    EnhancedUserRegistrationForm,
    EnhancedAuthenticationForm,
    UserProfileForm
)
from .models import User


@method_decorator([csrf_protect, never_cache], name='dispatch')
class EnhancedRegistrationView(CreateView):
    model = User
    form_class = EnhancedUserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Create Your Account - CrowdFund',
            'breadcrumbs': [
                {'title': 'Register', 'url': None}
            ],
            'form_title': 'Create Your Account',
            'form_description': 'Join our community and start funding amazing projects.',
            'submit_text': 'Create Account',
            'show_cancel': True,
            'cancel_url': reverse_lazy('accounts:login'),
            'ajax_form': True
        })
        return context

    def form_valid(self, form):
        user = form.save()
        username = user.username
        password = form.cleaned_data['password1']
        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
            messages.success(self.request, f'Welcome to CrowdFund, {user.get_full_name()}! Your account has been created successfully.')
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Account created successfully!', 'redirect_url': str(self.success_url)})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {field: list(errs) for field, errs in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors, 'message': 'Please correct the errors below.'})
        messages.error(self.request, 'Please correct the errors below and try again.')
        return super().form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You are already logged in.')
            return redirect('projects:home')
        return super().dispatch(request, *args, **kwargs)


@method_decorator([csrf_protect, never_cache], name='dispatch')
class EnhancedLoginView(LoginView):
    form_class = EnhancedAuthenticationForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('accounts:dashboard')
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'Login - CrowdFund', 'breadcrumbs': [{'title': 'Login', 'url': None}], 'form_title': 'Welcome Back', 'form_description': 'Sign in to your account to continue.', 'submit_text': 'Sign In', 'show_cancel': False, 'ajax_form': True})
        return context

    def form_valid(self, form):
        user = form.get_user()
        remember_me = form.cleaned_data.get('remember_me', False)
        if remember_me:
            self.request.session.set_expiry(30 * 24 * 60 * 60)
        else:
            self.request.session.set_expiry(0)
        messages.success(self.request, f'Welcome back, {user.get_full_name()}!')
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Login successful!', 'redirect_url': str(self.get_success_url())})
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Invalid email or password. Please try again.', 'errors': {'__all__': ['Invalid email or password.']}})
        messages.error(self.request, 'Invalid email or password. Please try again.')
        return super().form_invalid(form)

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return self.success_url


class EnhancedLogoutView(LogoutView):
    next_page = reverse_lazy('projects:home')
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You have been successfully logged out. Thank you for using CrowdFund!')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    login_url = reverse_lazy('accounts:login')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_projects = user.owned_projects.all()
        user_contributions = user.contributions.all()
        total_projects = user_projects.count()
        total_raised = sum(project.current_funding for project in user_projects)
        total_contributed = sum(contribution.amount for contribution in user_contributions)
        active_projects = user_projects.filter(is_active=True, start_date__lte=timezone.now().date(), end_date__gte=timezone.now().date()).count()
        context.update({'title': f'{user.get_full_name()} - Profile','breadcrumbs':[{'title':'Profile','url':None}],'statistics':{'total_projects':total_projects,'active_projects':active_projects,'total_raised':total_raised,'total_contributed':total_contributed,'success_rate':round((active_projects / max(total_projects, 1)) * 100, 1)},'recent_projects':user_projects[:5],'recent_contributions':user_contributions[:5]})
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('accounts:profile')
    login_url = reverse_lazy('accounts:login')
    def get_object(self):
        return self.request.user
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title':'Update Profile - CrowdFund','breadcrumbs':[{'title':'Profile','url':reverse_lazy('accounts:profile')},{'title':'Update','url':None}],'form_title':'Update Your Profile','form_description':'Keep your profile information up to date.','submit_text':'Save Changes','show_cancel':True,'cancel_url':reverse_lazy('accounts:profile'),'ajax_form':True})
        return context
    def form_valid(self, form):
        messages.success(self.request,'Your profile has been updated successfully!')
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success':True,'message':'Profile updated successfully!','redirect_url':str(self.success_url)})
        return super().form_valid(form)
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {field: list(errs) for field, errs in form.errors.items()}
            return JsonResponse({'success':False,'errors':errors,'message':'Please correct the errors below.'})
        messages.error(self.request,'Please correct the errors below and try again.')
        return super().form_invalid(form)
