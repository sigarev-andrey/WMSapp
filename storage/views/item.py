from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ..forms import ItemForm, FilterForm
from .data_processing import clean_filters
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import Item
from .data_processing import get_items


class ItemListView(PermissionRequiredMixin, ListView):
    permission_required = 'storage.view_item'
    model = Item
    template_name = 'items.html'
    context_object_name = 'items'
    paginate_by = 10

    def get_queryset(self):
        items = get_items()
        filters = {
            'category__id': self.request.GET.get('category'),
            'full_item_name__icontains': self.request.GET.get('text_filter')
        }
        filters = clean_filters(filters)
        if filters:
            items = items.filter(**filters)
        return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        html_queries = {
            'category': self.request.GET.get('category'),
            'text_filter': self.request.GET.get('text_filter'),
        }
        html_queries = clean_filters(html_queries)
        context['filter_form'] = FilterForm(initial=html_queries)
        context['filters'] = html_queries
        
        # Handle current_id for scrolling to specific item
        current_id = self.request.session.get('current_id')
        if current_id:
            del self.request.session['current_id']
            context['current_id'] = current_id
            print(context)
        return context


class ItemCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'storage.add_item'
    model = Item
    form_class = ItemForm
    template_name = 'add_item.html'
    success_url = reverse_lazy('storage:items')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Позиция успешно добавлена')
        self.request.session['current_id'] = self.object.id
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('storage:items')


class ItemUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'storage.edit_item'
    model = Item
    form_class = ItemForm
    template_name = 'edit_item.html'
    success_url = reverse_lazy('storage:items')
    context_object_name = 'edit_item_form'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Позиция успешно изменена')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('items')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.object.id
        return context


class ItemDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'storage.delete_item'
    model = Item
    template_name = 'delete.html'
    success_url = reverse_lazy('storage:items')

    def form_valid(self, form):
        try:
            self.object.delete()
            messages.success(self.request, 'Позиция удалена')
        except Exception as e:
            messages.error(self.request, e.args[0])
        return redirect(self.success_url)