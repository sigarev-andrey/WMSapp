from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ..forms import CompanyForm, FilterForm
from .data_processing import clean_filters
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import Company


class CompanyListView(PermissionRequiredMixin, ListView):
    permission_required = 'storage.view_company'
    model = Company
    template_name = 'companies.html'
    context_object_name = 'companies'
    paginate_by = 10

    def get_queryset(self):
        companies = Company.objects.all()
        filters = {
            'name__icontains': self.request.GET.get('text_filter')
        }
        filters = clean_filters(filters)
        if filters:
            companies = companies.filter(**filters)
        companies = companies.order_by('name')
        return companies
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        html_queries = {
            'text_filter': self.request.GET.get('text_filter')
        }
        html_queries = clean_filters(html_queries)
        context['filter_form'] = FilterForm(initial=html_queries)
        context['filters'] = html_queries
        return context

class CompanyCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'storage.add_company'
    model = Company
    form_class = CompanyForm
    template_name = 'add_company.html'
    success_url = reverse_lazy('storage:companies')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Фирма успешно добавлена')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('storage:companies')

class CompanyUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'storage.edit_company'
    model = Company
    form_class = CompanyForm
    template_name = 'edit_company.html'
    success_url = reverse_lazy('storage:companies')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Фирма успешно изменена')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('company')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.object.id
        return context

class CompanyDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'storage.delete_company'
    model = Company
    template_name = 'delete.html'
    success_url = reverse_lazy('storage:companies')

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except Exception as e:
            print(e.args[0])
            messages.error(self.request, e)
        return redirect(self.success_url)
