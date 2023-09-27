from django import forms
from django.forms import ModelForm
from .models import *

class StorageFilterForm(forms.Form):
    text_filter = forms.CharField(max_length=255, required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label='Не выбрана')
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
        self.fields['category'].widget.attrs.update({
            'id': 'category',
            'placeholder': 'Категория'
        })

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
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
        self.fields['manufacturer'].widget.attrs.update({
            'id': 'maufacturer_name',
            'placeholder': 'Производитель'
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
        self.fields['date'].widget = forms.widgets.DateInput(
            format=('%Y-%m-%d'),
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )

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
    #contract = forms.ModelChoiceField(queryset=Contract.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
            
    class Meta:
        model = ItemInRelease
        exclude = ['release']