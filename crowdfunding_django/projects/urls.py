from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Home and Dashboard
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Project List and Detail
    path('projects/', views.project_list_view, name='list'),
    path('projects/<int:pk>/', views.project_detail_view, name='detail'),
    
    # Project CRUD
    path('projects/create/', views.project_create_view, name='create'),
    path('projects/<int:pk>/edit/', views.project_update_view, name='edit'),
    path('projects/<int:pk>/delete/', views.project_delete_view, name='delete'),
    
    # User-specific views
    path('my-projects/', views.my_projects_view, name='my_projects'),
    
    # Contribution
    path('projects/<int:project_id>/contribute/', views.contribute_to_project, name='contribute'),
    
    # AJAX endpoints
    path('ajax/check-title/', views.ajax_check_title, name='check_title'),
    path('ajax/project/<int:project_id>/stats/', views.ajax_project_stats, name='project_stats'),
    path('ajax/search/', views.ajax_search_projects, name='search_projects'),
]