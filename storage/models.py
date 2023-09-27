from django.db import models
from django.db.models.functions import Lower

class Manufacturer(models.Model):
    name = models.CharField(max_length=250)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name=('unique_manufacrurer_name')
            )
        ]
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self) -> str:
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self) -> str:
        return self.name

class Unit(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self) -> str:
        return self.name

class Item(models.Model):
    manufacturer = models.ForeignKey(Manufacturer,
                                     on_delete=models.PROTECT,
                                     related_name='item_manufacturer')
    article = models.CharField(max_length=250)
    category = models.ForeignKey(Category,
                                 on_delete=models.PROTECT,
                                 related_name='item_category')
    description = models.TextField()
    unit = models.ForeignKey(Unit,
                             on_delete=models.PROTECT,
                             related_name='item_unit')

    class Meta:
        unique_together = ('manufacturer', 'article')
        ordering = ['article']
        indexes = [
            models.Index(fields=['article'])
        ]

    def __str__(self) -> str:
        return self.manufacturer.name + " " + self.article + " " + self.description

class Contract(models.Model):
    short_number = models.CharField(max_length=250)
    full_number = models.CharField(max_length=250, blank=True)
    date = models.DateField(null=True)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('short_number', 'full_number', 'date')

    def __str__(self) -> str:
        str = self.short_number
        if self.date:
            str += ' от ' + self.date.strftime('%d.%m.%Y')
        return str
    
class Storage(models.Model):
    item = models.ForeignKey(Item,
                             on_delete=models.PROTECT,
                             related_name='storage_item')
    contract = models.ForeignKey(Contract,
                                 on_delete=models.PROTECT,
                                 related_name='storage_contract')
    count = models.PositiveIntegerField()

    class Meta:
        unique_together = ('item', 'contract')

    def __str__(self) -> str:
        return self.item.manufacturer.name + " " + self.item.article + " " + self.contract.short_number + " " + str(self.count)

class Supply(models.Model):
    date = models.DateField()
    contract = models.ForeignKey(Contract,
                                 on_delete=models.PROTECT,
                                 related_name='supply_contract')
    description = models.TextField(blank=True)
    items = models.ManyToManyField(Item, through='ItemInSupply')

class ItemInSupply(models.Model):
    item = models.ForeignKey(Item,
                             on_delete=models.PROTECT)
    supply = models.ForeignKey(Supply,
                               on_delete=models.PROTECT)
    count = models.PositiveIntegerField()

class Staff(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.surname + ' ' + self.name[0] + '. ' + self.patronymic[0] + '.'

class Company(models.Model):
    name = models.CharField(max_length=250)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name=('unique_company_name')
            )
        ]
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]

    def __str__(self) -> str:
        return self.name
    
class Release(models.Model):
    date = models.DateField()
    contract = models.ForeignKey(Contract,
                                 on_delete=models.PROTECT)
    staff = models.ForeignKey(Staff,
                              on_delete=models.PROTECT)
    company = models.ForeignKey(Company,
                                on_delete=models.PROTECT)
    description = models.TextField(blank=True)
    items = models.ManyToManyField(Storage, through='ItemInRelease')
    
    class Meta:
        unique_together = ('date', 'contract', 'staff', 'company')
        ordering = ['date']

class ItemInRelease(models.Model):
    item = models.ForeignKey(Storage,
                             on_delete=models.PROTECT)
    release = models.ForeignKey(Release,
                                on_delete=models.PROTECT)
    count = models.PositiveIntegerField()

    class Meta:
        unique_together = ('item', 'release')
        ordering = ['item']
