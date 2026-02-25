from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ..forms import ManufacturerForm, FilterForm
from .data_processing import clean_filters
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import Manufacturer


class ManufacturerListView(PermissionRequiredMixin, ListView):
    permission_required = 'storage.view_manufacturer'
    model = Manufacturer
    template_name = 'manufacturers.html'
    context_object_name = 'manufacturers'
    paginate_by = 10

    def get_queryset(self):
        manufacturers = Manufacturer.objects.all()
        filters = {
            'name__icontains': self.request.GET.get('text_filter')
        }
        filters = clean_filters(filters)
        if filters:
            manufacturers = manufacturers.filter(**filters)
        return manufacturers
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        html_queries = {
            'text_filter': self.request.GET.get('text_filter')
        }
        html_queries = clean_filters(html_queries)
        context['filter_form'] = FilterForm(initial=html_queries)
        context['filters'] = html_queries
        return context
    
class ManufacturerCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'storage.add_manufacturer'
    model = Manufacturer
    form_class = ManufacturerForm
    template_name = 'add_manufacturer.html'
    success_url = reverse_lazy('storage:manufacturers')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Производитель успешно добавлен')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('manufacturers')
    
class ManufacturerUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'storage.edit_manufacturer'
    model = Manufacturer
    form_class = ManufacturerForm
    template_name = 'edit_manufacturer.html'
    success_url = reverse_lazy('storage:manufacturers')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Произвоитель успешно изменен')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('manufacturers')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        context['id'] = self.object.id
        return context

class ManufacturerDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'storage.delete_manufacturer'
    model = Manufacturer
    template_name = 'delete.html'
    success_url = reverse_lazy('storage:manufacturers')

    def form_valid(self, form):
        try:
            self.object.delete()
            messages.success(self.request, 'Производитель удалён')
        except Exception as e:
            messages.error(self.request, e.args[0])
        return redirect(self.success_url)