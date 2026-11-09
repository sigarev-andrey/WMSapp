from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from storage.interface import select_interface


IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1'
ANDROID = 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/130.0.0.0 Mobile Safari/537.36'
DESKTOP = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36'


class InterfaceSelectionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser('device-test', password='test-pass')

    def test_phones_and_tablets_use_mobile_login_before_authentication(self):
        agents = [
            IPHONE, ANDROID,
            'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) Version/18.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; SM-X710) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Linux; U; en-US) AppleWebKit/533.16 Silk/3.2 Safari/533.16',
            'Opera/9.80 (J2ME/MIDP; Opera Mini/9.0) Presto/2.12.423',
        ]
        for agent in agents:
            with self.subTest(agent=agent):
                response = self.client.get('/', HTTP_USER_AGENT=agent, follow=True)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'mobile/login.html')
                self.assertEqual(response.redirect_chain[0][0], '/mobile/')
                self.assertEqual(len(response.redirect_chain), 2)

    def test_desktops_and_unknown_agents_keep_desktop_login(self):
        for agent in [DESKTOP, 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Version/18.0 Safari/605.1.15',
                      'Mozilla/5.0 (X11; Linux x86_64) Firefox/132.0', '', 'unknown-browser']:
            with self.subTest(agent=agent):
                response = self.client.get('/', HTTP_USER_AGENT=agent, follow=True)
                self.assertTemplateUsed(response, 'login.html')
                self.assertEqual(response.redirect_chain, [('/login/', 302)])

    def test_mobile_login_post_returns_to_requested_document(self):
        response = self.client.get('/supplies/?contract=7', HTTP_USER_AGENT=IPHONE, follow=True)
        self.assertEqual(response.context['next'], '/mobile/supplies/?contract=7')
        response = self.client.post('/mobile/login/', {
            'username': 'device-test', 'password': 'test-pass', 'next': '/mobile/supplies/?contract=7',
        }, HTTP_USER_AGENT=IPHONE)
        self.assertEqual(response.url, '/mobile/supplies/?contract=7')

    def test_deep_links_resolve_to_the_corresponding_mobile_pages(self):
        for source, target in [
            ('/storage', '/mobile/'), ('/supplies', '/mobile/supplies/'),
            ('/releases/details/12/', '/mobile/releases/12/'),
            ('/supplies/edit/7/', '/mobile/supplies/7/edit/'),
            ('/supplies/details/7/add-item/', '/mobile/supplies/7/items/add/'),
            ('/items/', '/mobile/directories/items/'),
            ('/manufacturers/add/', '/mobile/directories/manufacturers/add/'),
            ('/staff/edit/4/', '/mobile/directories/staff/4/edit/'),
            ('/units/delete/5/', '/mobile/directories/units/5/delete/'),
            ('/reports/report-common/', '/mobile/reports/stock/'),
            ('/reports/report-by-contract/', '/mobile/reports/contract/'),
        ]:
            with self.subTest(source=source):
                self.assertEqual(self.client.get(source, HTTP_USER_AGENT=ANDROID).url, target)

    def test_filters_and_page_survive_the_redirect(self):
        response = self.client.get('/storage_with_contract/', {
            'text_filter': 'Болт & гайка', 'category': '4', 'contract': '7', 'page': '2',
        }, HTTP_USER_AGENT=IPHONE)
        self.assertEqual(urlsplit(response.url).path, '/mobile/')
        self.assertEqual(parse_qs(urlsplit(response.url).query), {
            'q': ['Болт & гайка'], 'category': ['4'], 'contract': ['7'], 'page': ['2'], 'mode': ['contracts'],
        })

    def test_manual_desktop_mode_persists_through_login(self):
        response = self.client.get('/login/?ui=desktop', HTTP_USER_AGENT=IPHONE, follow=True)
        self.assertTemplateUsed(response, 'login.html')
        self.assertEqual(self.client.session['interface_mode'], 'desktop')
        response = self.client.post('/login/', {'username': 'device-test', 'password': 'test-pass'},
                                    HTTP_USER_AGENT=IPHONE, follow=True)
        self.assertTemplateUsed(response, 'storage.html')
        self.assertEqual(self.client.get('/supplies/', HTTP_USER_AGENT=IPHONE).status_code, 200)

    def test_manual_mobile_mode_persists_on_desktop(self):
        self.client.force_login(self.user)
        response = self.client.get('/mobile/?ui=mobile', HTTP_USER_AGENT=DESKTOP, follow=True)
        self.assertTemplateUsed(response, 'mobile/stock.html')
        self.assertEqual(response.redirect_chain, [('/mobile/', 302)])
        self.assertEqual(self.client.get('/storage/', HTTP_USER_AGENT=DESKTOP).url, '/mobile/')
        self.assertEqual(self.client.session['interface_mode'], 'mobile')

    def test_auto_mode_clears_override_and_detects_each_request(self):
        self.client.force_login(self.user)
        self.client.get('/storage/?ui=desktop', HTTP_USER_AGENT=IPHONE)
        response = self.client.get('/storage/?ui=auto', HTTP_USER_AGENT=IPHONE, follow=True)
        self.assertTemplateUsed(response, 'mobile/stock.html')
        self.assertNotIn('interface_mode', self.client.session)
        response = self.client.get('/storage/', HTTP_USER_AGENT=DESKTOP)
        self.assertTemplateUsed(response, 'storage.html')

    def test_auto_mode_returns_desktop_after_manual_mobile_selection(self):
        self.client.force_login(self.user)
        self.client.get('/mobile/?ui=mobile', HTTP_USER_AGENT=DESKTOP)
        response = self.client.get('/storage/?ui=auto', HTTP_USER_AGENT=DESKTOP, follow=True)
        self.assertTemplateUsed(response, 'storage.html')
        self.assertEqual(response.redirect_chain, [('/storage/', 302)])

    def test_explicit_mobile_url_remains_available_on_desktop(self):
        self.client.force_login(self.user)
        response = self.client.get('/mobile/', HTTP_USER_AGENT=DESKTOP)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mobile/stock.html')

    def test_invalid_preference_is_ignored(self):
        response = self.client.get('/storage/?ui=invalid', HTTP_USER_AGENT=ANDROID)
        self.assertEqual(urlsplit(response.url).path, '/mobile/')
        self.assertNotIn('interface_mode', self.client.session)

    def test_posts_are_not_redirected_or_used_to_change_preferences(self):
        self.client.force_login(self.user)
        response = self.client.post('/categories/add/?ui=mobile', {'name': 'Device test'}, HTTP_USER_AGENT=IPHONE)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/categories/')
        from storage.models import Category
        self.assertTrue(Category.objects.filter(name='Device test').exists())
        self.assertNotIn('interface_mode', self.client.session)

    def test_ajax_modals_keep_the_original_response(self):
        self.client.force_login(self.user)
        response = self.client.get('/categories/add/', HTTP_USER_AGENT=IPHONE, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_category.html')

    def test_unrelated_paths_and_unsafe_methods_are_not_selected(self):
        factory = RequestFactory()
        for method, path in [('get', '/admin/'), ('get', '/static/mobile/mobile.css'), ('get', '/does-not-exist/'),
                             ('get', '/logout/'), ('post', '/supplies/add/'), ('put', '/storage/'), ('delete', '/storage/')]:
            with self.subTest(method=method, path=path):
                request = getattr(factory, method)(path, HTTP_USER_AGENT=IPHONE)
                request.session = {}
                self.assertIsNone(select_interface(request))

    def test_head_uses_same_selection_and_cache_varies_by_agent(self):
        response = self.client.head('/storage/', HTTP_USER_AGENT=IPHONE)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/mobile/')
        self.assertEqual(response.content, b'')
        for response in [response, self.client.get('/login/', HTTP_USER_AGENT=DESKTOP)]:
            self.assertIn('User-Agent', response['Vary'])
            self.assertIn('Cookie', response['Vary'])
