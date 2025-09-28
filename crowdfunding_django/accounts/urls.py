from django.urls import path
from .legacy_views import (
    CustomRegistrationView,
    CustomLoginView,
    logout_view,
    profile_view
)
from .auth_views import EnhancedRegistrationView, EnhancedLoginView

app_name = 'accounts'

urlpatterns = [
    # Authentication Views - using existing structure for now
    path('register/', EnhancedRegistrationView.as_view(), name='register'),
    path('login/', EnhancedLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('dashboard/', profile_view, name='dashboard'),  # Consolidated with profile view
]