from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from ..forms import CustomUserRegistrationForm, CustomAuthenticationForm
from ..models import User


class CustomRegistrationView(CreateView):
    model = User
    form_class = CustomUserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:dashboard')

    def form_valid(self, form):
        # Save the user
        user = form.save()
        print('DEBUG: User saved:', user)
        # Log the user in automatically
        from django.contrib.auth import login, authenticate
        password = form.cleaned_data['password1']
        user_auth = authenticate(username=user.username, password=password)
        print('DEBUG: Authenticated user:', user_auth)
        if user_auth:
            login(self.request, user_auth)
            messages.success(self.request, 'Registration successful! Welcome to CrowdFund!')
        else:
            print('DEBUG: Authentication failed after registration.')
        # Always redirect to dashboard after registration
        return redirect('accounts:dashboard')


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        # Always redirect to dashboard after login
        return reverse_lazy('accounts:dashboard')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('accounts:dashboard')


@login_required
def profile_view(request):
    context = {
        'user': request.user,
        'title': 'Profile'
    }
    return render(request, 'accounts/profile.html', context)
