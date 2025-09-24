"""
Simplified projects views module - uses modular architecture

This module provides clean, streamlined views for the projects app.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Sum

from .models import Project, ProjectContribution
from .forms import ProjectForm, ProjectSearchForm, ContributionForm


def home_view(request):
    """Homepage showing featured projects"""
    featured_projects = Project.objects.filter(
        is_active=True,
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    ).order_by('-created_at')[:6]
    
    # Get statistics
    total_projects = Project.objects.filter(is_active=True).count()
    total_funding = Project.objects.filter(is_active=True).aggregate(
        total=Sum('current_funding')
    )['total'] or 0
    active_campaigns = Project.objects.filter(
        is_active=True,
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    ).count()
    
    context = {
        'featured_projects': featured_projects,
        'total_projects': total_projects,
        'total_funding': total_funding,
        'active_campaigns': active_campaigns,
        'title': 'Home - Crowdfunding Platform'
    }
    return render(request, 'projects/home.html', context)


@login_required
def dashboard_view(request):
    """User dashboard showing their projects"""
    user_projects = Project.objects.filter(creator=request.user).order_by('-created_at')
    
    context = {
        'user_projects': user_projects,
        'title': 'Dashboard - Crowdfunding Platform'
    }
    return render(request, 'projects/dashboard.html', context)


def project_list_view(request):
    """List all active projects with search and pagination"""
    projects = Project.objects.filter(is_active=True).order_by('-created_at')
    
    # Search functionality
    search_form = ProjectSearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        if query:
            projects = projects.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(category__icontains=query)
            )
    
    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'projects': page_obj,
        'search_form': search_form,
        'title': 'All Projects - Crowdfunding Platform'
    }
    return render(request, 'projects/project_list.html', context)


def project_detail_view(request, pk):
    """Detailed view of a single project"""
    project = get_object_or_404(Project, pk=pk, is_active=True)
    
    # Calculate progress
    progress_percentage = 0
    if project.target_amount > 0:
        progress_percentage = min((project.current_funding / project.target_amount) * 100, 100)
    
    # Get recent contributions
    recent_contributions = ProjectContribution.objects.filter(
        project=project
    ).order_by('-created_at')[:5]
    
    context = {
        'project': project,
        'progress_percentage': progress_percentage,
        'recent_contributions': recent_contributions,
        'contribution_form': ContributionForm(),
        'title': f'{project.title} - Crowdfunding Platform'
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_create_view(request):
    """Create a new project"""
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'title': 'Create Project - Crowdfunding Platform'
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def project_update_view(request, pk):
    """Update an existing project"""
    project = get_object_or_404(Project, pk=pk, creator=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'title': f'Edit {project.title} - Crowdfunding Platform'
    }
    return render(request, 'projects/project_form.html', context)


@login_required
def project_delete_view(request, pk):
    """Delete a project"""
    project = get_object_or_404(Project, pk=pk, creator=request.user)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('projects:dashboard')
    
    context = {
        'project': project,
        'title': f'Delete {project.title} - Crowdfunding Platform'
    }
    return render(request, 'projects/project_confirm_delete.html', context)


@login_required
def my_projects_view(request):
    """User's own projects"""
    projects = Project.objects.filter(creator=request.user).order_by('-created_at')
    
    context = {
        'projects': projects,
        'title': 'My Projects - Crowdfunding Platform'
    }
    return render(request, 'projects/my_projects.html', context)


@login_required
def contribute_to_project(request, project_id):
    """Handle project contributions"""
    project = get_object_or_404(Project, pk=project_id, is_active=True)
    
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.project = project
            contribution.contributor = request.user
            contribution.save()
            
            # Update project funding
            project.current_funding += contribution.amount
            project.save()
            
            messages.success(request, f'Thank you for contributing ${contribution.amount} to {project.title}!')
            return redirect('projects:project_detail', pk=project.pk)
    
    return redirect('projects:project_detail', pk=project.pk)


# AJAX Views
def ajax_check_title(request):
    """AJAX endpoint to check if project title is available"""
    title = request.GET.get('title', '')
    if title:
        exists = Project.objects.filter(title__iexact=title).exists()
        return JsonResponse({'available': not exists})
    return JsonResponse({'available': True})


def ajax_project_stats(request, project_id):
    """AJAX endpoint for project statistics"""
    try:
        project = Project.objects.get(pk=project_id, is_active=True)
        stats = {
            'current_funding': float(project.current_funding),
            'target_amount': float(project.target_amount),
            'progress_percentage': min((project.current_funding / project.target_amount) * 100, 100) if project.target_amount > 0 else 0,
            'contributor_count': ProjectContribution.objects.filter(project=project).count(),
            'days_remaining': (project.end_date - timezone.now().date()).days if project.end_date > timezone.now().date() else 0
        }
        return JsonResponse({'success': True, 'stats': stats})
    except Project.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Project not found'})


def ajax_search_projects(request):
    """AJAX endpoint for project search"""
    query = request.GET.get('q', '')
    projects = []
    
    if query:
        project_objects = Project.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            is_active=True
        )[:10]
        
        projects = [{
            'id': p.id,
            'title': p.title,
            'description': p.description[:100] + '...' if len(p.description) > 100 else p.description,
            'current_funding': float(p.current_funding),
            'target_amount': float(p.target_amount),
            'url': f'/projects/{p.id}/'
        } for p in project_objects]
    
    return JsonResponse({'projects': projects})
