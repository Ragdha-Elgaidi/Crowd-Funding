
"""Views for the crowdfunding projects application.

Minimal views for projects: home, list, detail, create, edit, delete, and contribute.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ContributionForm, ProjectForm
from .models import Project, ProjectContribution


from django.contrib import messages
def home_view(request):
    today = timezone.now().date()
    projects = (
        Project.objects.filter(is_active=True, start_date__lte=today, end_date__gte=today)
        .order_by('-created_at')[:6]
    )
    # Add a debug message to confirm message display
    messages.info(request, 'Debug: Home page loaded successfully. If you see this, messages are working.')
    return render(request, 'projects/home.html', {'featured_projects': projects})


def project_list_view(request):
    projects = Project.objects.filter(is_active=True).order_by('-created_at')
    paginator = Paginator(projects, 12)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'projects/project_list.html', {'projects': page_obj})


def project_detail_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    recent_contributions = project.contributions.select_related('contributor').order_by('-contributed_at')[:5]
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'contributions': recent_contributions,
        'contribution_form': ContributionForm(),
    })


@login_required
def project_create_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, 'Project created')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/project_create.html', {'form': form})


@login_required
def project_update_view(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated')
            return redirect('projects:detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_edit.html', {'form': form, 'project': project})


@login_required
def project_delete_view(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted')
        return redirect('projects:list')
    return render(request, 'projects/project_delete.html', {'project': project})


@login_required
def contribute_to_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, is_active=True)
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.project = project
            contribution.contributor = request.user
            contribution.save()
            messages.success(request, 'Thank you for your contribution')
    return redirect('projects:detail', pk=project.pk)


@login_required
def my_projects_view(request):
    """Display projects owned by the current user."""
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
    paginator = Paginator(projects, 12)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'projects/project_list.html', {
        'projects': page_obj,
        'is_my_projects': True,
        'page_title': 'My Projects'
    })


@login_required
def my_contributions_view(request):
    """Display projects the current user has contributed to."""
    contributions = ProjectContribution.objects.filter(contributor=request.user).select_related('project')
    projects = [contribution.project for contribution in contributions]
    paginator = Paginator(projects, 12)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'projects/project_list.html', {
        'projects': page_obj,
        'is_my_contributions': True,
        'page_title': 'My Contributions'
    })