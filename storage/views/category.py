from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ..forms import CategoryForm, FilterForm
from .data_processing import clean_filters
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import Category


class CategoryListView(PermissionRequiredMixin, ListView):
    permission_required = 'storage.view_category'
    model = Category
    template_name = 'categories.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        categories = Category.objects.all()
        filters = {
            'name__icontains': self.request.GET.get('text_filter')
        }
        filters = clean_filters(filters)
        if filters:
            categories = categories.filter(**filters)
        return categories
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        html_queries = {
            'text_filter': self.request.GET.get('text_filter')
        }
        html_queries = clean_filters(html_queries)
        context['filter_form'] = FilterForm(initial=html_queries)
        context['filters'] = html_queries
        return context

class CategoryCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'storage.add_category'
    model = Category
    form_class = CategoryForm
    template_name = 'add_category.html'
    success_url = reverse_lazy('storage:categories')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Категория успешно добавлена')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('storage:categories')

class CategoryUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'storage.edit_category'
    model = Category
    form_class = CategoryForm
    template_name = 'edit_category.html'
    success_url = reverse_lazy('storage:categories')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Категория успешно изменена')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.object.id
        return context

class CategoryDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'storage.delete_category'
    model = Category
    template_name = 'delete.html'
    success_url = reverse_lazy('storage:categories')

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(self.request, e.args[0])
        return redirect(self.success_url)