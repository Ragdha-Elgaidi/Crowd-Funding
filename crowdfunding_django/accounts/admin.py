from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for User model
    """
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'phone_number', 'is_staff', 'is_active', 'date_joined'
    ]
    
    list_filter = [
        'is_staff', 'is_active', 'is_superuser', 
        'date_joined', 'last_login'
    ]
    
    search_fields = [
        'username', 'email', 'first_name', 'last_name', 'phone_number'
    ]
    
    ordering = ['-date_joined']
    
    # Fields to display in user detail view
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'is_email_verified')
        }),
    )
    
    # Fields to display when adding a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number')
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
