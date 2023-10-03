from django.urls import path
from django.contrib.auth import views as lv
from . import views
from django.contrib.auth.views import LogoutView
from django.conf import settings

app_name = 'storage'

urlpatterns = [
    path('', views.storage),
    path('storage/', views.storage, name='storage'),
    path('manufacturers/', views.manufacturers, name='manufacturers'),
    path('manufacturers/add/', views.add_manufacturer, name='add-manufacturer'),
    path('manufacturers/edit/<int:id>/', views.edit_manufacturer, name='edit-manufacturer'),
    path('manufacturers/delete/<int:id>/', views.delete_manufacturer, name='delete-manufacturer'),
    path('units/', views.units, name='units'),
    path('units/add/', views.add_unit, name='add-unit'),
    path('units/edit/<int:id>/', views.edit_unit, name='edit-unit'),
    path('units/delete/<int:id>/', views.delete_unit, name='delete-unit'),
    path('categories/', views.categories, name='categories'),
    path('categories/add/', views.add_category, name='add-category'),
    path('categories/edit/<int:id>/', views.edit_category, name='edit-category'),
    path('categories/delete/<int:id>/', views.delete_category, name='delete-category'),
    path('companies/', views.companies, name='companies'),
    path('companies/add/', views.add_company, name='add-company'),
    path('companies/edit/<int:id>/', views.edit_company, name='edit-company'),
    path('companies/delete/<int:id>/', views.delete_company, name='delete_company'),
    path('login/', views.user_login, name='login'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path('items/', views.items, name='items'),
    path('items/edit/<int:id>/', views.edit_item, name='edit-item'),
    path('items/delete/<int:id>/', views.delete_item, name='delete-item'),
    path('contracts/', views.contracts, name='contracts'),
    path('contracts/edit/<int:id>/', views.edit_contract, name='edit-contract'),
    path('contracts/delete/<int:id>/', views.delete_contract, name='delete-contract'),
    path('supplies/', views.supplies, name='supplies'),
    path('supplies/add/', views.add_supply, name='add-supply'),
    path('supplies/edit/<int:id>/', views.edit_supply, name='edit-supply'),
    path('supplies/details/<int:id>/', views.details_supply, name='details-supply'),
    path('supplies/details/<int:id>/add-item/', views.add_item_in_supply, name='add-item-in-supply'),
    path('supplies/details/delete-item/<int:id>/', views.delete_item_from_supply, name='delete-item-from-supply'),
    path('staff/', views.staff, name='staff'),
    path('staff/add/', views.add_staff, name='add-staff'),
    path('staff/edit/<int:id>/', views.edit_staff, name='edit-staff'),
    path('staff/delete/<int:id>/', views.delete_staff, name='delete-staff'),
    path('releases/', views.releases, name='releases'),
    path('releases/add/', views.add_release, name='add-release'),
    path('releases/edit/<int:id>/', views.edit_release, name='edit-release'),
    path('releases/delete/<int:id>/', views.delete_release, name='delete-release'),
    path('releases/details/<int:id>/', views.details_release, name='details-release'),
    path('releases/details/<int:id>/add-item/', views.add_item_in_release, name='add-item-in-release')
]