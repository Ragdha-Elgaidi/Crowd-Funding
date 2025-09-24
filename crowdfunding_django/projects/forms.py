from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Project, ProjectContribution
from datetime import date


class ProjectForm(forms.ModelForm):
    """
    Form for creating and editing projects
    """
    
    class Meta:
        model = Project
        fields = [
            'title', 'details', 'total_target', 
            'start_date', 'end_date', 'image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project title'
            }),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your project in detail...'
            }),
            'total_target': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Target amount in EGP',
                'step': '0.01',
                'min': '1'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
    
    def clean_start_date(self):
        """Validate start date"""
        start_date = self.cleaned_data.get('start_date')
        
        if start_date:
            # For new projects, start date cannot be in the past
            if not self.instance.pk and start_date < date.today():
                raise ValidationError("Start date cannot be in the past.")
        
        return start_date
    
    def clean_end_date(self):
        """Validate end date"""
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')
        
        if end_date and start_date:
            if end_date <= start_date:
                raise ValidationError("End date must be after start date.")
        
        return end_date
    
    def clean_total_target(self):
        """Validate target amount"""
        target = self.cleaned_data.get('total_target')
        
        if target:
            if target <= 0:
                raise ValidationError("Target amount must be greater than 0.")
            if target > 10000000:  # 10 million EGP limit
                raise ValidationError("Target amount cannot exceed 10,000,000 EGP.")
        
        return target


class ProjectSearchForm(forms.Form):
    """
    Form for searching projects
    """
    
    SEARCH_CHOICES = [
        ('', 'All Projects'),
        ('active', 'Active Projects'),
        ('upcoming', 'Upcoming Projects'),
        ('ended', 'Ended Projects'),
    ]
    
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search projects by title or description...'
        })
    )
    
    status_filter = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_search = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Search by date'
        }),
        help_text="Find projects active on this date"
    )
    
    min_target = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum target amount',
            'step': '0.01'
        })
    )
    
    max_target = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maximum target amount',
            'step': '0.01'
        })
    )


class ContributionForm(forms.ModelForm):
    """
    Form for making contributions to projects
    """
    
    class Meta:
        model = ProjectContribution
        fields = ['amount', 'message']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contribution amount in EGP',
                'step': '0.01',
                'min': '1'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional message to the project owner...'
            })
        }
    
    def clean_amount(self):
        """Validate contribution amount"""
        amount = self.cleaned_data.get('amount')
        
        if amount:
            if amount <= 0:
                raise ValidationError("Contribution amount must be greater than 0.")
            if amount > 100000:  # 100k EGP limit per contribution
                raise ValidationError("Single contribution cannot exceed 100,000 EGP.")
        
        return amount


class ProjectFilterForm(forms.Form):
    """
    Form for advanced project filtering
    """
    
    SORT_CHOICES = [
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
        ('-total_target', 'Highest Target'),
        ('total_target', 'Lowest Target'),
        ('-current_funding', 'Most Funded'),
        ('end_date', 'Ending Soon'),
    ]
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    owner_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Project owner name'
        })
    )