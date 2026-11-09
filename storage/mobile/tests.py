from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from storage.models import (
    Category, Company, Contract, Item, ItemInRelease, ItemInSupply,
    Manufacturer, Release, Staff, Storage, Supply, Unit,
)
from .views import DIRECTORIES


class MobileTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser('warehouse', 'test@example.com', 'test-pass')
        cls.reader = get_user_model().objects.create_user('reader', password='test-pass')
        cls.reader.user_permissions.add(*Permission.objects.filter(codename__startswith='view_', content_type__app_label='storage'))
        cls.category = Category.objects.create(name='Крепёж')
        cls.other_category = Category.objects.create(name='Кабель')
        cls.unit = Unit.objects.create(name='шт.')
        cls.manufacturer = Manufacturer.objects.create(name='Завод')
        cls.item = Item.objects.create(article='M8', description='Болт', category=cls.category, unit=cls.unit, manufacturer=cls.manufacturer)
        cls.other_item = Item.objects.create(article='ВВГ', description='Кабель', category=cls.other_category, unit=cls.unit)
        cls.contract = Contract.objects.create(short_number='А-01', date=date(2026, 1, 1))
        cls.other_contract = Contract.objects.create(short_number='Б-02', date=date(2026, 2, 1))
        cls.company = Company.objects.create(name='Монтаж')
        cls.staff = Staff.objects.create(surname='Иванов', name='Иван', patronymic='Иванович')
        cls.stock = Storage.objects.create(item=cls.item, contract=cls.contract, count=20)
        cls.other_stock = Storage.objects.create(item=cls.item, contract=cls.other_contract, count=5)
        Storage.objects.create(item=cls.other_item, contract=cls.contract, count=0)
        cls.supply = Supply.objects.create(date=date(2026, 3, 10), contract=cls.contract, description='Первая поставка')
        cls.release = Release.objects.create(date=date(2026, 3, 11), contract=cls.contract, company=cls.company)

    def setUp(self):
        self.client.force_login(self.user)

    def url(self, name, **kwargs):
        return reverse(f'mobile:{name}', kwargs=kwargs)

    def test_anonymous_is_redirected_to_mobile_login_with_original_query(self):
        self.client.logout()
        response = self.client.get('/mobile/releases/?q=Монтаж')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/mobile/login/?next='))
        self.assertIn('releases', response.url)
        self.assertTrue(self.client.get('/mobile').url.startswith('/mobile/login/'))
        self.assertEqual(self.client.get('/mobile/login/').status_code, 200)
        self.assertEqual(self.client.get('/storage/').url, '/login/')

    def test_login_returns_to_mobile_document(self):
        self.client.logout()
        response = self.client.post('/mobile/login/', {'username': 'warehouse', 'password': 'test-pass', 'next': '/mobile/supplies/'})
        self.assertRedirects(response, '/mobile/supplies/')

    def test_login_rejects_external_redirect(self):
        self.client.logout()
        response = self.client.post('/mobile/login/', {'username': 'warehouse', 'password': 'test-pass', 'next': 'https://example.com/'})
        self.assertRedirects(response, '/mobile/')

    def test_login_without_stock_permission_goes_to_menu(self):
        get_user_model().objects.create_user('new-user', password='test-pass')
        self.client.logout()
        response = self.client.post('/mobile/login/', {'username': 'new-user', 'password': 'test-pass'})
        self.assertRedirects(response, '/mobile/menu/')

    def test_bad_login_has_inline_error(self):
        self.client.logout()
        response = self.client.post('/mobile/login/', {'username': 'warehouse', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_logout_requires_post(self):
        self.assertEqual(self.client.get('/mobile/logout/').status_code, 405)
        self.assertRedirects(self.client.post('/mobile/logout/'), '/mobile/login/')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_stock_aggregates_contracts_and_excludes_zero_stock(self):
        response = self.client.get('/mobile/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mobile/stock.html')
        rows = list(response.context['page_obj'])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['total_count'], 25)
        self.assertContains(response, 'viewport-fit=cover')
        self.assertNotContains(response, 'jquery')

    def test_stock_contract_mode_and_filters(self):
        response = self.client.get('/mobile/', {'mode': 'contracts', 'contract': self.contract.pk, 'category': self.category.pk, 'q': 'M8'})
        self.assertEqual(response.status_code, 200)
        rows = list(response.context['page_obj'])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['count'], 20)
        self.assertIn('contract', response.context['filter_form'].fields)
        self.assertNotIn('contract=', response.context['common_mode_query'])
        response = self.client.get('/mobile/', {'contract': self.other_contract.pk})
        self.assertEqual(list(response.context['page_obj'])[0]['total_count'], 25)
        self.assertNotIn('contract', response.context['filter_form'].fields)
        self.assertFalse(response.context['has_filters'])
        self.assertNotIn('contract=', response.context['page_query'])
        response = self.client.get('/mobile/', {'contract': 'outdated', 'q': 'M8', 'category': self.category.pk})
        self.assertFalse(response.context['filter_form'].errors)
        self.assertEqual(list(response.context['page_obj'])[0]['total_count'], 25)

    def test_mode_alone_does_not_count_as_filter(self):
        response = self.client.get('/mobile/', {'mode': 'contracts'})
        self.assertFalse(response.context['has_filters'])

    def test_invalid_filters_show_errors_instead_of_server_error(self):
        for path, data in [('/mobile/', {'category': 'oops'}), ('/mobile/supplies/', {'start_date': 'bad'}),
                           ('/mobile/releases/', {'start_date': '2026-11-02', 'end_date': '2026-01-01'})]:
            with self.subTest(path=path):
                response = self.client.get(path, data)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['filter_form'].errors)
                self.assertEqual(response.context['page_obj'].paginator.count, 0)

    def test_document_search_and_dates(self):
        response = self.client.get('/mobile/releases/', {'q': 'Монтаж', 'start_date': '2026-03-01', 'end_date': '2026-03-31'})
        self.assertEqual(list(response.context['page_obj']), [self.release])
        response = self.client.get('/mobile/supplies/', {'start_date': '2026-04-01'})
        self.assertEqual(response.context['page_obj'].paginator.count, 0)

    def test_pagination_preserves_filters_and_handles_invalid_page(self):
        for index in range(18):
            Supply.objects.create(date=date(2026, 4, 1), contract=self.contract, description=f'bolt & nut {index}')
        response = self.client.get('/mobile/supplies/', {'q': 'bolt & nut', 'contract': self.contract.pk})
        self.assertTrue(response.context['page_obj'].has_next())
        self.assertContains(response, 'q=bolt+%26+nut&amp;contract=')
        response = self.client.get('/mobile/supplies/', {'q': 'bolt & nut', 'page': '9999'})
        self.assertEqual(response.context['page_obj'].number, 2)
        self.assertEqual(self.client.get('/mobile/supplies/?page=bad').status_code, 200)

    def test_all_directories_forms_and_document_pages_render(self):
        for kind in DIRECTORIES:
            for name in ('directory', 'directory-add'):
                with self.subTest(kind=kind, name=name):
                    self.assertEqual(self.client.get(self.url(name, kind=kind)).status_code, 200)
        for kind, document in [('supplies', self.supply), ('releases', self.release)]:
            for name in ('document-detail', 'document-edit', 'document-delete', 'line-add'):
                with self.subTest(kind=kind, name=name):
                    self.assertEqual(self.client.get(self.url(name, kind=kind, pk=document.pk)).status_code, 200)
            self.assertEqual(self.client.get(self.url('document-add', kind=kind)).status_code, 200)
        for kind in ('stock', 'contract'):
            self.assertEqual(self.client.get(self.url('report', kind=kind)).status_code, 200)

    def test_unknown_resource_is_not_exposed(self):
        for path in ('/mobile/users/', '/mobile/directories/users/', '/mobile/reports/users/'):
            self.assertEqual(self.client.get(path).status_code, 404)

    def test_reader_cannot_mutate_or_see_mutation_controls(self):
        self.client.force_login(self.reader)
        response = self.client.get('/mobile/supplies/')
        self.assertNotContains(response, 'Добавить поставку')
        actions = [self.url('document-add', kind='supplies'), self.url('document-edit', kind='supplies', pk=self.supply.pk),
                   self.url('document-delete', kind='supplies', pk=self.supply.pk), self.url('line-add', kind='releases', pk=self.release.pk),
                   self.url('directory-add', kind='categories'), self.url('directory-delete', kind='categories', pk=self.category.pk)]
        for path in actions:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 403)
                self.assertEqual(self.client.post(path, {}).status_code, 403)

    def test_missing_read_permission_is_enforced(self):
        user = get_user_model().objects.create_user('restricted')
        self.client.force_login(user)
        for path in ('/mobile/', '/mobile/supplies/', '/mobile/directories/items/', '/mobile/reports/stock/', '/mobile/reports/contract/'):
            self.assertEqual(self.client.get(path).status_code, 403)
        self.assertEqual(self.client.get('/mobile/menu/').status_code, 200)

    def test_standard_change_permission_allows_edit(self):
        self.reader.user_permissions.add(Permission.objects.get(codename='change_supply'))
        self.client.force_login(self.reader)
        response = self.client.post(self.url('document-edit', kind='supplies', pk=self.supply.pk), {
            'date': '2026-03-10', 'contract': self.contract.pk, 'description': 'Изменено',
        })
        self.assertEqual(response.status_code, 302)
        self.supply.refresh_from_db()
        self.assertEqual(self.supply.description, 'Изменено')

    def test_document_creation_redirects_to_mobile_detail(self):
        response = self.client.post('/mobile/supplies/add/', {'date': '2026-05-01', 'contract': self.contract.pk, 'description': 'Новая'})
        supply = Supply.objects.get(description='Новая')
        self.assertRedirects(response, self.url('document-detail', kind='supplies', pk=supply.pk))
        response = self.client.post('/mobile/releases/add/', {'date': '2026-05-02', 'contract': self.contract.pk, 'company': self.company.pk})
        release = Release.objects.get(date=date(2026, 5, 2))
        self.assertRedirects(response, self.url('document-detail', kind='releases', pk=release.pk))

    def test_invalid_document_retains_entered_data(self):
        response = self.client.post('/mobile/supplies/add/', {'date': 'bad', 'description': 'Сохранить текст'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Сохранить текст')
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(Supply.objects.count(), 1)

    def test_supply_line_updates_inventory_and_can_be_removed(self):
        path = self.url('line-add', kind='supplies', pk=self.supply.pk)
        for count in (3, 2):
            self.assertEqual(self.client.post(path, {'item': self.item.pk, 'count': count}).status_code, 302)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.count, 25)
        line = ItemInSupply.objects.get(supply=self.supply)
        self.assertEqual(line.count, 5)
        delete = self.url('line-delete', kind='supplies', pk=self.supply.pk, line_pk=line.pk)
        self.assertEqual(self.client.get(delete).status_code, 200)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.count, 25)
        self.assertEqual(self.client.post(delete).status_code, 302)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.count, 20)

    def test_release_line_updates_and_returns_inventory(self):
        path = self.url('line-add', kind='releases', pk=self.release.pk)
        for count in (3, 2):
            self.assertEqual(self.client.post(path, {'item': self.stock.pk, 'count': count}).status_code, 302)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.count, 15)
        line = ItemInRelease.objects.get(release=self.release)
        self.assertEqual(line.count, 5)
        self.assertEqual(self.client.post(self.url('line-delete', kind='releases', pk=self.release.pk, line_pk=line.pk)).status_code, 302)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.count, 20)

    def test_release_preserves_cross_contract_selection(self):
        response = self.client.post(self.url('line-add', kind='releases', pk=self.release.pk), {'item': self.other_stock.pk, 'count': 2})
        self.assertEqual(response.status_code, 302)
        self.other_stock.refresh_from_db()
        self.assertEqual(self.other_stock.count, 3)

    def test_invalid_counts_do_not_change_inventory(self):
        for count in (0, -1, '1.5', 'bad', 21):
            response = self.client.post(self.url('line-add', kind='releases', pk=self.release.pk), {'item': self.stock.pk, 'count': count})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['form'].errors)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.count, 20)
        self.assertFalse(ItemInRelease.objects.exists())
        response = self.client.post(self.url('line-add', kind='supplies', pk=self.supply.pk), {'item': self.item.pk, 'count': -1})
        self.assertTrue(response.context['form'].errors)

    def test_cannot_delete_line_through_another_document(self):
        line = ItemInSupply.objects.create(supply=self.supply, item=self.item, count=3)
        other = Supply.objects.create(date=date(2026, 5, 1), contract=self.contract)
        response = self.client.post(self.url('line-delete', kind='supplies', pk=other.pk, line_pk=line.pk))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(ItemInSupply.objects.filter(pk=line.pk).exists())

    def test_used_supply_line_cannot_be_deleted_beyond_available_stock(self):
        line = ItemInSupply.objects.create(supply=self.supply, item=self.item, count=30)
        response = self.client.post(self.url('line-delete', kind='supplies', pk=self.supply.pk, line_pk=line.pk))
        self.assertContains(response, 'Недостаточно товара')
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.count, 20)
        self.assertTrue(ItemInSupply.objects.filter(pk=line.pk).exists())

    def test_contract_is_locked_after_lines_are_added(self):
        ItemInSupply.objects.create(supply=self.supply, item=self.item, count=3)
        response = self.client.post(self.url('document-edit', kind='supplies', pk=self.supply.pk), {
            'date': '2026-03-10', 'contract': self.other_contract.pk, 'description': 'New note',
        })
        self.assertEqual(response.status_code, 302)
        self.supply.refresh_from_db()
        self.assertEqual(self.supply.contract_id, self.contract.pk)
        self.assertEqual(self.supply.description, 'New note')

    def test_nonempty_document_cannot_be_deleted(self):
        ItemInSupply.objects.create(supply=self.supply, item=self.item, count=3)
        response = self.client.post(self.url('document-delete', kind='supplies', pk=self.supply.pk))
        self.assertContains(response, 'Сначала удалите позиции')
        self.assertTrue(Supply.objects.filter(pk=self.supply.pk).exists())

    def test_empty_document_delete_is_post_only(self):
        path = self.url('document-delete', kind='supplies', pk=self.supply.pk)
        self.assertEqual(self.client.get(path).status_code, 200)
        self.assertTrue(Supply.objects.filter(pk=self.supply.pk).exists())
        self.assertRedirects(self.client.post(path), '/mobile/supplies/')
        self.assertFalse(Supply.objects.filter(pk=self.supply.pk).exists())

    def test_directory_crud_and_protected_delete(self):
        response = self.client.post('/mobile/directories/categories/add/', {'name': 'Новое'})
        self.assertRedirects(response, '/mobile/directories/categories/')
        category = Category.objects.get(name='Новое')
        self.client.post(self.url('directory-edit', kind='categories', pk=category.pk), {'name': 'Изменено'})
        category.refresh_from_db()
        self.assertEqual(category.name, 'Изменено')
        self.assertRedirects(self.client.post(self.url('directory-delete', kind='categories', pk=category.pk)), '/mobile/directories/categories/')
        response = self.client.post(self.url('directory-delete', kind='categories', pk=self.category.pk))
        self.assertContains(response, 'используется в складском учёте')

    def test_item_manufacturer_uses_select_and_saves(self):
        response = self.client.get('/mobile/directories/items/add/')
        self.assertContains(response, '<select name="manufacturer"')
        response = self.client.post('/mobile/directories/items/add/', {
            'article': 'M10', 'manufacturer': self.manufacturer.pk, 'category': self.category.pk, 'unit': self.unit.pk,
        })
        self.assertRedirects(response, '/mobile/directories/items/')
        self.assertTrue(Item.objects.filter(article='M10').exists())

    def test_stock_report_download(self):
        response = self.client.post('/mobile/reports/stock/', {'q': 'M8', 'with_contract': 'on'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/ms-excel')
        self.assertTrue(response.content.startswith(bytes.fromhex('D0CF11E0')))

    def test_contract_report_and_invalid_report(self):
        response = self.client.post('/mobile/reports/contract/', {'contract': self.contract.pk})
        self.assertEqual(response['Content-Type'], 'application/ms-excel')
        response = self.client.post('/mobile/reports/contract/', {'contract': 'bad'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_report_without_matches(self):
        response = self.client.post('/mobile/reports/stock/', {'q': 'not-in-stock'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/ms-excel')
        self.assertTrue(response.content.startswith(bytes.fromhex('D0CF11E0')))

    def test_report_form_allows_multiple_downloads(self):
        response = self.client.get('/mobile/reports/stock/')
        self.assertNotContains(response, 'data-submit-form')

    def test_csrf_is_required_for_writes_and_logout(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        for path in ('/mobile/supplies/add/', '/mobile/logout/', '/mobile/directories/categories/add/'):
            self.assertEqual(client.post(path, {}).status_code, 403)

    def test_desktop_still_uses_original_templates(self):
        response = self.client.get('/storage/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'storage.html')
        self.assertNotContains(response, 'mobile/mobile.css')
