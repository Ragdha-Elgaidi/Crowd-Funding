from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication Views - using existing structure for now
    path('register/', views.CustomRegistrationView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Additional profile management
    # path('profile/edit/', views.profile_update_view, name='profile_update'),
]