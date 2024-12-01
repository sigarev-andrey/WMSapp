from django.contrib import admin
from .models import Manufacturer
from .models import Category
from .models import Unit
from .models import Item
from .models import Storage
from .models import Contract
from .models import ItemInRelease

class CategoryAdmin(admin.ModelAdmin):
    list_per_page = 15

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Категории'}
        return super(CategoryAdmin, self).changelist_view(request, extra_context=extra_context)

admin.site.register(Category, CategoryAdmin)

class UnitAdmin(admin.ModelAdmin):
    list_per_page = 15

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Единицы измерения'}
        return super(UnitAdmin, self).changelist_view(request, extra_context=extra_context)

admin.site.register(Unit, UnitAdmin)

class ContractAdmin(admin.ModelAdmin):
    list_per_page = 15

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Категории'}
        return super(ContractAdmin, self).changelist_view(request, extra_context=extra_context)

admin.site.register(Contract, ContractAdmin)

class ItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category')
    search_fields = ['manufacturer__name', 'article', 'description']
    list_filter = ['manufacturer', 'category']
    autocomplete_fields = ['manufacturer']
    list_per_page = 15

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Позиции'}
        return super(ItemAdmin, self).changelist_view(request, extra_context=extra_context)

admin.site.register(Item, ItemAdmin)

class StorageAdmin(admin.ModelAdmin):
    list_display = ('item', 'get_contract','get_unit', 'count', 'get_category')
    search_fields = ['item__manufacturer__name', 'item__article', 'item__description']
    list_filter = ['item__manufacturer', 'item__category']
    autocomplete_fields = ['item']
    list_per_page = 15

    @admin.display(ordering='item__unit', description='Unit')
    def get_unit(self, obj):
        return obj.item.unit
    
    @admin.display(ordering='storage__category', description='Category')
    def get_category(self, obj):
        return obj.item.category
    
    @admin.display(ordering='contract__short_number', description='Contract')
    def get_contract(self, obj):
        return obj.contract.short_number

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Позиции на складе'}
        return super(StorageAdmin, self).changelist_view(request, extra_context=extra_context)

admin.site.register(Storage, StorageAdmin)

class ManufacturerAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_per_page = 15

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Производители'}
        return super(ManufacturerAdmin, self).changelist_view(request, extra_context=extra_context)

admin.site.register(Manufacturer, ManufacturerAdmin)