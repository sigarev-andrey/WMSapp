from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from ..forms import ReleaseForm, ItemInReleaseForm, FilterForm
from .data_processing import clean_filters
from django.shortcuts import redirect, get_object_or_404
from django.db import transaction
from django.db.models import F, Q
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from ..models import Release, ItemInRelease, Item, Storage, Contract
from ..logic import ReleaseService


AUTOCOMPLETE_LIMIT = 30
AUTOCOMPLETE_MIN_QUERY_LENGTH = 2


def _apply_storage_search(queryset, query):
    for term in query.split():
        queryset = queryset.filter(
            Q(item__article__icontains=term)
            | Q(item__description__icontains=term)
            | Q(item__manufacturer__name__icontains=term)
            | Q(contract__short_number__icontains=term)
            | Q(contract__full_number__icontains=term)
            | Q(contract__description__icontains=term)
        )
    return queryset


def _storage_option_label(storage_item):
    manufacturer = storage_item.item.manufacturer.name if storage_item.item.manufacturer else ''
    return ' '.join(
        part for part in [
            manufacturer,
            storage_item.item.article,
            str(storage_item.contract),
            storage_item.item.description,
        ]
        if part
    )


@permission_required('storage.view_storage')
def release_item_options(request):
    query = request.GET.get('q', '').strip()
    contract_id = request.GET.get('contract')
    if len(query) < AUTOCOMPLETE_MIN_QUERY_LENGTH:
        return JsonResponse({'results': []})

    storage_items = Storage.objects.select_related(
        'item',
        'item__manufacturer',
        'contract',
    ).filter(count__gt=0)

    if contract_id:
        storage_items = storage_items.filter(contract_id=contract_id)

    storage_items = (
        _apply_storage_search(storage_items, query)
        .order_by('item__manufacturer__name', 'item__article', 'contract__short_number')[:AUTOCOMPLETE_LIMIT]
    )

    return JsonResponse({
        'results': [
            {
                'id': storage_item.id,
                'label': _storage_option_label(storage_item),
                'count': storage_item.count,
                'contract': str(storage_item.contract),
            }
            for storage_item in storage_items
        ]
    })


class ReleaseListView(PermissionRequiredMixin, ListView):
    permission_required = 'storage.view_release'
    model = Release
    template_name = 'releases.html'
    context_object_name = 'releases'
    paginate_by = 10

    def get_queryset(self):
        supplies = Release.objects.all().order_by('-date')
        filters = {
            'name__icontains': self.request.GET.get('text_filter')
        }
        filters = clean_filters(filters)
        if filters:
            supplies = supplies.filter(**filters)
        return supplies
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        html_queries = {
            'text_filter': self.request.GET.get('text_filter')
        }
        html_queries = clean_filters(html_queries)
        context['filter_form'] = FilterForm(initial=html_queries)
        context['filters'] = html_queries
        return context
    

class ReleaseDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'storage.view_iteminrelease'
    model = Release
    template_name = 'details_release.html'
    context_object_name = 'release'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем связанные объекты
        items_list = self.object.iteminrelease_set.select_related('item').all()
        
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


class ReleaseCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'storage.add_release'
    model = Release
    form_class = ReleaseForm
    template_name = 'add_release.html'
    success_url = reverse_lazy('storage:releases')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Выдача успешно добавлена')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('storage:releases')


class ReleaseUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'storage.edit_release'
    model = Release
    form_class = ReleaseForm
    template_name = 'edit_release.html'
    success_url = reverse_lazy('storage:releases')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'ВВыдача успешно изменена')
        return response

    def form_invalid(self, form):
        messages.error(self.request, form.errors.as_data())
        return redirect('release')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.object.id
        return context
    

class ReleaseDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'storage.delete_release'
    model = Release
    template_name = 'delete.html'
    success_url = reverse_lazy('storage:releases')

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(self.request, e.args[0])
        return redirect(self.success_url)


class ItemInReleaseCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'storage.create_iteminrelease'
    model = ItemInRelease
    form_class = ItemInReleaseForm
    template_name = 'add_item_in_release.html'
    
    def form_valid(self, form):
        release = get_object_or_404(Release, pk=self.kwargs['pk'])
        item = form.cleaned_data['item']
        count = form.cleaned_data['count']

        form.instance.release = release

        try:
            # use service layer
            ReleaseService.add_item(
                release, item, count
            )
            messages.success(self.request, 'Позиция успешно добавлена')    
        except Exception as e:
            messages.error(self.request, f'Ошибка: {e}')

        return redirect('storage:details-release', pk=release.pk)
    
    def get_success_url(self):
        return reverse('storage:details-release', kwargs={'pk': self.object.release.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['release_pk'] = self.kwargs['pk']
        return context


class ItemInReleaseDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'storage.delete_iteminrelease'
    model = ItemInRelease
    template_name = 'delete.html'
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        release_pk = self.object.release.pk
        
        try:
            # use service layer
            ReleaseService.delete_item(self.object)
            messages.success(self.request, 'Позиция удалёна из выдачи')
        except Exception as e:
            messages.error(self.request, f'Ошибка: {e}')
        
        return redirect('storage:details-release', pk=release_pk)