from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ..forms import ContractForm, FilterForm
from .data_processing import clean_filters
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from ..models import Contract


class ContractListView(PermissionRequiredMixin, ListView):
    permission_required = 'storage.view_contract'
    model = Contract
    template_name = 'contracts.html'
    context_object_name = 'contracts'
    paginate_by = 10

    def get_queryset(self):
        contracts = Contract.objects.all()
        filters = {
            'short_number__icontains': self.request.GET.get('text_filter')
        }
        filters = clean_filters(filters)
        if filters:
            contracts = contracts.filter(**filters)
        contracts = contracts.order_by('-date')
        return contracts
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        html_queries = {
            'text_filter': self.request.GET.get('text_filter')
        }
        html_queries = clean_filters(html_queries)
        context['filter_form'] = FilterForm(initial=html_queries)
        context['filters'] = html_queries
        return context

class ContractCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'storage.add_contract'
    model = Contract
    form_class = ContractForm
    template_name = 'add_contract.html'
    success_url = reverse_lazy('storage:contracts')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Договор успешно добавлен')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('storage:contracts')

class ContractUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'storage.edit_contract'
    model = Contract
    form_class = ContractForm
    template_name = 'edit_contract.html'
    success_url = reverse_lazy('storage:contracts')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Договор успешно изменен')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('contracts')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.object.id
        return context

class ContractDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'storage.delete_contract'
    model = Contract
    template_name = 'delete.html'
    success_url = reverse_lazy('storage:contracts')

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except Exception as e:
            print(e.args[0])
            messages.error(self.request, e.args[0])
        return redirect(self.success_url)