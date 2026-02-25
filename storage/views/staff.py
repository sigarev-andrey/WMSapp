from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ..forms import StaffForm, FilterForm
from .data_processing import clean_filters
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import Staff


class StaffListView(PermissionRequiredMixin, ListView):
    permission_required = 'storage.view_staff'
    model = Staff
    template_name = 'staff.html'
    context_object_name = 'staff'
    paginate_by = 10

    def get_queryset(self):
        staff = Staff.objects.all()
        filters = {
            'name__icontains': self.request.GET.get('name_filter'),
            'surname__icontains': self.request.GET.get('surname_filter'),
            'patronymic__icontains': self.request.GET.get('patronymic_filter')
        }
        filters = clean_filters(filters)
        if filters:
            staff = staff.filter(**filters)
        staff = staff.order_by('name')
        return staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        html_queries = {
            'name_filter': self.request.GET.get('name_filter'),
            'surname_filter': self.request.GET.get('surname_filter'),
            'patronymic_filter': self.request.GET.get('patronymic_filter')
        }
        html_queries = clean_filters(html_queries)
        context['filter_form'] = FilterForm(initial=html_queries)
        context['filters'] = html_queries
        return context

class StaffCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'storage.add_staff'
    model = Staff
    form_class = StaffForm
    template_name = 'add_staff.html'
    success_url = reverse_lazy('storage:staff')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Работник успешно добавлен')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('storage:staff')

class StaffUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'storage.edit_staff'
    model = Staff
    form_class = StaffForm
    template_name = 'edit_staff.html'
    success_url = reverse_lazy('storage:staff')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Работник успешно изменен')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('staff')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.object.id
        return context

class StaffDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'storage.delete_staff'
    model = Staff
    template_name = 'delete.html'
    success_url = reverse_lazy('storage:staff')

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except Exception as e:
            print(e.args[0])
            messages.error(self.request, e)
        return redirect(self.success_url)