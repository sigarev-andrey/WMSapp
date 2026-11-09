"""Choose the default interface without changing submitted requests."""
import re

from django.http import HttpResponseRedirect
from django.urls import Resolver404, resolve, reverse


MOBILE_AGENT = re.compile(
    r'android|iphone|ipad|ipod|mobile|tablet|kindle|silk/|'
    r'windows phone|iemobile|blackberry|bb10|opera mini',
    re.IGNORECASE,
)
SESSION_KEY = 'interface_mode'
DIRECTORIES = {
    'manufacturers': 'manufacturer', 'units': 'unit', 'categories': 'category',
    'companies': 'company', 'items': 'item', 'contracts': 'contract', 'staff': 'staff',
}


def mobile_target(match):
    """Translate known desktop pages; leave admin, assets and logout alone."""
    if match.namespace != 'storage':
        return None
    name = match.url_name
    if name in (None, 'storage', 'storage_with_contract'):
        return reverse('mobile:stock')
    if name == 'login':
        return reverse('mobile:login')
    for kind, singular in DIRECTORIES.items():
        if name == kind:
            return reverse('mobile:directory', kwargs={'kind': kind})
        for action in ('add', 'edit', 'delete'):
            if name == f'{action}-{singular}':
                return reverse(f'mobile:directory-{action}', kwargs={'kind': kind, **match.kwargs})
    for kind, singular in (('supplies', 'supply'), ('releases', 'release')):
        if name == kind:
            return reverse('mobile:documents', kwargs={'kind': kind})
        for action, mobile_action in (('add', 'add'), ('edit', 'edit'), ('delete', 'delete'), ('details', 'detail')):
            if name == f'{action}-{singular}':
                return reverse(f'mobile:document-{mobile_action}', kwargs={'kind': kind, **match.kwargs})
        if name == f'add-item-in-{singular}':
            return reverse('mobile:line-add', kwargs={'kind': kind, **match.kwargs})
    if name in ('report-common', 'report-by-contract'):
        return reverse('mobile:report', kwargs={'kind': 'stock' if name == 'report-common' else 'contract'})
    return None


def select_interface(request):
    # Never turn a submitted form into a GET, or replace an AJAX modal with a page.
    if request.method not in ('GET', 'HEAD') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return None
    try:
        # Desktop navigation also contains URLs without their trailing slash.
        match = resolve(request.path_info if request.path_info.endswith('/') else request.path_info + '/')
    except Resolver404:
        return None
    if match.namespace not in ('storage', 'mobile'):
        return None

    preference = request.GET.get('ui')
    if preference == 'auto':
        request.session.pop(SESSION_KEY, None)
    elif preference in ('mobile', 'desktop'):
        request.session[SESSION_KEY] = preference

    detected_mode = 'mobile' if MOBILE_AGENT.search(request.headers.get('User-Agent', '')) else 'desktop'
    request.interface_mode = request.session.get(SESSION_KEY, detected_mode)
    target = mobile_target(match)
    request.interface_varies = target is not None
    query = request.GET.copy()
    if preference in ('mobile', 'desktop', 'auto'):
        query.pop('ui', None)

    if target and request.interface_mode == 'mobile':
        if 'text_filter' in query:
            if 'q' not in query:
                query.setlist('q', query.getlist('text_filter'))
            query.pop('text_filter')
        if match.url_name == 'storage_with_contract':
            query['mode'] = 'contracts'
    elif preference in ('mobile', 'desktop', 'auto'):
        # Consume the one-time preference parameter so later links cannot undo a switch.
        target = request.path
    else:
        return None

    # The /mobile/ namespace remains an explicit entry point on any device.
    # Manual mode links point to the appropriate namespace before setting their preference.
    suffix = query.urlencode()
    return HttpResponseRedirect(f'{target}?{suffix}' if suffix else target)
