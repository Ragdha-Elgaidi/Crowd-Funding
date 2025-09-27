from django import forms
from django.core.exceptions import ValidationError
from .models import Project, ProjectContribution
from datetime import date

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'details', 'total_target', 'start_date', 'end_date', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Project title'}),
            'details': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Project details'}),
            'total_target': forms.NumberInput(attrs={'min': '1'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'image': forms.FileInput()
        }
    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and not self.instance.pk and start_date < date.today():
            raise ValidationError("Start date cannot be in the past.")
        return start_date
    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')
        if end_date and start_date and end_date <= start_date:
            raise ValidationError("End date must be after start date.")
        return end_date
    def clean_total_target(self):
        target = self.cleaned_data.get('total_target')
        if target and target <= 0:
            raise ValidationError("Target amount must be greater than 0.")
        return target


class ProjectSearchForm(forms.Form):
    query = forms.CharField(required=False, max_length=200)
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))


class ProjectFilterForm(forms.Form):
    STATUS_CHOICES = (
        ("all", "All"),
        ("active", "Active"),
        ("upcoming", "Upcoming"),
        ("ended", "Ended"),
    )
    status = forms.ChoiceField(required=False, choices=STATUS_CHOICES)

class ContributionForm(forms.ModelForm):
    class Meta:
        model = ProjectContribution
        fields = ['amount', 'message']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': '1'}),
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Message (optional)'})
        }
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise ValidationError("Contribution amount must be greater than 0.")
        return amount
