from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from ..forms import SupplyForm, ItemInSupplyForm, FilterForm
from .data_processing import clean_filters
from django.shortcuts import redirect, get_object_or_404
from django.db import transaction
from django.db.models import F
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.core.paginator import Paginator
from ..models import Supply, ItemInSupply, Item, Storage, Contract
from ..logic import SupplyService


class SupplyListView(PermissionRequiredMixin, ListView):
    permission_required = 'storage.view_supply'
    model = Supply
    template_name = 'supplies.html'
    context_object_name = 'supplies'
    paginate_by = 10

    def get_queryset(self):
        supplies = Supply.objects.all().order_by('-date')
        filters = {
            'contract__id': self.request.GET.get('contract'),
            'date__gte': self.request.GET.get('start_date'),
            'date__lte': self.request.GET.get('end_date')
        }
        filters = clean_filters(filters)
        if filters:
            supplies = supplies.filter(**filters)
        return supplies
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        html_queries = {
            'contract': self.request.GET.get('contract'),
            'start_date': self.request.GET.get('start_date'),
            'end_date': self.request.GET.get('end_date')
        }
        html_queries = clean_filters(html_queries)
        context['filter_form'] = FilterForm(initial=html_queries)
        context['filters'] = html_queries
        return context
    
class SupplyDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'storage.view_iteminsupply'
    model = Supply
    template_name = 'details_supply.html'
    context_object_name = 'supply'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем связанные объекты
        items_list = self.object.iteminsupply_set.select_related('item').all()
        
        # Пагинация (get_page автоматически обрабатывает ошибки)
        paginator = Paginator(items_list, self.paginate_by)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        # Добавляем в контекст
        context.update({
            'items': page_obj,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'paginator': paginator,
        })
        
        return context

class SupplyCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'storage.add_supply'
    model = Supply
    form_class = SupplyForm
    template_name = 'add_supply.html'
    success_url = reverse_lazy('storage:supplies')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Поставка успешно добавлена')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('storage:supplies')

class SupplyUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'storage.edit_supply'
    model = Supply
    form_class = SupplyForm
    template_name = 'edit_supply.html'
    success_url = reverse_lazy('storage:supplies')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Поставка успешно изменена')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('supply')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.object.id
        return context

class SupplyDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'storage.delete_supply'
    model = Supply
    template_name = 'delete.html'
    success_url = reverse_lazy('storage:supplies')

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(self.request, e.args[0])
        return redirect(self.success_url)

class ItemInSupplyCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'storage.create_iteminsupply'
    model = ItemInSupply
    form_class = ItemInSupplyForm
    template_name = 'add_item_in_supply.html'
    
    def form_valid(self, form):
        supply = get_object_or_404(Supply, pk=self.kwargs['pk'])
        item = form.cleaned_data['item']
        count = form.cleaned_data['count']

        form.instance.supply = supply

        try:
            # use service layer
            SupplyService.add_item(
                supply, item, count
            )
            messages.success(self.request, 'Позиция успешно добавлена')    
        except Exception as e:
            messages.error(self.request, f'Ошибка: {e}')

        return redirect('storage:details-supply', pk=supply.pk)
    
    def get_success_url(self):
        return reverse('storage:details-supply', kwargs={'pk': self.object.supply.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['supply_pk'] = self.kwargs['pk']
        return context
    
class ItemInSupplyDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'storage.delete_iteminsupply'
    model = ItemInSupply
    template_name = 'delete.html'
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        supply_pk = self.object.supply.pk
        
        try:
            # use service layer
            SupplyService.delete_item(self.object)
            messages.success(self.request, 'Позиция удалёна из поставки')
        except Exception as e:
            messages.error(self.request, f'Ошибка: {e}')
        
        return redirect('storage:details-supply', pk=supply_pk)