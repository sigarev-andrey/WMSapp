from .data_processing import clean_filters, get_storage_common, get_storage_with_contract
from ..models import Category, Item, ItemInSupply, Storage, Contract, ItemInRelease
from ..forms import ReportByContractForm, ReportCommonForm
from django.db.models import Sum
from django.utils.encoding import escape_uri_path
from django.shortcuts import render
from django.http import HttpResponse
from datetime import date
from dataclasses import dataclass
import xlwt


# Базовые константы
EXCEL_FONT_HEIGHT = 220
EXCEL_HEADER_FONT_HEIGHT = 240


@dataclass
class ExcelStyles:
    """Стили для Excel отчетов"""
    default = xlwt.easyxf('font: name Calibri, height 220; align: vert center;')
    centered = xlwt.easyxf('font: name Calibri, height 220; align: vert center, horiz center;')
    header = xlwt.easyxf('font: bold 1, name Calibri, height 240; align: vert center, horiz center;')
    totals = xlwt.easyxf('font: bold 1, name Calibri, height 240; align: vert center, horiz left;')

def get_width(num_characters):
    '''Function to get MS Excel row width according string lenght'''
    return int((1 + num_characters) * 256)

def report_common(request):
    if request.method == 'POST':
        response = HttpResponse(content_type='application/ms-excel')
        file_name = f'storage_report_{date.today()}.xls'
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        filters = {
            'item__category__id': request.POST.get('category'),
            'full_item_name__icontains': request.POST.get('text_filter'),
            'contract__id': request.POST.get('contract'),
        }
        filters = clean_filters(filters)
        by_contract = request.POST.get('with_contract')
        columns_styles = []
        columns_styles.append(xlwt.easyxf('font: name Calibri, height 220; align: vert center;'))
        columns_styles.append(xlwt.easyxf('font: name Calibri, height 220; align: vert center, horiz center;'))
        columns_styles.append(xlwt.easyxf('font: name Calibri, height 220; align: vert center, horiz center;'))
        if by_contract:
            storage = get_storage_with_contract()
            columns_to_write = ['full_item_name', 'contract_number', 'unit', 'count']
            columns = ['Наименование', 'Договор', 'Ед. изм.', 'Кол-во']
            columns_styles.append(xlwt.easyxf('font: name Calibri, height 220; align: vert center, horiz center;'))
        else:
            storage = get_storage_common()
            columns_to_write = ['full_item_name', 'unit', 'total_count']
            columns = ['Наименование', 'Ед. изм.', 'Кол-во']
        if filters:
            storage = storage.filter(**filters)

        categories = Category.objects.all()

        wb = xlwt.Workbook(encoding='utf-8')

        for category in categories:
            rows = storage.filter(category=category)
            if not rows:
                continue
            ws = wb.add_sheet(category.name)
            row_num = 0
            header_style = xlwt.easyxf('font: bold 1, name Calibri, height 240; align: vert center, horiz center;')
            ws.row(row_num).height_mismatch = True
            ws.row(row_num).height = 30 * 20
            columns_width = []
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], header_style)
                columns_width.append(get_width(len(columns[col_num])))
            for row in rows:
                row_num += 1
                for col_num in range(len(columns_to_write)):
                    ws.write(row_num, col_num, row[columns_to_write[col_num]], columns_styles[col_num])
                    column_width = get_width(len(str(row[columns_to_write[col_num]])))
                    if column_width > columns_width[col_num]:
                        columns_width[col_num] = column_width
            for col_num in range(len(columns_width)):
                ws.col(col_num).width = columns_width[col_num]
        
        wb.save(response)
        return response
    else:
        report_common_form = ReportCommonForm()
        return render(request, 'report_common.html', {'report_common_form': report_common_form})

def set_column_widths(ws, columns_widths):
    for i, width in enumerate(columns_widths):
        ws.col(i).width = width

def write_data(ws, row_num, data, style, columns_widths):
    for col_num, value in enumerate(data):
        ws.write(row_num, col_num, value, style)
        new_width = get_width(len(str(value)))
        if new_width > columns_widths[col_num]:
            columns_widths[col_num] = new_width

def generate_report_supplies_sheet(ws, items, item_model, styles):
    columns_widths = [0, 0, 0]
    row_num = 0
    for item_id, total_count in items:
        item = Item.objects.get(id=item_id)
        write_data(ws, row_num, [str(item), 'Всего', total_count], styles['totals_style'], columns_widths)
        row_num += 1
        for row in item_model.filter(item=item):
            write_data(ws, row_num, ['', row.supply.date.isoformat(), row.count], styles['default_style'], columns_widths)
            row_num += 1
    set_column_widths(ws, columns_widths)

def generate_report_releases_sheet(ws, item_totals, items_in_release, styles):
    columns_widths = [0, 0, 0, 0]
    row_num = 0
    for item_id, total_count in item_totals:
        #item = Storage.objects.get(id=storage_id).item
        item = Item.objects.get(id=item_id)
        write_data(ws, row_num, [str(item), 'Всего', total_count], styles['totals_style'], columns_widths)
        row_num += 1
        for row in items_in_release.filter(item__item__id=item.id):
            contract = Storage.objects.get(id=row.item.id).contract
            write_data(ws, row_num, ['', row.release.date.isoformat(), row.count, contract.short_number], styles['default_style'], columns_widths)
            row_num += 1
    set_column_widths(ws, columns_widths)

def report_by_contract(request):
    if request.method == 'POST':
        contract_id = request.POST.get('contract')
        contract = Contract.objects.get(id=contract_id)
        response = HttpResponse(content_type='application/ms-excel')
        file_name = f'contract_report_{contract.short_number}_{date.today().isoformat()}.xls'
        response['Content-Disposition'] = f"attachment; filename={escape_uri_path(file_name)}"
        
        wb = xlwt.Workbook(encoding='utf-8')
        styles = {'default_style': xlwt.easyxf('font: name Calibri, height 240; align: vert center, horiz left;'),
                  'totals_style': xlwt.easyxf('font: bold 1, name Calibri, height 240; align: vert center, horiz left;'),}
        
        # Поставки
        supplies = ItemInSupply.objects.filter(supply__contract=contract_id)
        supplies_group = supplies.values_list('item').annotate(total_count=Sum('count')).order_by('item')
        ws = wb.add_sheet('Поставки')
        generate_report_supplies_sheet(ws, supplies_group, supplies, styles)

        # Выдачи
        releases = ItemInRelease.objects.filter(release__contract=contract_id)
        releases_group = releases.values_list('item__item').annotate(total_count=Sum('count')).order_by('item__item')
        ws = wb.add_sheet('Выдачи')
        generate_report_releases_sheet(ws, releases_group, releases, styles)
        
        wb.save(response)
        return response
    else:
        report_by_contract_form = ReportByContractForm()
        return render(request, 'report_by_contract.html', {'report_by_contract_form': report_by_contract_form})