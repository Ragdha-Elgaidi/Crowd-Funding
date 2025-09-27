from django.contrib import admin
from .models import Project, ProjectContribution


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'total_target', 'current_funding', 'is_active', 'created_at']
    search_fields = ['title', 'owner__email', 'owner__first_name', 'owner__last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'current_funding']


@admin.register(ProjectContribution)
class ProjectContributionAdmin(admin.ModelAdmin):
    list_display = ['project', 'contributor', 'amount', 'contributed_at']
    search_fields = ['project__title', 'contributor__email']
    ordering = ['-contributed_at']
    readonly_fields = ['contributed_at']
