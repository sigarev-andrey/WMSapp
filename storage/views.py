from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseForbidden
from .models import Storage, Category, Manufacturer, Unit
from django.db import transaction
from django.db.models import CharField, Value, Sum, F
from django.db.models.functions import Concat
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from .forms import *

def clean_filters(filters):
    filters = {k: v for (k, v) in filters.items() if v}
    return filters

@permission_required('storage.view_storage')
def storage(request):
    storage = Storage.objects.all()
    storage = storage.annotate(full_item_name=Concat('item__manufacturer__name', Value(' '), 'item__article', Value(' '),
                                                     'item__description', output_field=CharField()))
    storage = storage.values('full_item_name', unit=F('item__unit__name'), category=F('item__category__name')).order_by('full_item_name').annotate(total_count=Sum('count'))
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
    paginator = Paginator(storage, 10)
    page_number = request.GET.get('page')
    page_storage = paginator.get_page(page_number)
    filter_form = StorageFilterForm(initial=html_queries)
    if request.method == 'POST':
        filter_form = StorageFilterForm(request.POST)
        filters = {
            'item__category__id': request.POST.get('category'),
            'full_item_name__icontains': request.POST.get('text_filter')
        }
        filters = clean_filters(filters)
        html_queries = {
            'category': request.POST.get('category'),
            'text_filter': request.POST.get('text_filter'),
        }
        html_queries = clean_filters(html_queries)
        if filters:
            storage = storage.filter(**filters)
        paginator = Paginator(storage, 10)
        page_number = request.GET.get('page')
        page_storage = paginator.get_page(page_number)
    return render(request,
                  'storage.html',
                  {'storage': page_storage,
                   'filter_form': filter_form,
                   'filters': html_queries})

@permission_required('storage.view_manufacturers')
def manufacturers(request):
    manufacturers = Manufacturer.objects.all()
    return render(request,
                  'manufacturers.html',
                  {'manufacturers': manufacturers})

@permission_required('storage.add_manufacturers')
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

@permission_required('storage.edit_manufacturers')
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
    
@permission_required('storage.delete_manufacturers')
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

@permission_required("storage.view_unit")
def units(request):
    units = Unit.objects.all()
    return render(request,
                  'units.html',
                  {'units': units})

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

def categories(request):
    context = {}
    categories = Category.objects.all()
    context['categories'] = categories
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
        context['add_category_form'] = add_category_form
    return render(request,
                  'categories.html',
                   context)

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

def companies(request):
    companies = Company.objects.all()
    return render(request,
                  'companies.html',
                  {'companies': companies})

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

def items(request):
    items = Item.objects.all()
    paginator = Paginator(items, 10)
    page_number = request.GET.get('page')
    page_items = paginator.get_page(page_number)
    if (request.method == 'POST'):
        add_item_form = ItemForm(request.POST)
        if add_item_form.is_valid:
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Позиция успешно добавлена')
            add_item_form.save()
            return redirect('/items/')
    else:
        add_item_form = ItemForm()
    return render(request,
                  'items.html',
                  {'items': page_items,
                   'add_item_form': add_item_form})

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

def contracts(request):
    contracts = Contract.objects.all()
    if (request.method == 'POST'):
        add_contract_form = ContractForm(request.POST)
        if add_contract_form.is_valid:
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Договор успешно добавлена')
            add_contract_form.save()
            return redirect('/contracts/')
    else:
        add_contract_form = ContractForm()
    return render(request,
                  'contracts.html',
                  {'contracts': contracts,
                   'add_contract_form': add_contract_form})

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

def supplies(request):
    supplies = Supply.objects.all()
    return render(request,
                  'supplies.html',
                  {'supplies': supplies})

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

def details_supply(request, id):
    supply = get_object_or_404(Supply, pk=id)
    items = ItemInSupply.objects.filter(supply=supply.pk)
    return render(request,
                  'details_supply.html',
                  {'supply': supply,
                   'items': items})

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
            add_item_in_supply_form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Позиция успешно добавлена')
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

def staff(request):
    staff = Staff.objects.all()
    return render(request,
                  'staff.html',
                  {'staff': staff})

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

def releases(request):
    releases = Release.objects.all()
    return render(request,
                  'releases.html',
                  {'releases': releases})

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

def details_release(request, id=None):
    release = get_object_or_404(Release, pk=id)
    items = ItemInRelease.objects.filter(release=release.pk)
    return render(request,
                  'details_release.html',
                  {'release': release,
                   'items': items})

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