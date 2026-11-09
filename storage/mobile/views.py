"""Mobile pages. All inventory mutations go through the shared service layer."""
from functools import reduce
from operator import or_

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from storage import forms as model_forms
from storage import models
from storage.logic import CountError, ReleaseService, SupplyService
from storage.views.data_processing import get_storage_common, get_storage_with_contract
from storage.views.reports import report_by_contract, report_common
from .forms import (
    ContractReportForm, ContractStockFilterForm, DocumentFilterForm, MobileAuthenticationForm, ReleaseLineForm,
    ReportForm, SearchForm, StockFilterForm, SupplyLineForm, prepare_form,
)


authenticated = login_required(login_url='mobile:login')
DIRECTORIES = {
    'items': (models.Item, model_forms.ItemForm, 'Позиции', ('article', 'description', 'manufacturer__name')),
    'contracts': (models.Contract, model_forms.ContractForm, 'Договоры', ('short_number', 'full_number', 'description')),
    'categories': (models.Category, model_forms.CategoryForm, 'Категории', ('name',)),
    'manufacturers': (models.Manufacturer, model_forms.ManufacturerForm, 'Производители', ('name',)),
    'units': (models.Unit, model_forms.UnitForm, 'Единицы измерения', ('name',)),
    'staff': (models.Staff, model_forms.StaffForm, 'Сотрудники', ('surname', 'name', 'patronymic')),
    'companies': (models.Company, model_forms.CompanyForm, 'Организации', ('name',)),
}
DOCUMENTS = {
    'supplies': (models.Supply, model_forms.SupplyForm, models.ItemInSupply, SupplyService, 'Поставки', 'Поставка'),
    'releases': (models.Release, model_forms.ReleaseForm, models.ItemInRelease, ReleaseService, 'Выдачи', 'Выдача'),
}


def config(registry, kind):
    if kind not in registry:
        raise Http404
    return registry[kind]


def can(request, model, action='view'):
    return request.user.has_perm(f'storage.{action}_{model._meta.model_name}')


def require_permission(request, model, action='view'):
    if not can(request, model, action):
        raise PermissionDenied


def page(request, template, title, section='menu', **context):
    return render(request, f'mobile/{template}.html', {'title': title, 'section': section, **context})


def paginate(request, queryset, params=None):
    params = request.GET.copy() if params is None else params.copy()
    params.pop('page', None)
    return {
        'page_obj': Paginator(queryset, 15).get_page(request.GET.get('page')),
        'page_query': params.urlencode(),
        'has_filters': any(value for key, value in params.items() if key != 'mode'),
    }


class MobileLoginView(LoginView):
    template_name = 'mobile/login.html'
    authentication_form = MobileAuthenticationForm
    next_page = reverse_lazy('mobile:stock')
    extra_context = {'title': 'Вход в WMS', 'is_login': True}

    def get_default_redirect_url(self):
        return reverse('mobile:stock' if can(self.request, models.Storage) else 'mobile:menu')


class MobileLogoutView(LogoutView):
    http_method_names = ['post', 'options']
    next_page = reverse_lazy('mobile:login')


@authenticated
def stock(request):
    require_permission(request, models.Storage)
    by_contract = request.GET.get('mode') == 'contracts'
    params = request.GET.copy()
    if not by_contract:
        params.pop('contract', None)
    form_class = ContractStockFilterForm if by_contract else StockFilterForm
    form = form_class(params)
    queryset = get_storage_with_contract() if by_contract else get_storage_common()
    if form.is_valid():
        data = form.cleaned_data
        if data['q']:
            queryset = queryset.filter(full_item_name__icontains=data['q'])
        if data['category']:
            queryset = queryset.filter(item__category=data['category'])
        if data.get('contract'):
            queryset = queryset.filter(contract=data['contract'])
    else:
        queryset = queryset.none()
    queryset = queryset.order_by('full_item_name', 'item_id', 'contract_id') if by_contract else queryset.order_by('full_item_name')
    mode_query = params.copy()
    mode_query.pop('mode', None)
    mode_query.pop('page', None)
    common_mode_query = mode_query.copy()
    common_mode_query.pop('contract', None)
    return page(request, 'stock', 'Склад', 'stock', filter_form=form,
                by_contract=by_contract, mode_query=mode_query.urlencode(),
                common_mode_query=common_mode_query.urlencode(), **paginate(request, queryset, params))


@authenticated
def menu(request):
    directories = [{'kind': kind, 'title': spec[2]} for kind, spec in DIRECTORIES.items() if can(request, spec[0])]
    return page(request, 'menu', 'Ещё', directories=directories,
                stock_reports=can(request, models.Storage),
                contract_reports=all(can(request, model) for model in (models.Contract, models.ItemInSupply, models.ItemInRelease)))


@authenticated
def documents(request, kind):
    model, _, line_model, _, title, _ = config(DOCUMENTS, kind)
    require_permission(request, model)
    form = DocumentFilterForm(request.GET)
    queryset = model.objects.select_related('contract').order_by('-date', '-pk')
    if kind == 'releases':
        queryset = queryset.select_related('company', 'staff')
    if form.is_valid():
        data = form.cleaned_data
        if data['q']:
            search = Q(description__icontains=data['q']) | Q(contract__short_number__icontains=data['q'])
            if kind == 'releases':
                search |= Q(company__name__icontains=data['q']) | Q(staff__surname__icontains=data['q'])
            queryset = queryset.filter(search)
        for key, lookup in [('contract', 'contract'), ('start_date', 'date__gte'), ('end_date', 'date__lte')]:
            if data[key]:
                queryset = queryset.filter(**{lookup: data[key]})
    else:
        queryset = queryset.none()
    return page(request, 'documents', title, kind, kind=kind, filter_form=form,
                can_add=can(request, model, 'add'), can_detail=can(request, line_model),
                **paginate(request, queryset))


def document_lines(document, kind):
    return document.iteminsupply_set if kind == 'supplies' else document.iteminrelease_set


def document_url(kind, pk):
    return reverse('mobile:document-detail', kwargs={'kind': kind, 'pk': pk})


@authenticated
def document_detail(request, kind, pk):
    model, _, line_model, _, _, singular = config(DOCUMENTS, kind)
    require_permission(request, model)
    require_permission(request, line_model)
    document = get_object_or_404(model.objects.select_related('contract'), pk=pk)
    item_path = 'item' if kind == 'supplies' else 'item__item'
    lines = document_lines(document, kind).select_related(f'{item_path}__manufacturer', f'{item_path}__unit')
    if kind == 'releases':
        lines = lines.select_related('item__contract')
    return page(request, 'document_detail', f'{singular} №{pk}', kind, document=document, kind=kind,
                can_edit=can(request, model, 'change'), can_delete=can(request, model, 'delete'),
                can_add_line=can(request, line_model, 'add'), can_delete_line=can(request, line_model, 'delete'),
                back_url=reverse('mobile:documents', kwargs={'kind': kind}), **paginate(request, lines.order_by('pk')))


@authenticated
@require_http_methods(['GET', 'POST'])
def document_form(request, kind, pk=None):
    model, form_class, line_model, _, _, singular = config(DOCUMENTS, kind)
    require_permission(request, model, 'change' if pk else 'add')
    # Lock the document while editing so mobile line additions cannot race a contract change.
    with transaction.atomic():
        document = get_object_or_404(model.objects.select_for_update(), pk=pk) if pk else None
        form = prepare_form(form_class(request.POST if request.method == 'POST' else None, instance=document,
                                       initial={'date': timezone.localdate()} if not pk else None))
        if document and document_lines(document, kind).exists():
            form.fields['contract'].disabled = True
            form.fields['contract'].help_text = 'Договор нельзя изменить, пока в документе есть позиции.'
        if request.method == 'POST' and form.is_valid():
            document = form.save()
            messages.success(request, 'Документ сохранён.')
            if can(request, model) and can(request, line_model):
                return redirect(document_url(kind, document.pk))
            return redirect('mobile:documents', kind=kind)
    back = document_url(kind, pk) if pk else reverse('mobile:documents', kwargs={'kind': kind})
    return page(request, 'form', f'{"Изменить" if pk else "Добавить"}: {singular.lower()}', kind,
                form=form, back_url=back, submit_label='Сохранить документ')


@authenticated
@require_http_methods(['GET', 'POST'])
def document_delete(request, kind, pk):
    model, _, _, _, _, _ = config(DOCUMENTS, kind)
    require_permission(request, model, 'delete')
    document = get_object_or_404(model, pk=pk)
    error = None
    if request.method == 'POST':
        try:
            with transaction.atomic():
                document = get_object_or_404(model.objects.select_for_update(), pk=pk)
                document.delete()
            messages.success(request, 'Документ удалён.')
            return redirect('mobile:documents', kind=kind)
        except ProtectedError:
            error = 'Сначала удалите позиции из документа. Остатки будут пересчитаны автоматически.'
    return page(request, 'confirm_delete', 'Удалить документ', kind, object=document, error=error,
                back_url=document_url(kind, pk))


@authenticated
@require_http_methods(['GET', 'POST'])
def line_add(request, kind, pk):
    model, _, line_model, service, _, _ = config(DOCUMENTS, kind)
    require_permission(request, line_model, 'add')
    require_permission(request, model)
    require_permission(request, line_model)
    document = get_object_or_404(model, pk=pk)
    form_class = SupplyLineForm if kind == 'supplies' else ReleaseLineForm
    form = form_class(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                document = get_object_or_404(model.objects.select_for_update(), pk=pk)
                item = form.cleaned_data['item']
                if kind == 'releases':
                    item = models.Storage.objects.select_for_update().get(pk=item.pk)
                service.add_item(document, item, form.cleaned_data['count'])
            messages.success(request, 'Позиция добавлена. Остатки обновлены.')
            return redirect(document_url(kind, pk))
        except CountError as exc:
            form.add_error('count', str(exc))
        except IntegrityError:
            form.add_error(None, 'Данные изменились. Проверьте позицию и повторите сохранение.')
    return page(request, 'form', 'Добавить позицию', kind, form=form, back_url=document_url(kind, pk),
                subtitle=str(document), submit_label='Добавить позицию', searchable_item=True)


@authenticated
@require_http_methods(['GET', 'POST'])
def line_delete(request, kind, pk, line_pk):
    model, _, line_model, service, _, _ = config(DOCUMENTS, kind)
    require_permission(request, line_model, 'delete')
    parent_field = 'supply' if kind == 'supplies' else 'release'
    lookup = {'pk': line_pk, f'{parent_field}_id': pk}
    line = get_object_or_404(line_model, **lookup)
    error = None
    if request.method == 'POST':
        try:
            with transaction.atomic():
                get_object_or_404(model.objects.select_for_update(), pk=pk)
                line = get_object_or_404(line_model.objects.select_for_update(), **lookup)
                if kind == 'releases':
                    line.item = models.Storage.objects.select_for_update().get(pk=line.item_id)
                else:
                    models.Storage.objects.select_for_update().get(item=line.item, contract=line.supply.contract)
                service.delete_item(line)
            messages.success(request, 'Позиция удалена. Остатки обновлены.')
            return redirect(document_url(kind, pk))
        except CountError as exc:
            error = str(exc)
        except models.Storage.DoesNotExist:
            error = 'Позиция на складе не найдена. Проверьте складской учёт.'
    return page(request, 'confirm_delete', 'Удалить позицию', kind, object=line, error=error,
                explanation='Остаток на складе будет пересчитан.', back_url=document_url(kind, pk))


@authenticated
def directory(request, kind):
    model, _, title, fields = config(DIRECTORIES, kind)
    require_permission(request, model)
    form = SearchForm(request.GET)
    queryset = model.objects.all()
    if kind == 'items':
        queryset = queryset.select_related('manufacturer', 'category', 'unit')
    if form.is_valid():
        if form.cleaned_data['q']:
            queryset = queryset.filter(reduce(or_, [Q(**{f'{field}__icontains': form.cleaned_data['q']}) for field in fields]))
    else:
        queryset = queryset.none()
    queryset = queryset.order_by(*model._meta.ordering, 'pk')
    return page(request, 'directory', title, kind=kind, filter_form=form, can_add=can(request, model, 'add'),
                can_edit=can(request, model, 'change'), can_delete=can(request, model, 'delete'),
                back_url=reverse('mobile:menu'), **paginate(request, queryset))


@authenticated
@require_http_methods(['GET', 'POST'])
def directory_form(request, kind, pk=None):
    model, form_class, title, _ = config(DIRECTORIES, kind)
    require_permission(request, model, 'change' if pk else 'add')
    instance = get_object_or_404(model, pk=pk) if pk else None
    form = prepare_form(form_class(request.POST if request.method == 'POST' else None, instance=instance))
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Запись сохранена.')
        return redirect('mobile:directory', kind=kind)
    return page(request, 'form', 'Изменить запись' if pk else 'Добавить запись', form=form, subtitle=title,
                back_url=reverse('mobile:directory', kwargs={'kind': kind}), submit_label='Сохранить')


@authenticated
@require_http_methods(['GET', 'POST'])
def directory_delete(request, kind, pk):
    model, _, _, _ = config(DIRECTORIES, kind)
    require_permission(request, model, 'delete')
    instance = get_object_or_404(model, pk=pk)
    error = None
    if request.method == 'POST':
        try:
            instance.delete()
            messages.success(request, 'Запись удалена.')
            return redirect('mobile:directory', kind=kind)
        except ProtectedError:
            error = 'Запись используется в складском учёте и не может быть удалена.'
    return page(request, 'confirm_delete', 'Удалить запись', object=instance, error=error,
                back_url=reverse('mobile:directory', kwargs={'kind': kind}))


@authenticated
@require_http_methods(['GET', 'POST'])
def report(request, kind):
    if kind not in ('stock', 'contract'):
        raise Http404
    if kind == 'stock':
        require_permission(request, models.Storage)
    else:
        for model in (models.Contract, models.ItemInSupply, models.ItemInRelease):
            require_permission(request, model)
    form_class = ReportForm if kind == 'stock' else ContractReportForm
    form = form_class(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        # The existing report generators accept POST data. Only validated values reach them.
        data = request.POST.copy()
        data['text_filter'] = form.cleaned_data.get('q', '')
        request.POST = data
        return report_common(request) if kind == 'stock' else report_by_contract(request)
    return page(request, 'form', 'Отчёт по складу' if kind == 'stock' else 'Движение по договору',
                form=form, back_url=reverse('mobile:menu'), submit_label='Скачать Excel',
                subtitle='Отчёт будет сохранён в формате .xls на ваше устройство.', is_download=True)
