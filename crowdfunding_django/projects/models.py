
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()


class Project(models.Model):
    """
    Project model for crowdfunding campaigns
    """
    
    title = models.CharField(
        max_length=200,
        help_text="Project title (max 200 characters)"
    )
    details = models.TextField(
        help_text="Detailed description of your project"
    )
    total_target = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(1.00)],
        help_text="Target amount in EGP"
    )
    start_date = models.DateField(
        help_text="Campaign start date"
    )
    end_date = models.DateField(
        help_text="Campaign end date"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Additional fields for better functionality
    current_funding = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Current amount raised"
    )
    image = models.ImageField(
        upload_to='project_images/',
        blank=True,
        null=True,
        help_text="Project image (optional)"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
    
    def __str__(self):
        return f"{self.title} by {self.owner.get_full_name()}"
    
    def clean(self):
        """Custom validation for the Project model"""
        super().clean()
        
        if self.start_date and self.end_date:
            # Check if end date is after start date
            if self.end_date <= self.start_date:
                raise ValidationError({
                    'end_date': 'End date must be after start date'
                })
            
            # Check if start date is not in the past (for new projects)
            if not self.pk and self.start_date < timezone.now().date():
                raise ValidationError({
                    'start_date': 'Start date cannot be in the past'
                })
    
    @property
    def funding_percentage(self):
        """Calculate funding percentage"""
        if self.total_target > 0:
            return (self.current_funding / self.total_target) * 100
        return 0
    
    @property
    def days_left(self):
        """Calculate days left in campaign"""
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return max(0, delta.days)
        return 0
    
    @property
    def is_campaign_active(self):
        """Check if campaign is currently active"""
        today = timezone.now().date()
        return self.is_active and self.start_date <= today <= self.end_date
    
    @property
    def campaign_status(self):
        """Get campaign status"""
        today = timezone.now().date()
        if not self.is_active:
            return "Inactive"
        if today < self.start_date:
            return "Upcoming"
        if today > self.end_date:
            return "Ended"
        return "Active"
    
    @property
    def current_amount(self):
        """Alias for current_funding used in templates"""
        return self.current_funding

    @property
    def goal_amount(self):
        """Alias for total_target used in templates"""
        return self.total_target

    @property
    def total_contributions(self):
        """Return number of contributions backing the project"""
        return self.contributions.count()

    def save(self, *args, **kwargs):
        """Override save to ensure validation"""
        self.full_clean()
        super().save(*args, **kwargs)


class ProjectContribution(models.Model):
    """
    Model to track contributions to projects
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    contributor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1.00)]
    )
    contributed_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(
        blank=True,
        help_text="Optional message from contributor"
    )
    
    class Meta:
        ordering = ['-contributed_at']
        verbose_name = 'Contribution'
        verbose_name_plural = 'Contributions'
    
    def __str__(self):
        return f"{self.contributor.get_full_name()} - {self.amount} EGP to {self.project.title}"
    
    def save(self, *args, **kwargs):
        """Update project funding when contribution is saved"""
        super().save(*args, **kwargs)
        
        # Update project current funding
        total_contributions = self.project.contributions.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        self.project.current_funding = total_contributions
        self.project.save(update_fields=['current_funding'])
