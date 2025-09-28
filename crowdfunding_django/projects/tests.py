from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Project, ProjectContribution

class AuthRedirectTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')

    def test_login_redirect(self):
        response = self.client.post(reverse('accounts:login'), {'username': 'testuser', 'password': 'testpass'})
        self.assertRedirects(response, reverse('accounts:dashboard'))

    def test_registration_redirect(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'email': 'newuser@example.com'
        })
        self.assertRedirects(response, reverse('accounts:dashboard'))

class ContributionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.project = Project.objects.create(
            title='Test Project',
            details='Details',
            total_target=1000,
            start_date='2025-01-01',
            end_date='2025-12-31',
            owner=self.user,
            is_active=True
        )

    def test_contribution_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('projects:contribute', args=[self.project.pk]), {'amount': 100})
        self.assertRedirects(response, reverse('projects:detail', args=[self.project.pk]))