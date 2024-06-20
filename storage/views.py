from datetime import date
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.db import transaction
from django.db.models import CharField, Value, Sum, F
from django.db.models.functions import Concat
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.utils.encoding import smart_str
from django.utils.encoding import escape_uri_path
import xlwt
from .forms import *
from .models import Storage, Category, Manufacturer, Unit


def clean_filters(filters):
    '''Function to return only filled filter fields in form'''
    filters = {k: v for (k, v) in filters.items() if v}
    return filters

def get_storage_common():
    '''Function to return storage dateset without contract and summed counts of same items'''
    result = Storage.objects.all()
    result = result.annotate(full_item_name=Concat('item__manufacturer__name', Value(' '), 'item__article', Value(' '),
                                                     'item__description', output_field=CharField()))
    result = result.values('full_item_name', unit=F('item__unit__name'), category=F('item__category__name')
                             ).order_by('full_item_name').annotate(total_count=Sum('count'))
    result = result.filter(total_count__gt=0)
    return result

def get_storage_with_contract():
    '''Function to return storage dataset with contract of each item'''
    result = Storage.objects.all()
    result = result.annotate(full_item_name=Concat('item__manufacturer__name', Value(' '), 'item__article', Value(' '),
                                                     'item__description', output_field=CharField()))
    result = result.annotate(category=F('item__category__name'))
    result = result.annotate(unit=F('item__unit__name'))
    result = result.annotate(contract_number=F('contract__short_number'))
    result = result.values('full_item_name', 'category', 'contract', 'contract_number','unit', 'count')
    result = result.filter(count__gt=0)
    return result

@permission_required('storage.view_storage')
def storage(request):
    storage = get_storage_common()
    filters = {
        'item__category__id': request.GET.get('category'),
        'full_item_name__icontains': request.GET.get('text_filter')
    }
    filters = clean_filters(filters)
    if filters:
        storage = storage.filter(**filters)
    html_queries = {
        'category': request.GET.get('category'),
        'text_filter': request.GET.get('text_filter'),
    }
    html_queries = clean_filters(html_queries)
    paginator = Paginator(storage, 15)
    page_number = request.GET.get('page')
    page_storage = paginator.get_page(page_number)
    filter_form = StorageFilterForm(initial=html_queries)
    return render(request,
                  'storage.html',
                  {'storage': page_storage,
                   'filter_form': filter_form,
                   'filters': html_queries})

@permission_required('storage.view_storage')
def storage_with_contract(request):
    storage = get_storage_with_contract()
    filters = {
        'item__category__id': request.GET.get('category'),
        'full_item_name__icontains': request.GET.get('text_filter'),
        'contract__id': request.GET.get('contract'),
    }
    filters = clean_filters(filters)
    if filters:
        storage = storage.filter(**filters)
    html_queries = {
        'category': request.GET.get('category'),
        'text_filter': request.GET.get('text_filter'),
        'contract': request.GET.get('contract'),
    }
    html_queries = clean_filters(html_queries)
    paginator = Paginator(storage, 15)
    page_number = request.GET.get('page')
    page_storage = paginator.get_page(page_number)
    filter_form = StorageFilterForm(initial=html_queries)
    return render(request,
                  'storage_with_contract.html',
                  {'storage': page_storage,
                   'filter_form': filter_form,
                   'filters': html_queries})

@permission_required('storage.view_manufacturer')
def manufacturers(request):
    manufacturers = Manufacturer.objects.all()
    filters = {
        'name__icontains': request.GET.get('text_filter'),
    }
    filters = clean_filters(filters)
    if filters:
        manufacturers = manufacturers.filter(**filters)
    html_queries = {
        'text_filter': request.GET.get('text_filter'),
    }
    html_queries = clean_filters(html_queries)
    paginator = Paginator(manufacturers, 10)
    page_number = request.GET.get('page')
    page_manufacturers = paginator.get_page(page_number)
    filter_form = StorageFilterForm(initial=html_queries)
    return render(request,
                  'manufacturers.html',
                  {'manufacturers': page_manufacturers,
                   'filter_form': filter_form,
                   'filters': html_queries})

@permission_required('storage.add_manufacturer')
def add_manufacturer(request):
    if (request.method == 'POST'):
        add_manufacturer_form = ManufacturerForm(request.POST)
        if add_manufacturer_form.is_valid():
            add_manufacturer_form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Производитель успешно добавлен')
            return redirect('/manufacturers/')
        messages.add_message(request,
                             messages.ERROR,
                             add_manufacturer_form.errors.as_data())
        return redirect('/manufacturers/')
    else:
        add_manufacturer_form = ManufacturerForm()
    return render(request,
                  'add_manufacturer.html',
                  {'add_manufacturer_form': add_manufacturer_form})

@permission_required('storage.edit_manufacturer')
def edit_manufacturer(request, id=None):
    manufacturer = get_object_or_404(Manufacturer, pk=id)
    if (request.method == 'POST'):
        edit_manufacturer_form = ManufacturerForm(request.POST, instance=manufacturer)
        if edit_manufacturer_form.is_valid():
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Произвоитель успешно изменен')
            edit_manufacturer_form.save()
            return redirect('/manufacturers/')
        messages.add_message(request,
                             messages.ERROR,
                             edit_manufacturer_form.errors.as_data())
        return redirect('/manufacturers/')
    else:
        edit_manufacturer_form = ManufacturerForm(instance=manufacturer)
        return render(request,
                      'edit_manufacturer.html',
                      {'edit_manufacturer_form': edit_manufacturer_form,
                       'id': id})
    
@permission_required('storage.delete_manufacturer')
def delete_manufacturer(request, id=None):
    manufacturer = get_object_or_404(Manufacturer, pk=id)
    try:
        manufacturer.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             'Производитель удален')
    except Exception as e:
        messages.add_message(request,
                             messages.ERROR,
                             e)
    return redirect('/manufacturers/')

@permission_required('storage.view_unit')
def units(request):
    units = Unit.objects.all()
    return render(request,
                  'units.html',
                  {'units': units})

@permission_required('storage.add_unit')
def add_unit(request):
    if (request.method == 'POST'):
        add_unit_form = UnitForm(request.POST)
        if add_unit_form.is_valid():
            add_unit_form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Ед. изм. успешно добавлена')
            return redirect('/units/')
        messages.add_message(request,
                             messages.ERROR,
                             add_unit_form.errors.as_data())
        return redirect('/units/')
    else:
        add_unit_form = UnitForm()
    return render(request,
                  'add_unit.html',
                  {'add_unit_form': add_unit_form})

@permission_required('storage.edit_unit')
def edit_unit(request, id=None):
    unit = get_object_or_404(Unit, pk=id)
    if (request.method == 'POST'):
        edit_unit_form = UnitForm(request.POST, instance=unit)
        if edit_unit_form.is_valid():
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Ед. изм. успешно изменена')
            edit_unit_form.save()
            return redirect('/units/')
        messages.add_message(request,
                             messages.ERROR,
                             edit_unit_form.errors.as_data())
        return redirect('/units/')
    else:
        edit_unit_form = UnitForm(instance=unit)
        return render(request,
                      'edit_unit.html',
                      {'edit_unit_form': edit_unit_form,
                       'id': id})

@permission_required('storage.delete_unit')    
def delete_unit(request, id=None):
    unit = get_object_or_404(Unit, pk=id)
    try:
        unit.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             'Ед. изм. удалена')
    except Exception as e:
        messages.add_message(request,
                             messages.ERROR,
                             e)
    return redirect('/units/')

@permission_required('storage.view_category')
def categories(request):
    categories = Category.objects.all()
    return render(request,
                  'categories.html',
                   {'categories': categories})

@permission_required('storage.add_category')
def add_category(request):
    if (request.method == 'POST'):
        add_category_form = CategoryForm(request.POST)
        if add_category_form.is_valid():
            messages.add_message(request,
                                messages.SUCCESS,
                                'Ед. изм. успешно добавлена')
            add_category_form.save()
            return redirect('/categories/')
        messages.add_message(request,
                             messages.ERROR,
                             add_category_form.errors.as_data())
        return redirect('/categories/')
    else:
        add_category_form = CategoryForm()
    return render(request,
                  'add_category.html',
                  {'add_category_form': add_category_form})

@permission_required("storage.edit_category")
def edit_category(request, id=None):
    category = get_object_or_404(Category, pk=id)
    if (request.method == 'POST'):
        edit_category_form = CategoryForm(request.POST, instance=category)
        if edit_category_form.is_valid():
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Категория успешно изменена')
            edit_category_form.save()
            return redirect('/categories/')
        messages.add_message(request,
                             messages.ERROR,
                             edit_category_form.errors.as_data())
        return redirect('/categories/')
    else:
        edit_category_form = CategoryForm(instance=category)
    return render(request,
                  'edit_category.html',
                  {'edit_category_form': edit_category_form,
                   'id': id})

@permission_required('storage.delete_category')
def delete_category(request, id=None):
    category = get_object_or_404(Category, pk=id)
    try:
        category.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             'Категория удалена')
    except Exception as e:
        messages.add_message(request,
                             messages.ERROR,
                             e)
    return redirect('/categories/')

@permission_required('storage.view_company')
def companies(request):
    companies = Company.objects.all()
    return render(request,
                  'companies.html',
                  {'companies': companies})

@permission_required('storage.add_company')
def add_company(request):
    if (request.method == 'POST'):
        add_company_form = CompanyForm(request.POST)
        if add_company_form.is_valid():
            print('form is valid')
            add_company_form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Фирма успешно добавлена')
            return redirect('/companies/')
        messages.add_message(request,
                             messages.ERROR,
                             add_company_form.errors.as_data())
        return redirect('/companies/')
    else:
        add_company_form = CompanyForm()
        print('form created')
    return render(request,
                  'add_company.html',
                  {'add_company_form': add_company_form})

@permission_required('storage.edit_company')
def edit_company(request, id=None):
    company = get_object_or_404(Company, pk=id)
    if (request.method == 'POST'):
        edit_company_form = CompanyForm(request.POST, instance=company)
        if edit_company_form.is_valid():
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Фирма изменена')
            edit_company_form.save()
            return redirect('/companies/')
        messages.add_message(request,
                             messages.ERROR,
                             edit_company_form.errors.as_data())
        return redirect('/companies/')
    else:
        edit_company_form = CompanyForm(instance=company)
        return render(request,
                      'edit_company.html',
                      {'edit_company_form': edit_company_form,
                       'id': id})

@permission_required('storage.delete_company')
def delete_company(request, id=None):
    company = get_object_or_404(Company, pk=id)
    try:
        company.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             'Фирма удалена')
    except Exception as e:
        messages.add_message(request,
                             messages.ERROR,
                             e)
    return redirect('/companies/')

@permission_required('storage.view_item')
def items(request):
    items = Item.objects.all().annotate(full_item_name=Concat('manufacturer__name', Value(' '), \
                                                              'article', Value(' '), \
                                                              'description', \
                                                              output_field=CharField()))
    filters = {
        'category__id': request.GET.get('category'),
        'full_item_name__icontains': request.GET.get('text_filter')
    }
    filters = clean_filters(filters)
    if filters:
        items = items.filter(**filters)
    html_queries = {
        'category': request.GET.get('category'),
        'text_filter': request.GET.get('text_filter'),
    }
    html_queries = clean_filters(html_queries)
    page_size = 10
    paginator = Paginator(items, page_size)
    current_id = request.session.get('current_id')
    print(current_id)
    if current_id:
        del request.session['current_id']
        current_item = Item.objects.get(pk=current_id)
        item_name = str(current_item.manufacturer or '') + ' ' + current_item.article + ' ' + current_item.description
        print(item_name)
        position = items.filter(full_item_name__lt=item_name).count()
        page_number = position // page_size + 1
    else:
        page_number = request.GET.get('page')
    page_items = paginator.get_page(page_number)
    filter_form = StorageFilterForm(initial=html_queries)
    return render(request,
                  'items.html',
                  {'items': page_items,
                   'filter_form': filter_form,
                   'filters': html_queries,
                   'current_id': current_id})

@permission_required('storage.add_item')
def add_item(request):
    if (request.method == 'POST'):
        add_item_form = ItemForm(request.POST)
        if add_item_form.is_valid():
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Позиция успешно добавлена')
            item = add_item_form.save()
            request.session['current_id'] = item.id
            return redirect('/items/')
        messages.add_message(request,
                        messages.ERROR,
                        add_item_form.errors.as_data())
        return redirect('/items/')
    else:
        add_item_form = ItemForm()
    return render(request,
                  'add_item.html',
                  {'add_item_form': add_item_form})

@permission_required('storage.edit_item')
def edit_item(request, id=None):
    item = get_object_or_404(Item, pk=id)
    if (request.method == 'POST'):
        edit_item_form = ItemForm(request.POST, instance=item)
        if edit_item_form.is_valid():
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Позиция успешно изменена')
            edit_item_form.save()
            return redirect('/items/')
        messages.add_message(request,
                             messages.ERROR,
                             edit_item_form.errors.as_data())
        return redirect('/items/')
    else:
        edit_item_form = ItemForm(instance=item)
    return render(request,
                  'edit_item.html',
                  {'edit_item_form': edit_item_form,
                   'id': id})

@permission_required('storage.delete_item')
def delete_item(request, id=None):
    item = get_object_or_404(Item, pk=id)
    try:
        item.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             'Позиция удалена')
    except Exception as e:
        messages.add_message(request,
                             messages.ERROR,
                             e)
    return redirect('/items/')

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/storage/')
                else:
                    return HttpResponse('Disabled account')
            else:
                messages.add_message(request,
                                     messages.ERROR,
                                     'Неправильное имя пользователя или пароль')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)

@permission_required('storage.view_contract')
def contracts(request):
    contracts = Contract.objects.all()
    return render(request,
                  'contracts.html',
                  {'contracts': contracts})

@permission_required('storage.add_contract')
def add_contract(request):
    if (request.method == 'POST'):
        add_contract_form = ContractForm(request.POST)
        if add_contract_form.is_valid:
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Договор успешно добавлена')
            add_contract_form.save()
            return redirect('/contracts/')
        messages.add_message(request,
                             messages.ERROR,
                             add_contract_form.errors.as_data())
        return redirect('/contracts/')
    else:
        add_contract_form = ContractForm()
    return render(request,
                  'add_contract.html',
                  {'add_contract_form': add_contract_form})

@permission_required('storage.edit_contract')
def edit_contract(request, id=None):
    contract = get_object_or_404(Contract, pk=id)
    if (request.method == 'POST'):
        edit_contract_form = ContractForm(request.POST, instance=contract)
        if edit_contract_form.is_valid():
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Договор успешно изменен')
            edit_contract_form.save()
            return redirect('/contracts/')
        messages.add_message(request,
                             messages.ERROR,
                             edit_contract_form.errors.as_data())
        return redirect('/contracts/')
    else:
        edit_contract_form = ContractForm(instance=contract)
    return render(request,
                  'edit_contract.html',
                  {'edit_contract_form': edit_contract_form,
                   'id': id})

@permission_required('storage.delete_contract')
def delete_contract(request, id=None):
    contract = get_object_or_404(Contract, pk=id)
    try:
        contract.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             'Договор удален')
    except Exception as e:
        messages.add_message(request,
                             messages.ERROR,
                             e)
    return redirect('/contracts/')

@permission_required('storage.view_supply')
def supplies(request):
    supplies = Supply.objects.all().order_by('date')
    page_size = 10
    paginator = Paginator(supplies, page_size)
    page_number = request.GET.get('page')
    page_items = paginator.get_page(page_number)
    return render(request,
                  'supplies.html',
                  {'supplies': page_items})

@permission_required('storage.add_supply')
def add_supply(request):
    if (request.method == 'POST'):
        add_supply_form = SupplyForm(request.POST)
        if add_supply_form.is_valid:
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Поставка успешно добавлена')
            add_supply_form.save()
            return redirect('/supplies/')
    else:
        add_supply_form = SupplyForm()
    return render(request,
                  'add_supply.html',
                  {'add_supply_form': add_supply_form})

@permission_required('storage.edit_supply')
def edit_supply(request, id=False):
    supply = get_object_or_404(Supply, pk=id)
    if (request.method == 'POST'):
        edit_supply_form = SupplyForm(request.POST, instance=supply)
        if edit_supply_form.is_valid():
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Поставка успешно изменена')
            edit_supply_form.save()
            return redirect('/supplies/')
        messages.add_message(request,
                             messages.ERROR,
                             edit_supply_form.errors.as_data())
        return redirect('/supplies/')
    else:
        edit_supply_form = SupplyForm(instance=supply)
        edit_supply_form.fields['contract'].widget.attrs['readonly'] = True
    return render(request,
                  'edit_supply.html',
                  {'edit_supply_form': edit_supply_form,
                   'id': id})

@permission_required('storage.delete_supply')
def delete_supply(request, id=False):
    supply = get_object_or_404(Supply, pk=id)
    try:
        supply.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             'Поставка удалена')
    except Exception as e:
        messages.add_message(request,
                             messages.ERROR,
                             e)
    return redirect('/supplies/')

@permission_required('storage.view_iteminsupply')
def details_supply(request, id):
    supply = get_object_or_404(Supply, pk=id)
    items = ItemInSupply.objects.filter(supply=supply.pk).order_by('pk')
    page_size = 10
    paginator = Paginator(items, page_size)
    item_id = request.session.get('item_id')
    if item_id:
        del request.session['item_id']
        items_count = items.filter(pk__lt=item_id).count()
        page_number = items_count // page_size + 1
    else:
        page_number = request.GET.get('page')
    page_items = paginator.get_page(page_number)
    return render(request,
                  'details_supply.html',
                  {'supply': supply,
                   'items': page_items,
                   'current_id': item_id})

@permission_required('storage.add_iteminsupply')
@transaction.atomic
def add_item_in_supply(request, id):
    supply = get_object_or_404(Supply, pk=id)
    if (request.method == 'POST'):
        add_item_in_supply_form = ItemInSupplyForm(request.POST)
        if add_item_in_supply_form.is_valid():
            add_item_in_supply_form.instance.supply = supply
            item, create = Storage.objects.get_or_create(item=add_item_in_supply_form.cleaned_data['item'],
                                                         contract=supply.contract,
                                                         defaults={'count': add_item_in_supply_form.cleaned_data['count']})
            if not create:
                item.count += add_item_in_supply_form.cleaned_data['count']
            item.save()
            item_in_supply, create = ItemInSupply.objects.get_or_create(item=add_item_in_supply_form.cleaned_data['item'],
                                                                        supply=supply,
                                                                        defaults={'count': add_item_in_supply_form.cleaned_data['count']})
            if not create:
                item_in_supply.count += add_item_in_supply_form.cleaned_data['count']
            item_in_supply.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Позиция успешно добавлена')
            request.session['item_id'] = item_in_supply.pk
            return redirect('/supplies/details/' + str(id) + '/')
        messages.add_message(request,
                 messages.ERROR,
                 add_item_in_supply_form.errors.as_data())
        return redirect('/supplies/details/' + str(id) + '/')
    else:
        add_item_in_supply_form = ItemInSupplyForm()
    return render(request,
                    'add_item_in_supply.html',
                    {'add_item_in_supply_form': add_item_in_supply_form,
                     'id': id})

@permission_required('storage.delete_iteminsupply')
@transaction.atomic
def delete_item_from_supply(request, id):
    item_in_supply = get_object_or_404(ItemInSupply, pk=id)
    supply_id = item_in_supply.supply.pk
    item_in_storage = get_object_or_404(Storage,
                                        item=item_in_supply.item,
                                        contract=item_in_supply.supply.contract)
    if (item_in_supply.count > item_in_storage.count):
        messages.add_message(request,
                        messages.ERROR,
                        'Невозможно удалить т.к. позиция выдана')
    else:
        try:
            item_in_storage.count -= item_in_supply.count
            item_in_storage.save()
            item_in_supply.delete()
        except Exception as e:
            messages.add_message(request,
                                 messages.ERROR,
                                 e)
    return redirect('/supplies/details/' + str(supply_id) + '/')

@permission_required('storage.view_staff')
def staff(request):
    staff = Staff.objects.all()
    return render(request,
                  'staff.html',
                  {'staff': staff})

@permission_required('storage.add_staff')
def add_staff(request):
    if (request.method == 'POST'):
        add_staff_form = StaffForm(request.POST)
        if add_staff_form.is_valid:
            add_staff_form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Персонал успешно добавлен')
            return redirect('/staff/')
    else:
        add_staff_form = StaffForm()
    return render(request,
                  'add_staff.html',
                  {'add_staff_form': add_staff_form})

@permission_required('storage.edit_staff')
def edit_staff(request, id=False):
    staff = get_object_or_404(Staff, pk=id)
    if (request.method == 'POST'):
        edit_staff_form = StaffForm(request.POST, instance=staff)
        if edit_staff_form.is_valid():
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Персонал успешно изменен')
            edit_staff_form.save()
            return redirect('/staff/')
        messages.add_message(request,
                             messages.ERROR,
                             edit_staff_form.errors.as_data())
        return redirect('/staff/')
    else:
        edit_staff_form = StaffForm(instance=staff)
    return render(request,
                  'edit_staff.html',
                  {'edit_staff_form': edit_staff_form,
                   'id': id})

@permission_required('storage.delete_staff')
def delete_staff(request, id=False):
    staff = get_object_or_404(Staff, pk=id)
    try:
        staff.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             'Персонал удален')
    except Exception as e:
        messages.add_message(request,
                             messages.ERROR,
                             e)
    return redirect('/staff/')

@permission_required('storage.view_release')
def releases(request):
    releases = Release.objects.all().order_by('date')
    page_size = 10
    paginator = Paginator(releases, page_size)
    page_number = request.GET.get('page')
    page_items = paginator.get_page(page_number)
    return render(request,
                  'releases.html',
                  {'releases': page_items})

@permission_required('storage.add_release')
def add_release(request):
    if (request.method == 'POST'):
        add_release_form = ReleaseForm(request.POST)
        if add_release_form.is_valid:
            add_release_form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Выдача успешно добавлена')
            return redirect('/releases/')
        messages.add_message(request,
                             messages.ERROR,
                             add_release_form.errors.as_data())
        return redirect('/releases/')
    else:
        add_release_form = ReleaseForm()
    return render(request,
                  'add_release.html',
                  {'add_release_form': add_release_form})

@permission_required('storage.edit_release')
def edit_release(request, id=None):
    release = get_object_or_404(Release, pk=id)
    if (request.method == 'POST'):
        POST = request.POST.copy()
        POST['contract'] = release.contract
        edit_release_form = ReleaseForm(POST, instance=release)
        if edit_release_form.is_valid():
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Выдача успешно изменена')
            edit_release_form.save()
            return redirect('/releases/')
        messages.add_message(request,
                             messages.ERROR,
                             edit_release_form.errors.as_data())
        return redirect('/releases/')
    else:
        edit_release_form = ReleaseForm(instance=release)
        edit_release_form.fields['contract'].widget.attrs['disabled'] = True
    return render(request,
                  'edit_release.html',
                  {'edit_release_form': edit_release_form,
                   'id': id})

@permission_required('storage.delete_release')
def delete_release(request, id=None):
    release = get_object_or_404(Release, pk=id)
    try:
        release.delete()
        messages.add_message(request,
                             messages.SUCCESS,
                             'Поставка удалена')
    except Exception as e:
        messages.add_message(request,
                             messages.ERROR,
                             e)
    return redirect('/releases/')

@permission_required('storage.view_iteminrelease')
def details_release(request, id=None):
    release = get_object_or_404(Release, pk=id)
    items = ItemInRelease.objects.filter(release=release.pk)
    page_size = 10
    paginator = Paginator(items, page_size)
    page_number = request.GET.get('page')
    page_items = paginator.get_page(page_number)
    return render(request,
                  'details_release.html',
                  {'release': release,
                   'items': page_items})

@permission_required('storage.add_iteminrelease')
@transaction.atomic
def add_item_in_release(request, id):
    release = get_object_or_404(Release, pk=id)
    if (request.method == 'POST'):
        add_item_in_release_form = ItemInReleaseForm(request.POST)
        if add_item_in_release_form.is_valid():
            add_item_in_release_form.instance.release = release
            item = add_item_in_release_form.cleaned_data['item']
            if item.count < add_item_in_release_form.cleaned_data['count']:
                messages.add_message(request,
                                     messages.ERROR,
                                     'Кол-во выдачи не должно превышать ' + str(item.count))
                return redirect('/releases/details/' + str(id) + '/')
            item.count -= add_item_in_release_form.cleaned_data['count']
            item.save()
            item_in_release, create = ItemInRelease.objects.get_or_create(item=add_item_in_release_form.cleaned_data['item'],
                                                                          release=release,
                                                                          defaults={'count': add_item_in_release_form.cleaned_data['count']})
            if not create:
                item_in_release.count += add_item_in_release_form.cleaned_data['count']
            item_in_release.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Позиция успешно добавлена')
            return redirect('/releases/details/' + str(id) + '/')
        messages.add_message(request,
                 messages.ERROR,
                 add_item_in_release_form.errors.as_data())
        return redirect('/releases/details/' + str(id) + '/')
    else:
        add_item_in_release_form = ItemInReleaseForm()
    return render(request,
                    'add_item_in_release.html',
                    {'add_item_in_release_form': add_item_in_release_form,
                     'id': id})

@permission_required('storage.delete_iteminrelease')
@transaction.atomic
def delete_item_from_release(request, id):
    item_in_release = get_object_or_404(ItemInRelease, pk=id)
    release_id = item_in_release.release.pk
    item_in_storage = get_object_or_404(Storage,
                                        item=item_in_release.item.item,
                                        contract=item_in_release.item.contract)
    try:
        item_in_storage.count += item_in_release.count
        item_in_storage.save()
        item_in_release.delete()
    except Exception as e:
        messages.add_message(request,
                                messages.ERROR,
                                e)
    return redirect('/releases/details/' + str(release_id) + '/')

def get_width(num_characters):
    '''Function to get MS Excel row width according string lenght'''
    return int((1 + num_characters) * 256)

def export_storage_to_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    file_name = f'storage_report_{date.today()}.xls'
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    filters = {
        'item__category__id': request.GET.get('category'),
        'full_item_name__icontains': request.GET.get('text_filter'),
        'contract__id': request.GET.get('contract'),
    }
    filters = clean_filters(filters)
    by_contract = int(request.GET.get('by_contract'))
    columns_styles = []
    columns_styles.append(xlwt.easyxf('font: name Calibri, height 220; align: vert center;'))
    columns_styles.append(xlwt.easyxf('font: name Calibri, height 220; align: vert center, horiz center;'))
    columns_styles.append(xlwt.easyxf('font: name Calibri, height 220; align: vert center, horiz center;'))
    if by_contract:
        storage = get_storage_with_contract()
        columns_to_write = ['full_item_name', 'contract_number', 'unit', 'count']
        columns = ['Наименование', 'Договор', 'Ед. изм.', 'Кол-во']
        columns_styles.append(xlwt.easyxf('font: name Calibri, height 220; align: vert center, horiz center;'))
    else:
        storage = get_storage_common()
        columns_to_write = ['full_item_name', 'unit', 'total_count']
        columns = ['Наименование', 'Ед. изм.', 'Кол-во']
    if filters:
        storage = storage.filter(**filters)

    categories = Category.objects.all()

    wb = xlwt.Workbook(encoding='utf-8')

    for category in categories:
        rows = storage.filter(category=category)
        if not rows:
            continue
        ws = wb.add_sheet(category.name)
        row_num = 0
        header_style = xlwt.easyxf('font: bold 1, name Calibri, height 240; align: vert center, horiz center;')
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 30 * 20
        columns_width = []
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], header_style)
            columns_width.append(get_width(len(columns[col_num])))
        for row in rows:
            row_num += 1
            for col_num in range(len(columns_to_write)):
                ws.write(row_num, col_num, row[columns_to_write[col_num]], columns_styles[col_num])
                column_width = get_width(len(str(row[columns_to_write[col_num]])))
                if column_width > columns_width[col_num]:
                    columns_width[col_num] = column_width
        for col_num in range(len(columns_width)):
            ws.col(col_num).width = columns_width[col_num]
    
    wb.save(response)
    return response

def set_column_widths(ws, columns_widths):
    for i, width in enumerate(columns_widths):
        ws.col(i).width = width

def write_data(ws, row_num, data, style, columns_widths):
    for col_num, value in enumerate(data):
        ws.write(row_num, col_num, value, style)
        new_width = get_width(len(str(value)))
        if new_width > columns_widths[col_num]:
            columns_widths[col_num] = new_width

def generate_report_supplies_sheet(ws, items, item_model, styles):
    columns_widths = [0, 0, 0]
    row_num = 0
    for item_id, total_count in items:
        item = Item.objects.get(id=item_id)
        write_data(ws, row_num, [str(item), 'Всего', total_count], styles['totals_style'], columns_widths)
        row_num += 1
        for row in item_model.filter(item=item):
            write_data(ws, row_num, ['', row.supply.date.isoformat(), row.count], styles['default_style'], columns_widths)
            row_num += 1
    set_column_widths(ws, columns_widths)

def generate_report_releases_sheet(ws, item_totals, items_in_release, styles):
    columns_widths = [0, 0, 0, 0]
    row_num = 0
    for item_id, total_count in item_totals:
        #item = Storage.objects.get(id=storage_id).item
        item = Item.objects.get(id=item_id)
        write_data(ws, row_num, [str(item), 'Всего', total_count], styles['totals_style'], columns_widths)
        row_num += 1
        for row in items_in_release.filter(item__item__id=item.id):
            contract = Storage.objects.get(id=row.item.id).contract
            write_data(ws, row_num, ['', row.release.date.isoformat(), row.count, contract.short_number], styles['default_style'], columns_widths)
            row_num += 1
    set_column_widths(ws, columns_widths)

def report_by_contract(request):
    if request.method == 'POST':
        contract_id = request.POST['contract']
        contract = Contract.objects.get(id=contract_id)
        response = HttpResponse(content_type='application/ms-excel')
        file_name = f'contract_report_{contract.short_number}_{date.today().isoformat()}.xls'
        response['Content-Disposition'] = f"attachment; filename={escape_uri_path(file_name)}"
        
        wb = xlwt.Workbook(encoding='utf-8')
        styles = {'default_style': xlwt.easyxf('font: name Calibri, height 240; align: vert center, horiz left;'),
                  'totals_style': xlwt.easyxf('font: bold 1, name Calibri, height 240; align: vert center, horiz left;'),}
        
        # Поставки
        supplies = ItemInSupply.objects.filter(supply__contract=contract_id)
        supplies_group = supplies.values_list('item').annotate(total_count=Sum('count')).order_by('item')
        ws = wb.add_sheet('Поставки')
        generate_report_supplies_sheet(ws, supplies_group, supplies, styles)

        # Выдачи
        releases = ItemInRelease.objects.filter(release__contract=contract_id)
        releases_group = releases.values_list('item__item').annotate(total_count=Sum('count')).order_by('item__item')
        ws = wb.add_sheet('Выдачи')
        generate_report_releases_sheet(ws, releases_group, releases, styles)
        
        wb.save(response)
        return response
    else:
        report_by_contract_form = ReportByContractForm()
        return render(request, 'report_by_contract.html', {'report_by_contract_form': report_by_contract_form})