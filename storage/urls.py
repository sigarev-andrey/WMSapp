from django.urls import path
from django.contrib.auth import views as lv
from . import views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from .views import (
    LoginView, LogoutView,
    StorageListView, StorageWithContractListView,
    ManufacturerListView, ManufacturerCreateView, ManufacturerUpdateView, ManufacturerDeleteView,
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    UnitListView, UnitCreateView, UnitUpdateView, UnitDeleteView,
    ItemListView, ItemCreateView, ItemUpdateView, ItemDeleteView,
    CompanyListView, CompanyCreateView, CompanyUpdateView, CompanyDeleteView,
    SupplyListView, SupplyDetailView, SupplyCreateView, SupplyUpdateView, SupplyDeleteView,
    ItemInSupplyCreateView, ItemInSupplyDeleteView,
    StaffListView, StaffCreateView, StaffUpdateView, StaffDeleteView,
    ContractListView, ContractCreateView, ContractUpdateView, ContractDeleteView,
    ReleaseListView, ReleaseDetailView, ReleaseCreateView, ReleaseUpdateView, ReleaseDeleteView,
    ItemInReleaseCreateView, ItemInReleaseDeleteView,
    report_common, report_by_contract,
)

app_name = 'storage'

urlpatterns = [
    #redirect from root path to storage.html
    path('', StorageListView.as_view()),
    #storage path
    path('storage/', StorageListView.as_view(), name='storage'),
    path('storage_with_contract/', StorageWithContractListView.as_view(), name='storage_with_contract'),
    #manufacturer instance path
    path('manufacturers/', ManufacturerListView.as_view(), name='manufacturers'),
    path('manufacturers/add/', ManufacturerCreateView.as_view(), name='add-manufacturer'),
    path('manufacturers/edit/<int:pk>/', ManufacturerUpdateView.as_view(), name='edit-manufacturer'),
    path('manufacturers/delete/<int:pk>/', ManufacturerDeleteView.as_view(), name='delete-manufacturer'),
    #unit instance path
    path('units/', UnitListView.as_view(), name='units'),
    path('units/add/', UnitCreateView.as_view(), name='add-unit'),
    path('units/edit/<int:pk>/', UnitUpdateView.as_view(), name='edit-unit'),
    path('units/delete/<int:pk>/', UnitDeleteView.as_view(), name='delete-unit'),
    #category instance path
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('categories/add/', CategoryCreateView.as_view(), name='add-category'),
    path('categories/edit/<int:pk>/', CategoryUpdateView.as_view(), name='edit-category'),
    path('categories/delete/<int:pk>/', CategoryDeleteView.as_view(), name='delete-category'),
    #company instance path
    path('companies/', CompanyListView.as_view(), name='companies'),
    path('companies/add/', CompanyCreateView.as_view(), name='add-company'),
    path('companies/edit/<int:pk>/', CompanyUpdateView.as_view(), name='edit-company'),
    path('companies/delete/<int:pk>/', CompanyDeleteView.as_view(), name='delete-company'),
    #login, logout path
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    #item instance path
    path('items/', ItemListView.as_view(), name='items'),
    path('items/add/', ItemCreateView.as_view(), name='add-item'),
    path('items/edit/<int:pk>/', ItemUpdateView.as_view(), name='edit-item'),
    path('items/delete/<int:pk>/', ItemDeleteView.as_view(), name='delete-item'),
    #contract instance path
    path('contracts/', ContractListView.as_view(), name='contracts'),
    path('contracts/add/', ContractCreateView.as_view(), name='add-contract'),
    path('contracts/edit/<int:pk>/', ContractUpdateView.as_view(), name='edit-contract'),
    path('contracts/delete/<int:pk>/', ContractDeleteView.as_view(), name='delete-contract'),
    #supply instance path
    path('supplies/', SupplyListView.as_view(), name='supplies'),
    path('supplies/add/', SupplyCreateView.as_view(), name='add-supply'),
    path('supplies/edit/<int:pk>/', SupplyUpdateView.as_view(), name='edit-supply'),
    path('supplies/details/<int:pk>/', SupplyDetailView.as_view(), name='details-supply'),
    path('supplies/delete/<int:pk>/', SupplyDeleteView.as_view(), name='delete-supply'),
    path('supplies/details/<int:pk>/add-item/', ItemInSupplyCreateView.as_view(), name='add-item-in-supply'),
    path('supplies/details/delete-item/<int:pk>/', ItemInSupplyDeleteView.as_view(), name='delete-item-from-supply'),
    #staff instance path
    path('staff/', StaffListView.as_view(), name='staff'),
    path('staff/add/', StaffCreateView.as_view(), name='add-staff'),
    path('staff/edit/<int:pk>/', StaffUpdateView.as_view(), name='edit-staff'),
    path('staff/delete/<int:pk>/', StaffDeleteView.as_view(), name='delete-staff'),
    #release instance path
    path('releases/', ReleaseListView.as_view(), name='releases'),
    path('releases/add/', ReleaseCreateView.as_view(), name='add-release'),
    path('releases/edit/<int:pk>/', ReleaseUpdateView.as_view(), name='edit-release'),
    path('releases/delete/<int:pk>/', ReleaseDeleteView.as_view(), name='delete-release'),
    path('releases/details/<int:pk>/', ReleaseDetailView.as_view(), name='details-release'),
    path('releases/details/<int:pk>/add-item/', ItemInReleaseCreateView.as_view(), name='add-item-in-release'),
    path('releases/details/delete-item/<int:pk>/', ItemInReleaseDeleteView.as_view(), name='delete-item-from-release'),
    #reports
    path('reports/report-common/', views.report_common, name='report-common'),
    path('reports/report-by-contract/', views.report_by_contract, name='report-by-contract'),
]