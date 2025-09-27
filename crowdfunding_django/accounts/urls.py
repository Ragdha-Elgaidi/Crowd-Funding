from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication Views - using existing structure for now
    path('register/', views.CustomRegistrationView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.profile_view, name='dashboard'),  # Consolidated with profile view
]