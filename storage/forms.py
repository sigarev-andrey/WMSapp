from django import forms
from django.forms import ModelForm
from django.db.models import F
from django.db.models.functions import Coalesce
from .models import *


class FilterForm(forms.Form):
    text_filter = forms.CharField(max_length=255, required=False)
    name_filter = forms.CharField(max_length=255, required=False)
    surname_filter = forms.CharField(max_length=255, required=False)
    patronymic_filter = forms.CharField(max_length=255, required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label='Не выбрана')
    contract = forms.ModelChoiceField(queryset=Contract.objects.all(), required=False, empty_label='Не выбран')
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['text_filter'].widget.attrs.update({
            'id': 'text_filter',
            'placeholder': 'Наименование'
        })
        self.fields['name_filter'].widget.attrs.update({
            'id': 'name_filter',
            'placeholder': 'Имя'
        })
        self.fields['surname_filter'].widget.attrs.update({
            'id': 'surname_filter',
            'placeholder': 'Фамилия'
        })
        self.fields['patronymic_filter'].widget.attrs.update({
            'id': 'patronymic_filter',
            'placeholder': 'Отчество'
        })
        self.fields['category'].widget.attrs.update({
            'id': 'category',
            'placeholder': 'Категория'
        })
        self.fields['contract'].widget.attrs.update({
            'id': 'contract',
            'placeholder': 'Договор'
        })
        self.fields['start_date'].widget = forms.widgets.DateInput(
            format=('%Y-%m-%d'),
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
        self.fields['end_date'].widget = forms.widgets.DateInput(
            format=('%Y-%m-%d'),
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )

class SupplyFilterForm(forms.Form):
    pass

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['username'].widget.attrs.update({
            'type': 'text',
            'placeholder': 'Имя пользователя',
            'aria-label': 'Имя пользователя',
            'aria-describedby': 'user-icon',
            'autocomplete': 'off'
        })
        self.fields['password'].widget.attrs.update({
            'type': 'password',
            'placeholder': 'Пароль',
            'aria-label': 'Пароль',
            'aria-describedby': 'pass-icon'
        })

class ManufacturerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['name'].widget.attrs.update({
                'id': 'manufacturer_name',
                'placeholder': 'Наименование'
        })

    class Meta:
        model = Manufacturer
        fields = ['name']

class UnitForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['name'].widget.attrs.update({
            'id': 'unit-name',
            'placeholder': 'Наименование'
        })

    class Meta:
        model = Unit
        fields = ['name']

class CategoryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['name'].widget.attrs.update({
            'id': 'category-name',
            'placeholder': 'Наименование'
        })

    class Meta:
        model = Category
        fields = ['name']

class ItemForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['article'].widget.attrs.update({
            'id': 'article',
            'placeholder': 'Артикул'
        })
        self.fields['category'].widget.attrs.update({
            'id': 'category_name',
            'placeholder': 'Категория'
        })
        self.fields['description'].widget.attrs.update({
            'id': 'description',
            'placeholder': 'Описание'
        })
        self.fields['unit'].widget.attrs.update({
            'id': 'unit_name',
            'placeholder': 'Ед. изм.'
        })

    class Meta:
        model = Item
        widgets = {
            'manufacturer': forms.TextInput(),
        }
        fields = ['manufacturer', 'article', 'category', 'description', 'unit']

class ContractForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget = forms.widgets.DateInput(
            format=('%Y-%m-%d'),
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
        self.fields['short_number'].widget.attrs.update({
            'class': 'form-control',
            'id': 'short_number',
            'placeholder': 'Короткий номер'
        })
        self.fields['full_number'].widget.attrs.update({
            'class': 'form-control',
            'id': 'full_number',
            'placeholder': 'Полный номер'
        })
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'id': 'description',
            'placeholder': 'Описание'
        })

    class Meta:
        model = Contract
        fields = ['short_number', 'full_number', 'date', 'description']

class SupplyForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['date'].widget = forms.widgets.DateInput(
            format=('%Y-%m-%d'),
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
        self.fields['contract'].widget.attrs.update({
            'id': 'contract'
        })

    class Meta:
        model = Supply
        fields = ['date', 'contract', 'description']

class CompanyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = Company
        fields = ['name']

class ItemInSupplyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['count'].widget.attrs.update({
            'id': 'count',
            'placeholder': 'Кол-во'
        })

    class Meta:
        model = ItemInSupply
        exclude = ['supply']

class StaffForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['name'].widget.attrs.update({
            'id': 'name',
            'placeholder': 'Имя'
        })
        self.fields['surname'].widget.attrs.update({
            'id': 'surname',
            'placeholder': 'Фамилия'
        })
        self.fields['patronymic'].widget.attrs.update({
            'id': 'patronymic',
            'placeholder': 'Отчество'
        })
        
    class Meta:
        model = Staff
        fields = ['name', 'surname', 'patronymic']

class ReleaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['date'].widget = forms.widgets.DateInput(
            format=('%Y-%m-%d'),
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
    
    class Meta:
        model = Release
        fields = ['date', 'contract', 'staff', 'company', 'description']

class ItemInReleaseForm(ModelForm):

    #for future usage for filtering items by contract
    contract = forms.ModelChoiceField(queryset=Contract.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
        self.fields['count'].widget.attrs.update({
            'id': 'count',
            'placeholder': 'Кол-во'
        })
        self.fields['contract'].widget.attrs.update({
            'id': 'contract',
        })
        #self.fields['item'].queryset = Storage.objects.filter(count__gt=0)
        qs = Storage.objects.all().annotate(manufacturer_name=F('item__manufacturer__name'),
                                            item_article=F('item__article'),
                                            item_description=F('item__description')).filter(count__gt=0)
        self.fields['item'].queryset = qs
            
    class Meta:
        model = ItemInRelease
        widgets = {
            'item': forms.TextInput(),
        }
        exclude = ['release']

class ReportByContractForm(forms.Form):
    contract = forms.ModelChoiceField(queryset=Contract.objects.all(), required=True, empty_label='Не выбран')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contract'].widget.attrs.update({
            'class': 'form-control',
            'id': 'contract',
            'placeholder': 'Договор',
            'required': 'required'
        })

class ReportCommonForm(forms.Form):
    text_filter = forms.CharField(max_length=255, required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label='Не выбрана')
    with_contract = forms.BooleanField(required=False)
    contract = forms.ModelChoiceField(queryset=Contract.objects.all(), required=False, disabled=True, empty_label='Не выбран')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['text_filter'].widget.attrs.update({
            'class': 'form-control',
            'id': 'text_filter',
            'placeholder': 'Наименование'
        })
        self.fields['category'].widget.attrs.update({
            'class': 'form-control',
            'id': 'category',
            'placeholder': 'Категория'
        })
        self.fields['with_contract'].widget.attrs.update({
            'class': 'form-check-input',
            'id': 'with-contract'
        })
        self.fields['contract'].widget.attrs.update({
            'class': 'form-control',
            'id': 'contract',
            'placeholder': 'Договор'
        })