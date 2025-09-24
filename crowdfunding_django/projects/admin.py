from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Project, ProjectContribution


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin interface for Project model
    """
    
    list_display = [
        'title', 'owner', 'total_target', 'current_funding', 
        'funding_percentage_display', 'campaign_status', 
        'start_date', 'end_date', 'is_active', 'created_at'
    ]
    
    list_filter = [
        'is_active', 'start_date', 'end_date', 'created_at',
        'total_target'
    ]
    
    search_fields = [
        'title', 'details', 'owner__first_name', 
        'owner__last_name', 'owner__email'
    ]
    
    ordering = ['-created_at']
    
    readonly_fields = [
        'created_at', 'updated_at', 'current_funding', 
        'funding_percentage_display', 'days_left_display',
        'campaign_status_display'
    ]
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('title', 'details', 'image')
        }),
        ('Financial Details', {
            'fields': ('total_target', 'current_funding')
        }),
        ('Campaign Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Owner & Status', {
            'fields': ('owner', 'is_active')
        }),
        ('Statistics', {
            'fields': (
                'funding_percentage_display', 
                'days_left_display',
                'campaign_status_display'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    ]
    
    def funding_percentage_display(self, obj):
        """Display funding percentage with progress bar"""
        percentage = obj.funding_percentage
        color = 'success' if percentage >= 100 else 'info' if percentage >= 50 else 'warning'
        return format_html(
            '<div class="progress" style="width: 100px;">'
            '<div class="progress-bar bg-{}" style="width: {}%;">{:.1f}%</div>'
            '</div>',
            color, min(percentage, 100), percentage
        )
    funding_percentage_display.short_description = 'Funding Progress'
    
    def days_left_display(self, obj):
        """Display days left with color coding"""
        days = obj.days_left
        if days > 30:
            color = 'green'
        elif days > 7:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} days</span>',
            color, days
        )
    days_left_display.short_description = 'Days Left'
    
    def campaign_status_display(self, obj):
        """Display campaign status with badge"""
        status = obj.campaign_status
        color_map = {
            'Active': 'success',
            'Upcoming': 'info',
            'Ended': 'secondary',
            'Inactive': 'danger'
        }
        color = color_map.get(status, 'secondary')
        
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, status
        )
    campaign_status_display.short_description = 'Status'
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('owner')
    
    actions = ['activate_projects', 'deactivate_projects']
    
    def activate_projects(self, request, queryset):
        """Bulk activate projects"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} projects activated.')
    activate_projects.short_description = "Activate selected projects"
    
    def deactivate_projects(self, request, queryset):
        """Bulk deactivate projects"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} projects deactivated.')
    deactivate_projects.short_description = "Deactivate selected projects"


@admin.register(ProjectContribution)
class ProjectContributionAdmin(admin.ModelAdmin):
    """
    Admin interface for ProjectContribution model
    """
    
    list_display = [
        'project_link', 'contributor_link', 'amount', 
        'contributed_at', 'has_message'
    ]
    
    list_filter = [
        'contributed_at', 'amount', 'project__title'
    ]
    
    search_fields = [
        'project__title', 'contributor__first_name', 
        'contributor__last_name', 'contributor__email',
        'message'
    ]
    
    ordering = ['-contributed_at']
    
    readonly_fields = ['contributed_at']
    
    fieldsets = [
        ('Contribution Details', {
            'fields': ('project', 'contributor', 'amount')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Timestamp', {
            'fields': ('contributed_at',)
        })
    ]
    
    def project_link(self, obj):
        """Link to project admin page"""
        url = reverse('admin:projects_project_change', args=[obj.project.pk])
        return format_html('<a href="{}">{}</a>', url, obj.project.title)
    project_link.short_description = 'Project'
    
    def contributor_link(self, obj):
        """Link to user admin page"""
        url = reverse('admin:accounts_user_change', args=[obj.contributor.pk])
        return format_html('<a href="{}">{}</a>', url, obj.contributor.get_full_name())
    contributor_link.short_description = 'Contributor'
    
    def has_message(self, obj):
        """Show if contribution has a message"""
        return bool(obj.message)
    has_message.boolean = True
    has_message.short_description = 'Has Message'
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('project', 'contributor')
