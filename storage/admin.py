from django.contrib import admin
from .models import Manufacturer
from .models import Category
from .models import Unit
from .models import Item
from .models import Storage
from .models import Contract
from .models import ItemInRelease

admin.site.register(Manufacturer)
admin.site.register(Category)
admin.site.register(Unit)
admin.site.register(Item)
admin.site.register(Storage)
admin.site.register(Contract)
admin.site.register(ItemInRelease)