from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('projects/', views.project_list_view, name='list'),
    path('projects/create/', views.project_create_view, name='create'),
    path('projects/<int:pk>/', views.project_detail_view, name='detail'),
    path('projects/<int:pk>/edit/', views.project_update_view, name='edit'),
    path('projects/<int:pk>/delete/', views.project_delete_view, name='delete'),
    path('projects/<int:pk>/contribute/', views.contribute_to_project, name='contribute'),
    path('my-projects/', views.my_projects_view, name='my_projects'),
    path('my-contributions/', views.my_contributions_view, name='my_contributions'),
]
