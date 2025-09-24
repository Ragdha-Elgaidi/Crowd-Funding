"""
Project views using modular base classes and mixins.

This module contains all project-related views built using the
modular view system for better code reuse and maintainability.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from .base import (
    BaseListView, BaseDetailView, BaseCreateView, 
    BaseUpdateView, BaseDeleteView, BaseDashboardView,
    StatisticsMixin, AjaxResponseMixin
)
from ..models import Project, ProjectContribution
from ..forms import ProjectForm, ProjectSearchForm, ContributionForm, ProjectFilterForm


# Home and Dashboard Views

class HomeView(StatisticsMixin, TemplateView):
    """
    Homepage showing featured projects and platform statistics.
    """
    template_name = 'projects/home.html'
    title = 'Crowdfunding Platform - Fund Your Dreams'
    
    def get_featured_projects(self):
        """Get featured projects for homepage."""
        return Project.objects.filter(
            is_active=True,
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).order_by('-created_at')[:6]
    
    def get_statistics(self):
        """Get platform statistics."""
        return {
            'total_projects': Project.objects.filter(is_active=True).count(),
            'total_funding': Project.objects.filter(is_active=True).aggregate(
                total=Sum('current_funding')
            )['total'] or 0,
            'active_projects': Project.objects.filter(
                is_active=True,
                start_date__lte=timezone.now().date(),
                end_date__gte=timezone.now().date()
            ).count()
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_projects'] = self.get_featured_projects()
        return context


class DashboardView(BaseDashboardView):
    """
    User dashboard showing their projects and contributions.
    """
    template_name = 'projects/dashboard.html'
    title = 'Dashboard - Crowdfunding Platform'
    
    breadcrumbs = [
        {'title': 'Dashboard', 'icon': 'fas fa-tachometer-alt'}
    ]
    
    def get_user_projects(self):
        """Get user's projects."""
        return Project.objects.filter(
            owner=self.request.user
        ).order_by('-created_at')
    
    def get_user_contributions(self):
        """Get user's contributions."""
        return ProjectContribution.objects.filter(
            contributor=self.request.user
        ).order_by('-contributed_at')[:5]
    
    def get_statistics(self):
        """Get user-specific statistics."""
        user_projects = self.get_user_projects()
        user_contributions = self.get_user_contributions()
        
        return {
            'total_projects_created': user_projects.count(),
            'total_funding_raised': user_projects.aggregate(
                total=Sum('current_funding')
            )['total'] or 0,
            'total_contributed': user_contributions.aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'active_projects': user_projects.filter(
                is_active=True,
                end_date__gte=timezone.now().date()
            ).count()
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user_projects': self.get_user_projects()[:5],  # Recent 5
            'user_contributions': self.get_user_contributions(),
        })
        return context


# Project List and Detail Views

class ProjectListView(BaseListView):
    """
    List all projects with advanced filtering, searching, and sorting.
    """
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    title = 'Browse Projects - Crowdfunding Platform'
    
    # Search configuration
    search_fields = ['title', 'details']
    
    # Sorting configuration
    allowed_sort_fields = [
        '-created_at', 'created_at',
        '-total_target', 'total_target',
        '-current_funding', 'current_funding',
        'title', '-title',
        'end_date', '-end_date'
    ]
    default_sort = '-created_at'
    
    # Pagination configuration
    paginate_by = 12
    
    breadcrumbs = [
        {'title': 'Projects', 'icon': 'fas fa-list'}
    ]
    
    def get_queryset(self):
        """Get filtered and sorted project queryset."""
        queryset = Project.objects.filter(is_active=True)
        
        # Apply search, filter, and sort from mixins
        queryset = super().get_queryset()
        
        # Custom filters from forms
        queryset = self.apply_form_filters(queryset)
        
        return queryset.distinct()
    
    def apply_form_filters(self, queryset):
        """Apply filters from search and filter forms."""
        # Search form filters
        search_form = ProjectSearchForm(self.request.GET)
        if search_form.is_valid():
            status_filter = search_form.cleaned_data.get('status_filter')
            date_search = search_form.cleaned_data.get('date_search')
            min_target = search_form.cleaned_data.get('min_target')
            max_target = search_form.cleaned_data.get('max_target')
            
            # Status filter
            today = timezone.now().date()
            if status_filter == 'active':
                queryset = queryset.filter(
                    start_date__lte=today,
                    end_date__gte=today
                )
            elif status_filter == 'upcoming':
                queryset = queryset.filter(start_date__gt=today)
            elif status_filter == 'ended':
                queryset = queryset.filter(end_date__lt=today)
            
            # Date search
            if date_search:
                queryset = queryset.filter(
                    start_date__lte=date_search,
                    end_date__gte=date_search
                )
            
            # Target amount filters
            if min_target:
                queryset = queryset.filter(total_target__gte=min_target)
            if max_target:
                queryset = queryset.filter(total_target__lte=max_target)
        
        # Filter form
        filter_form = ProjectFilterForm(self.request.GET)
        if filter_form.is_valid():
            owner_name = filter_form.cleaned_data.get('owner_name')
            
            if owner_name:
                queryset = queryset.filter(
                    Q(owner__first_name__icontains=owner_name) |
                    Q(owner__last_name__icontains=owner_name)
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'search_form': ProjectSearchForm(self.request.GET),
            'filter_form': ProjectFilterForm(self.request.GET),
        })
        return context


class ProjectDetailView(BaseDetailView):
    """
    Display project details with contribution functionality.
    """
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    
    def get_title(self):
        return f'{self.get_object().title} - Crowdfunding Platform'
    
    def get_breadcrumbs(self):
        project = self.get_object()
        return [
            {'title': 'Projects', 'url': reverse_lazy('projects:list'), 'icon': 'fas fa-list'},
            {'title': project.title[:30], 'icon': 'fas fa-eye'}
        ]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        context.update({
            'title': self.get_title(),
            'breadcrumbs': self.get_breadcrumbs(),
            'contribution_form': ContributionForm(),
            'recent_contributions': project.contributions.order_by('-contributed_at')[:5],
            'funding_percentage': project.funding_percentage,
            'days_left': project.days_left,
        })
        return context


# Project CRUD Views

class ProjectCreateView(BaseCreateView):
    """
    Create a new project.
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_message = "Project '{title}' created successfully!"
    title = 'Create Project - Crowdfunding Platform'
    
    breadcrumbs = [
        {'title': 'Projects', 'url': reverse_lazy('projects:list'), 'icon': 'fas fa-list'},
        {'title': 'Create Project', 'icon': 'fas fa-plus'}
    ]
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})


class ProjectUpdateView(BaseUpdateView):
    """
    Update an existing project (owner only).
    """
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_message = "Project '{title}' updated successfully!"
    
    def get_title(self):
        return f'Edit {self.get_object().title} - Crowdfunding Platform'
    
    def get_breadcrumbs(self):
        project = self.get_object()
        return [
            {'title': 'Projects', 'url': reverse_lazy('projects:list'), 'icon': 'fas fa-list'},
            {'title': project.title[:20], 'url': reverse_lazy('projects:detail', kwargs={'pk': project.pk}), 'icon': 'fas fa-eye'},
            {'title': 'Edit', 'icon': 'fas fa-edit'}
        ]
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(BaseDeleteView):
    """
    Delete a project (owner only).
    """
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:dashboard')
    success_message = "Project deleted successfully!"
    
    def get_breadcrumbs(self):
        project = self.get_object()
        return [
            {'title': 'Projects', 'url': reverse_lazy('projects:list'), 'icon': 'fas fa-list'},
            {'title': project.title[:20], 'url': reverse_lazy('projects:detail', kwargs={'pk': project.pk}), 'icon': 'fas fa-eye'},
            {'title': 'Delete', 'icon': 'fas fa-trash'}
        ]


# User Project Views

class MyProjectsView(BaseListView):
    """
    List user's own projects.
    """
    model = Project
    template_name = 'projects/my_projects.html'
    context_object_name = 'projects'
    title = 'My Projects - Crowdfunding Platform'
    paginate_by = 10
    
    breadcrumbs = [
        {'title': 'My Projects', 'icon': 'fas fa-folder'}
    ]
    
    def get_queryset(self):
        return Project.objects.filter(
            owner=self.request.user
        ).order_by('-created_at')


class MyContributionsView(BaseListView):
    """
    List user's contributions.
    """
    model = ProjectContribution
    template_name = 'projects/my_contributions.html'
    context_object_name = 'contributions'
    title = 'My Contributions - Crowdfunding Platform'
    paginate_by = 15
    
    breadcrumbs = [
        {'title': 'My Contributions', 'icon': 'fas fa-heart'}
    ]
    
    def get_queryset(self):
        return ProjectContribution.objects.filter(
            contributor=self.request.user
        ).order_by('-contributed_at')


# AJAX Views

class ProjectContributeView(AjaxResponseMixin, TemplateView):
    """
    Handle project contributions via AJAX.
    """
    
    @method_decorator(login_required)
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, is_active=True)
        form = ContributionForm(request.POST)
        
        if form.is_valid():
            # Check if project is still accepting contributions
            if not project.is_accepting_contributions():
                return JsonResponse({
                    'success': False,
                    'message': 'This project is no longer accepting contributions.'
                })
            
            # Create contribution
            contribution = form.save(commit=False)
            contribution.contributor = request.user
            contribution.project = project
            contribution.save()
            
            # Update project funding
            project.current_funding += contribution.amount
            project.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Thank you for contributing ${contribution.amount}!',
                'new_funding': project.current_funding,
                'funding_percentage': project.funding_percentage,
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid contribution data.',
                'errors': form.errors
            })


# Function-based views for complex operations

@login_required
def project_search_ajax(request):
    """
    AJAX endpoint for project search with autocomplete.
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    projects = Project.objects.filter(
        Q(title__icontains=query) | Q(details__icontains=query),
        is_active=True
    )[:10]
    
    results = []
    for project in projects:
        results.append({
            'id': project.id,
            'title': project.title,
            'url': project.get_absolute_url(),
            'funding_percentage': project.funding_percentage,
            'days_left': project.days_left,
        })
    
    return JsonResponse({'results': results})


@require_POST
def toggle_project_status(request, pk):
    """
    Toggle project active status (AJAX).
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required'})
    
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    project.is_active = not project.is_active
    project.save()
    
    status = 'activated' if project.is_active else 'deactivated'
    
    return JsonResponse({
        'success': True,
        'message': f'Project {status} successfully!',
        'is_active': project.is_active
    })