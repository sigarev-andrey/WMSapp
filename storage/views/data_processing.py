from ..models import Storage, Item
from django.db.models.functions import Concat
from django.db.models import CharField, Value, Sum, F

def clean_filters(filters):
    '''Function to return only filled filter fields'''
    return {k: v for k, v in filters.items() if v}

def get_storage_common():
    '''Function to return storage dataset without contract and summed count of same items'''
    return (Storage.objects.all()
            .annotate(
                full_item_name=Concat(
                    'item__manufacturer__name', Value(' '),
                    'item__article', Value(' '),
                    'item__description',
                    output_field=CharField()
                )
            )
            .values(
                'full_item_name',
                unit=F('item__unit__name'),
                category=F('item__category__name')
            )
            .order_by('full_item_name')
            .annotate(total_count=Sum('count'))
            .filter(total_count__gt=0))

def get_storage_with_contract():
    '''Function to return storage dataset with contract of each item'''
    return (Storage.objects.all()
            .annotate(
                full_item_name=Concat(
                    'item__manufacturer__name', Value(' '),
                    'item__article', Value(' '),
                    'item__description',
                    output_field=CharField()
                ),
                category=F('item__category__name'),
                unit=F('item__unit__name'),
                contract_number=F('contract__short_number')
            )
            .values('full_item_name', 'category', 'contract',
                    'contract_number', 'unit', 'count')
            .filter(count__gt=0))

def get_items():
    '''Function to return items dataset with '''
    return (Item.objects.all()
            .annotate(
                full_item_name=Concat(
                    'manufacturer__name',
                     Value(' '),
                    'article', Value(' '),
                    'description',
                    output_field=CharField())))