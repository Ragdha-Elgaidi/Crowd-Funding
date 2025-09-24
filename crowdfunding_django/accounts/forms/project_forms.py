"""
Project Forms Module

Enhanced forms for project management with validation and modular design.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from projects.models import Project, ProjectContribution
from .auth_forms import BaseModelForm, BaseForm


class ProjectForm(BaseModelForm):
    """
    Enhanced form for creating and editing projects.
    """
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter project title',
            'maxlength': 200
        }),
        help_text="A clear, descriptive title for your project (max 200 characters)."
    )
    
    details = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Describe your project in detail...',
            'rows': 6,
            'maxlength': 5000
        }),
        help_text="Detailed description of your project, goals, and how funds will be used (max 5000 characters)."
    )
    
    total_target = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=100,
        widget=forms.NumberInput(attrs={
            'placeholder': 'e.g., 250000.00',
            'step': '0.01',
            'min': '100'
        }),
        help_text="Target amount in Egyptian Pounds (minimum 100 EGP)."
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'placeholder': 'YYYY-MM-DD'
        }),
        help_text="When your fundraising campaign will start."
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'placeholder': 'YYYY-MM-DD'
        }),
        help_text="When your fundraising campaign will end."
    )
    
    featured_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'image/*'
        }),
        help_text="Upload a compelling image for your project (optional)."
    )
    
    class Meta:
        model = Project
        fields = ['title', 'details', 'total_target', 'start_date', 'end_date', 'featured_image']
    
    def clean_title(self):
        """Validate project title"""
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            
            # Check for minimum length
            if len(title) < 10:
                raise ValidationError("Project title must be at least 10 characters long.")
            
            # Check for inappropriate content (basic filter)
            inappropriate_words = ['scam', 'fake', 'fraud', 'illegal']
            if any(word in title.lower() for word in inappropriate_words):
                raise ValidationError("Project title contains inappropriate content.")
        
        return title
    
    def clean_details(self):
        """Validate project details"""
        details = self.cleaned_data.get('details')
        if details:
            details = details.strip()
            
            # Check for minimum length
            if len(details) < 50:
                raise ValidationError("Project description must be at least 50 characters long.")
            
            # Check for maximum length
            if len(details) > 5000:
                raise ValidationError("Project description cannot exceed 5000 characters.")
        
        return details
    
    def clean_total_target(self):
        """Validate target amount"""
        total_target = self.cleaned_data.get('total_target')
        
        if total_target:
            # Minimum amount validation
            if total_target < 100:
                raise ValidationError("Target amount must be at least 100 EGP.")
            
            # Maximum amount validation (reasonable limit)
            if total_target > 10000000:  # 10 million EGP
                raise ValidationError("Target amount cannot exceed 10,000,000 EGP.")
        
        return total_target
    
    def clean_start_date(self):
        """Validate start date"""
        start_date = self.cleaned_data.get('start_date')
        
        if start_date:
            today = date.today()
            
            # For new projects, start date should not be in the past
            if not self.instance.pk and start_date < today:
                raise ValidationError("Start date cannot be in the past.")
            
            # Start date should not be too far in the future
            max_future_date = today + timedelta(days=365)  # 1 year
            if start_date > max_future_date:
                raise ValidationError("Start date cannot be more than 1 year in the future.")
        
        return start_date
    
    def clean_end_date(self):
        """Validate end date"""
        end_date = self.cleaned_data.get('end_date')
        
        if end_date:
            today = date.today()
            
            # End date should not be in the past
            if end_date < today:
                raise ValidationError("End date cannot be in the past.")
            
            # End date should not be too far in the future
            max_future_date = today + timedelta(days=730)  # 2 years
            if end_date > max_future_date:
                raise ValidationError("End date cannot be more than 2 years in the future.")
        
        return end_date
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            # End date must be after start date
            if end_date <= start_date:
                raise ValidationError({
                    'end_date': 'End date must be after start date.'
                })
            
            # Campaign duration validation
            duration = (end_date - start_date).days
            
            # Minimum campaign duration
            if duration < 7:  # 1 week
                raise ValidationError({
                    'end_date': 'Campaign must run for at least 1 week.'
                })
            
            # Maximum campaign duration
            if duration > 365:  # 1 year
                raise ValidationError({
                    'end_date': 'Campaign cannot run for more than 1 year.'
                })
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save project with additional processing"""
        project = super().save(commit=False)
        
        # Clean and process text fields
        project.title = project.title.strip()
        project.details = project.details.strip()
        
        if commit:
            project.save()
        
        return project


class ProjectSearchForm(BaseForm):
    """
    Form for searching and filtering projects.
    """
    
    search_query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search projects by title or description...',
            'class': 'form-control search-input'
        }),
        label='Search'
    )
    
    status_filter = forms.ChoiceField(
        choices=[
            ('', 'All Projects'),
            ('active', 'Active Campaigns'),
            ('upcoming', 'Upcoming Campaigns'),
            ('ended', 'Ended Campaigns'),
            ('successful', 'Successfully Funded'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Status'
    )
    
    date_search = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='Active on Date',
        help_text='Find projects that were active on a specific date'
    )
    
    min_target = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Minimum amount',
            'step': '0.01',
            'class': 'form-control'
        }),
        label='Min Target (EGP)'
    )
    
    max_target = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Maximum amount',
            'step': '0.01',
            'class': 'form-control'
        }),
        label='Max Target (EGP)'
    )
    
    def clean(self):
        """Validate search form"""
        cleaned_data = super().clean()
        min_target = cleaned_data.get('min_target')
        max_target = cleaned_data.get('max_target')
        
        if min_target and max_target:
            if min_target > max_target:
                raise ValidationError({
                    'max_target': 'Maximum target must be greater than minimum target.'
                })
        
        return cleaned_data


class ProjectFilterForm(BaseForm):
    """
    Form for additional project filtering options.
    """
    
    SORT_CHOICES = [
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
        ('-total_target', 'Highest Target'),
        ('total_target', 'Lowest Target'),
        ('-current_funding', 'Most Funded'),
        ('title', 'Alphabetical A-Z'),
        ('-title', 'Alphabetical Z-A'),
        ('end_date', 'Ending Soon'),
        ('-end_date', 'Ending Later'),
    ]
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Sort By'
    )
    
    owner_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by project owner name...',
            'class': 'form-control'
        }),
        label='Project Owner'
    )


class ContributionForm(BaseForm):
    """
    Form for making contributions to projects.
    """
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter contribution amount',
            'step': '0.01',
            'min': '1',
            'class': 'form-control'
        }),
        help_text="Minimum contribution is 1 EGP."
    )
    
    comment = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Add a supportive message (optional)...',
            'rows': 3,
            'maxlength': 500,
            'class': 'form-control'
        }),
        help_text="Optional message to support the project creator."
    )
    
    anonymous = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="Make this contribution anonymous",
        help_text="Your name will not be displayed publicly."
    )
    
    def clean_amount(self):
        """Validate contribution amount"""
        amount = self.cleaned_data.get('amount')
        
        if amount:
            # Minimum contribution
            if amount < 1:
                raise ValidationError("Minimum contribution is 1 EGP.")
            
            # Maximum contribution (anti-money laundering)
            if amount > 100000:  # 100,000 EGP
                raise ValidationError("Maximum single contribution is 100,000 EGP.")
        
        return amount
    
    def clean_comment(self):
        """Validate contribution comment"""
        comment = self.cleaned_data.get('comment')
        
        if comment:
            comment = comment.strip()
            
            # Basic content filtering
            inappropriate_words = ['spam', 'scam', 'fake', 'fraud']
            if any(word in comment.lower() for word in inappropriate_words):
                raise ValidationError("Comment contains inappropriate content.")
        
        return comment