from django.contrib import admin
from .models import Manufacturer
from .models import Category
from .models import Unit
from .models import Item
from .models import Storage
from .models import Contract
from .models import ItemInRelease

admin.site.register(Category)
admin.site.register(Unit)
admin.site.register(Contract)
admin.site.register(ItemInRelease)

class ItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'category')
    search_fields = ['manufacturer__name', 'article', 'description']
    list_filter = ['manufacturer', 'category']
    list_per_page = 15

admin.site.register(Item, ItemAdmin)

class StorageAdmin(admin.ModelAdmin):
    list_display = ('item', 'get_unit', 'count', 'get_category')
    search_fields = ['item__manufacturer__name', 'item__article', 'item__description']
    list_filter = ['item__manufacturer', 'item__category']
    list_per_page = 15

    @admin.display(ordering='item__unit', description='Unit')
    def get_unit(self, obj):
        return obj.item.unit
    
    @admin.display(ordering='item__category', description='Category')
    def get_category(self, obj):
        return obj.item.category

admin.site.register(Storage, StorageAdmin)

class ManufacturerAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_per_page = 15

admin.site.register(Manufacturer, ManufacturerAdmin)