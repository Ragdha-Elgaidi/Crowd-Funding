"""
Base views and mixins for the crowdfunding platform.

This module provides reusable view mixins and base classes that can be
composed to create feature-rich views with consistent behavior.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from typing import Dict, Any, Optional, List


class BaseContextMixin:
    """
    Mixin that provides common context data for all views.
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add common context
        context.update({
            'current_view': self.__class__.__name__,
            'app_name': self.request.resolver_match.app_name,
            'url_name': self.request.resolver_match.url_name,
            'current_user': self.request.user,
        })
        
        # Add page title if not set
        if 'title' not in context and hasattr(self, 'title'):
            context['title'] = self.title
        
        return context


class BreadcrumbMixin:
    """
    Mixin that provides breadcrumb navigation support.
    """
    breadcrumbs = []  # Override in subclasses
    
    def get_breadcrumbs(self):
        """
        Return breadcrumbs for the current view.
        Can be overridden to provide dynamic breadcrumbs.
        """
        return self.breadcrumbs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context


class MessageMixin:
    """
    Mixin that provides consistent messaging functionality.
    """
    success_message = ""
    error_message = ""
    warning_message = ""
    info_message = ""
    
    def get_success_message(self, cleaned_data=None):
        return self.success_message.format(**cleaned_data) if cleaned_data else self.success_message
    
    def get_error_message(self, form=None):
        return self.error_message
    
    def form_valid(self, form):
        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        error_message = self.get_error_message(form)
        if error_message:
            messages.error(self.request, error_message)
        return response


class AjaxResponseMixin:
    """
    Mixin that provides AJAX response support.
    """
    
    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    def get_ajax_data(self):
        """
        Return data for AJAX responses.
        Override in subclasses to provide custom data.
        """
        return {'success': True}
    
    def dispatch(self, request, *args, **kwargs):
        if self.is_ajax():
            self.template_name = getattr(self, 'ajax_template_name', self.template_name)
        return super().dispatch(request, *args, **kwargs)
    
    def render_to_response(self, context, **response_kwargs):
        if self.is_ajax():
            return self.render_to_ajax_response(context, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)
    
    def render_to_ajax_response(self, context, **response_kwargs):
        """
        Return an AJAX response.
        """
        data = self.get_ajax_data()
        data.update(context)
        return JsonResponse(data)


class SearchMixin:
    """
    Mixin that provides search functionality.
    """
    search_fields = []  # Fields to search in
    search_param = 'search'  # URL parameter name for search query
    
    def get_search_query(self):
        return self.request.GET.get(self.search_param, '').strip()
    
    def get_search_queryset(self, queryset):
        """
        Filter queryset based on search query.
        """
        search_query = self.get_search_query()
        if search_query and self.search_fields:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(q_objects)
        return queryset
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return self.get_search_queryset(queryset)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.get_search_query()
        return context


class FilterMixin:
    """
    Mixin that provides filtering functionality.
    """
    filter_fields = {}  # Dict mapping URL params to model fields
    
    def get_filter_params(self):
        """
        Extract filter parameters from request.
        """
        filters = {}
        for param, field in self.filter_fields.items():
            value = self.request.GET.get(param)
            if value:
                filters[field] = value
        return filters
    
    def get_filtered_queryset(self, queryset):
        """
        Apply filters to queryset.
        """
        filters = self.get_filter_params()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return self.get_filtered_queryset(queryset)


class SortMixin:
    """
    Mixin that provides sorting functionality.
    """
    sort_param = 'sort'  # URL parameter name for sort field
    default_sort = '-created_at'  # Default sort field
    allowed_sort_fields = []  # List of allowed sort fields
    
    def get_sort_field(self):
        sort_field = self.request.GET.get(self.sort_param, self.default_sort)
        if sort_field in self.allowed_sort_fields:
            return sort_field
        return self.default_sort
    
    def get_sorted_queryset(self, queryset):
        """
        Sort queryset.
        """
        sort_field = self.get_sort_field()
        return queryset.order_by(sort_field)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return self.get_sorted_queryset(queryset)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_sort'] = self.get_sort_field()
        context['allowed_sort_fields'] = self.allowed_sort_fields
        return context


class OwnerRequiredMixin(UserPassesTestMixin):
    """
    Mixin that ensures only the owner can access the view.
    """
    owner_field = 'owner'  # Field name for owner
    
    def test_func(self):
        obj = self.get_object()
        return getattr(obj, self.owner_field) == self.request.user


class StaffRequiredMixin(UserPassesTestMixin):
    """
    Mixin that ensures only staff users can access the view.
    """
    
    def test_func(self):
        return self.request.user.is_staff


class PaginationMixin:
    """
    Enhanced pagination mixin with AJAX support.
    """
    paginate_by = 25
    paginate_orphans = 5
    page_size_param = 'per_page'
    allowed_page_sizes = [10, 25, 50, 100]
    
    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by.
        """
        page_size = self.request.GET.get(self.page_size_param)
        if page_size and page_size.isdigit():
            page_size = int(page_size)
            if page_size in self.allowed_page_sizes:
                return page_size
        return self.paginate_by
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allowed_page_sizes'] = self.allowed_page_sizes
        context['current_page_size'] = self.get_paginate_by(None)
        context['show_page_size_selector'] = True
        return context


class StatisticsMixin:
    """
    Mixin that provides statistical data.
    """
    
    def get_statistics(self):
        """
        Override in subclasses to provide specific statistics.
        """
        return {}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statistics'] = self.get_statistics()
        return context


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at context.
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_time'] = timezone.now()
        return context


# Base View Classes

class BaseListView(
    BaseContextMixin,
    BreadcrumbMixin,
    SearchMixin,
    FilterMixin,
    SortMixin,
    PaginationMixin,
    AjaxResponseMixin,
    ListView
):
    """
    Enhanced ListView with search, filtering, sorting, and pagination.
    """
    pass


class BaseDetailView(
    BaseContextMixin,
    BreadcrumbMixin,
    AjaxResponseMixin,
    DetailView
):
    """
    Enhanced DetailView with common functionality.
    """
    pass


class BaseCreateView(
    BaseContextMixin,
    BreadcrumbMixin,
    MessageMixin,
    AjaxResponseMixin,
    LoginRequiredMixin,
    CreateView
):
    """
    Enhanced CreateView with messaging and AJAX support.
    """
    pass


class BaseUpdateView(
    BaseContextMixin,
    BreadcrumbMixin,
    MessageMixin,
    AjaxResponseMixin,
    LoginRequiredMixin,
    OwnerRequiredMixin,
    UpdateView
):
    """
    Enhanced UpdateView with ownership checking.
    """
    pass


class BaseDeleteView(
    BaseContextMixin,
    BreadcrumbMixin,
    MessageMixin,
    AjaxResponseMixin,
    LoginRequiredMixin,
    OwnerRequiredMixin,
    DeleteView
):
    """
    Enhanced DeleteView with ownership checking.
    """
    pass


class BaseDashboardView(
    BaseContextMixin,
    BreadcrumbMixin,
    StatisticsMixin,
    LoginRequiredMixin,
    TemplateView
):
    """
    Base view for dashboard pages.
    """
    pass