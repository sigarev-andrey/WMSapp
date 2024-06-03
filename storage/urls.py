from django.urls import path
from django.contrib.auth import views as lv
from . import views
from django.contrib.auth.views import LogoutView
from django.conf import settings

app_name = 'storage'

urlpatterns = [
    #redirect from root path to storage.html
    path('', views.storage),
    #storage path
    path('storage/', views.storage, name='storage'),
    path('storage_with_contract/', views.storage_with_contract, name='storage_with_contract'),
    path('storage/export/', views.export_storage_to_excel, name='storage-export'),
    path('manufacturers/', views.manufacturers, name='manufacturers'),
    path('manufacturers/add/', views.add_manufacturer, name='add-manufacturer'),
    path('manufacturers/edit/<int:id>/', views.edit_manufacturer, name='edit-manufacturer'),
    path('manufacturers/delete/<int:id>/', views.delete_manufacturer, name='delete-manufacturer'),
    #unit instance path
    path('units/', views.units, name='units'),
    path('units/add/', views.add_unit, name='add-unit'),
    path('units/edit/<int:id>/', views.edit_unit, name='edit-unit'),
    path('units/delete/<int:id>/', views.delete_unit, name='delete-unit'),
    #category instance path
    path('categories/', views.categories, name='categories'),
    path('categories/add/', views.add_category, name='add-category'),
    path('categories/edit/<int:id>/', views.edit_category, name='edit-category'),
    path('categories/delete/<int:id>/', views.delete_category, name='delete-category'),
    #company instance path
    path('companies/', views.companies, name='companies'),
    path('companies/add/', views.add_company, name='add-company'),
    path('companies/edit/<int:id>/', views.edit_company, name='edit-company'),
    path('companies/delete/<int:id>/', views.delete_company, name='delete_company'),
    #login, logout path
    path('login/', views.user_login, name='login'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    #item instance path
    path('items/', views.items, name='items'),
    path('items/add/', views.add_item, name='add-item'),
    path('items/edit/<int:id>/', views.edit_item, name='edit-item'),
    path('items/delete/<int:id>/', views.delete_item, name='delete-item'),
    #contract instance path
    path('contracts/', views.contracts, name='contracts'),
    path('contracts/add/', views.add_contract, name='add-contract'),
    path('contracts/edit/<int:id>/', views.edit_contract, name='edit-contract'),
    path('contracts/delete/<int:id>/', views.delete_contract, name='delete-contract'),
    #supply instance path
    path('supplies/', views.supplies, name='supplies'),
    path('supplies/add/', views.add_supply, name='add-supply'),
    path('supplies/edit/<int:id>/', views.edit_supply, name='edit-supply'),
    path('supplies/details/<int:id>/', views.details_supply, name='details-supply'),
    path('supplies/details/<int:id>/add-item/', views.add_item_in_supply, name='add-item-in-supply'),
    path('supplies/details/delete-item/<int:id>/', views.delete_item_from_supply, name='delete-item-from-supply'),
    #staff instance path
    path('staff/', views.staff, name='staff'),
    path('staff/add/', views.add_staff, name='add-staff'),
    path('staff/edit/<int:id>/', views.edit_staff, name='edit-staff'),
    path('staff/delete/<int:id>/', views.delete_staff, name='delete-staff'),
    #release instance path
    path('releases/', views.releases, name='releases'),
    path('releases/add/', views.add_release, name='add-release'),
    path('releases/edit/<int:id>/', views.edit_release, name='edit-release'),
    path('releases/delete/<int:id>/', views.delete_release, name='delete-release'),
    path('releases/details/<int:id>/', views.details_release, name='details-release'),
    path('releases/details/<int:id>/add-item/', views.add_item_in_release, name='add-item-in-release'),
    path('releases/details/delete-item/<int:id>/', views.delete_item_from_release, name='delete-item-from-release')
]