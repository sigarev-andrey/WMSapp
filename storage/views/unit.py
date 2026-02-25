from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ..forms import UnitForm
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import Unit


class UnitListView(PermissionRequiredMixin, ListView):
    permission_required = 'storage.view_unit'
    model = Unit
    template_name = 'units.html'
    context_object_name = 'units'
    paginate_by = 10

class UnitCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'storage.add_unit'
    model = Unit
    form_class = UnitForm
    template_name = 'add_unit.html'
    success_url = reverse_lazy('storage:units')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ед. изм. успешно добавлена')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('storage:units')
    
class UnitUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'storage.edit_unit'
    model = Unit
    form_class = UnitForm
    template_name = 'edit_unit.html'
    success_url = reverse_lazy('storage:units')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ед. изм. успешно изменена')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('units')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.object.id
        return context

class UnitDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'storage.delete_unit'
    model = Unit
    template_name = 'delete.html'
    success_url = reverse_lazy('storage:units')

    def form_valid(self, form):
        try:
            self.object.delete()
            messages.success(self.request, 'Ед. изм. удалена')
        except Exception as e:
            messages.error(self.request, e.args[0])
        return redirect(self.success_url)