from django import forms
from django.contrib.auth.forms import AuthenticationForm

from storage import forms as desktop
from storage.models import Category, Contract, Item, Storage


LABELS = {
    'name': 'Наименование', 'article': 'Артикул', 'manufacturer': 'Производитель',
    'category': 'Категория', 'unit': 'Единица измерения', 'description': 'Примечание',
    'short_number': 'Короткий номер', 'full_number': 'Полный номер', 'date': 'Дата',
    'contract': 'Договор', 'staff': 'Сотрудник', 'company': 'Организация',
    'surname': 'Фамилия', 'patronymic': 'Отчество',
}


def prepare_form(form):
    """Adapt existing model forms without modifying the desktop widgets."""
    for name, field in form.fields.items():
        field.label = LABELS.get(name, field.label)
        if isinstance(field, forms.ModelChoiceField):
            field.widget = forms.Select(choices=field.choices)
        elif isinstance(field, forms.DateField):
            field.widget = forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'})
        elif isinstance(field.widget, forms.Textarea):
            field.widget.attrs['rows'] = 4
    if isinstance(form, desktop.StaffForm):
        form.fields['name'].label = 'Имя'
    return form


class MobileAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={
        'autocomplete': 'username', 'autocapitalize': 'none', 'autofocus': True,
    }))
    password = forms.CharField(label='Пароль', strip=False, widget=forms.PasswordInput(attrs={
        'autocomplete': 'current-password',
    }))


class SearchForm(forms.Form):
    q = forms.CharField(label='Поиск', max_length=255, required=False,
                        widget=forms.TextInput(attrs={'type': 'search', 'placeholder': 'Найти по названию или артикулу'}))


class StockFilterForm(SearchForm):
    category = forms.ModelChoiceField(label='Категория', queryset=Category.objects.all(),
                                     required=False, empty_label='Все категории')


class ContractStockFilterForm(StockFilterForm):
    contract = forms.ModelChoiceField(label='Договор', queryset=Contract.objects.all(),
                                     required=False, empty_label='Все договоры')


class DocumentFilterForm(SearchForm):
    contract = forms.ModelChoiceField(label='Договор', queryset=Contract.objects.all(),
                                     required=False, empty_label='Все договоры')
    start_date = forms.DateField(label='С даты', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='По дату', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def clean(self):
        data = super().clean()
        if data.get('start_date') and data.get('end_date') and data['start_date'] > data['end_date']:
            self.add_error('end_date', 'Конечная дата должна быть не раньше начальной.')
        return data


class StockChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.item} · {obj.contract.short_number} · {obj.count} {obj.item.unit}'


class SupplyLineForm(forms.Form):
    item = forms.ModelChoiceField(label='Позиция', queryset=Item.objects.select_related('manufacturer', 'unit'),
                                 empty_label='Выберите позицию')
    count = forms.IntegerField(label='Количество', min_value=1, widget=forms.NumberInput(attrs={'inputmode': 'numeric'}))


class ReleaseLineForm(SupplyLineForm):
    item = StockChoiceField(label='Позиция на складе', queryset=Storage.objects.filter(count__gt=0).select_related(
        'item__manufacturer', 'item__unit', 'contract'), empty_label='Выберите позицию и договор',
        help_text='В списке указаны договор хранения и доступный остаток.')


class ReportForm(ContractStockFilterForm):
    with_contract = forms.BooleanField(label='Разбить остатки по договорам', required=False)


class ContractReportForm(forms.Form):
    contract = forms.ModelChoiceField(label='Договор', queryset=Contract.objects.all(), empty_label='Выберите договор')
