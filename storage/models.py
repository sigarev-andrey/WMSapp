from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.db.models import UniqueConstraint

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
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'

    def __str__(self) -> str:
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]
        verbose_name = 'Катагория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.name

class Unit(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name'])
        ]
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'

    def __str__(self) -> str:
        return self.name

class Item(models.Model):
    manufacturer = models.ForeignKey(Manufacturer,
                                     on_delete=models.PROTECT,
                                     related_name='item_manufacturer',
                                     null=True,
                                     blank=True)
    article = models.CharField(max_length=250)
    category = models.ForeignKey(Category,
                                 on_delete=models.PROTECT,
                                 related_name='item_category')
    description = models.TextField(blank=True)
    unit = models.ForeignKey(Unit,
                             on_delete=models.PROTECT,
                             related_name='item_unit')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['manufacturer', 'article'],
                             name='with_manufacturer'),
            UniqueConstraint(fields=['article'],
                             condition=Q(manufacturer=None),
                             name='without_manufacturer'),
        ]
        ordering = ['manufacturer', 'article']
        indexes = [
            models.Index(fields=['manufacturer', 'article'])
        ]
        verbose_name = 'Позиция'
        verbose_name_plural = 'Позиции'

    def __str__(self) -> str:
        s = self.article
        if self.manufacturer:
            s = self.manufacturer.name + ' ' + s
        if self.description:
            s += ' ' + self.description
        return s

class Contract(models.Model):
    short_number = models.CharField(max_length=250)
    full_number = models.CharField(max_length=250, blank=True)
    date = models.DateField(null=True)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('short_number', 'full_number', 'date')
        ordering = ['date']
        verbose_name = 'Договор'
        verbose_name_plural = 'Договоры'

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
        ordering = ['item', 'contract']
        verbose_name = 'Позиция на складе'
        verbose_name_plural = 'Позиции на складе'
    
    def __str__(self) -> str:
        s = self.item.article + ' ' + self.contract.short_number + ' ' + str(self.count)
        if self.item.manufacturer:
            s = self.item.manufacturer.name + ' ' + s
        return s

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
        verbose_name = 'Фирма'
        verbose_name_plural = 'Фирмы'

    def __str__(self) -> str:
        return self.name
    
class Release(models.Model):
    date = models.DateField()
    contract = models.ForeignKey(Contract,
                                 on_delete=models.PROTECT)
    staff = models.ForeignKey(Staff,
                              on_delete=models.PROTECT,
                              null=True,
                              blank=True)
    company = models.ForeignKey(Company,
                                on_delete=models.PROTECT)
    description = models.TextField(blank=True)
    items = models.ManyToManyField(Storage, through='ItemInRelease')
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['date', 'contract', 'staff', 'company'],
                             name='with_staff'),
            UniqueConstraint(fields=['date', 'contract', 'company'],
                             condition=Q(staff=None),
                             name='without_staff'),
        ]
        ordering = ['date']
        constraints = [
            UniqueConstraint(fields=['date', 'contract', 'staff', 'company'],
                             name='with_staff'),
            UniqueConstraint(fields=['date', 'contract', 'company'],
                             condition=Q(staff=None),
                             name='without_staff'),
        ]

class ItemInRelease(models.Model):
    item = models.ForeignKey(Storage,
                             on_delete=models.PROTECT)
    release = models.ForeignKey(Release,
                                on_delete=models.PROTECT)
    count = models.PositiveIntegerField()

    class Meta:
        unique_together = ('item', 'release')
        ordering = ['item']
