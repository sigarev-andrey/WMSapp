from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView
from .data_processing import (
    get_storage_common, get_storage_with_contract,
    clean_filters
)
from ..forms import FilterForm


class StorageListView(PermissionRequiredMixin, ListView):
    permission_required = 'storage.view_storage'
    template_name = 'storage.html'
    context_object_name = 'storage'
    paginate_by = 15

    def get_queryset(self):
        storage = get_storage_common()
        filters = {
            'item__category__id': self.request.GET.get('category'),
            'full_item_name__icontains': self.request.GET.get('text_filter')
        }
        filters = clean_filters(filters)
        if filters:
            storage = storage.filter(**filters)
        return storage
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        html_queries = {
            'category': self.request.GET.get('category'),
            'text_filter': self.request.GET.get('text_filter')
        }
        html_queries = clean_filters(html_queries)
        context['filter_form'] = FilterForm(initial=html_queries)
        context['filters'] = html_queries
        return context

class StorageWithContractListView(PermissionRequiredMixin, ListView):
    permission_required = 'storage.view_storage'
    template_name = 'storage_with_contract.html'
    context_object_name = 'storage'
    paginate_by = 15

    def get_queryset(self):
        storage = get_storage_with_contract()
        filters = {
            'item__category__id': self.request.GET.get('category'),
            'full_item_name__icontains': self.request.GET.get('text_filter'),
            'contract__id': self.request.GET.get('contract')
        }
        filters = clean_filters(filters)
        if filters:
            storage = storage.filter(**filters)
        return storage
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        html_queries = {
            'category': self.request.GET.get('category'),
            'text_filter': self.request.GET.get('text_filter'),
            'contract': self.request.GET.get('contract')
        }
        html_queries = clean_filters(html_queries)
        context['filter_form'] = FilterForm(initial=html_queries)
        context['filters'] = html_queries
        return context