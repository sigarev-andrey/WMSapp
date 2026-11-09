from django.urls import path

from . import views

app_name = 'mobile'

urlpatterns = [
    path('', views.stock, name='stock'),
    path('login/', views.MobileLoginView.as_view(), name='login'),
    path('logout/', views.MobileLogoutView.as_view(), name='logout'),
    path('menu/', views.menu, name='menu'),
    path('reports/<str:kind>/', views.report, name='report'),
    path('directories/<str:kind>/', views.directory, name='directory'),
    path('directories/<str:kind>/add/', views.directory_form, name='directory-add'),
    path('directories/<str:kind>/<int:pk>/edit/', views.directory_form, name='directory-edit'),
    path('directories/<str:kind>/<int:pk>/delete/', views.directory_delete, name='directory-delete'),
    path('<str:kind>/', views.documents, name='documents'),
    path('<str:kind>/add/', views.document_form, name='document-add'),
    path('<str:kind>/<int:pk>/', views.document_detail, name='document-detail'),
    path('<str:kind>/<int:pk>/edit/', views.document_form, name='document-edit'),
    path('<str:kind>/<int:pk>/delete/', views.document_delete, name='document-delete'),
    path('<str:kind>/<int:pk>/items/add/', views.line_add, name='line-add'),
    path('<str:kind>/<int:pk>/items/<int:line_pk>/delete/', views.line_delete, name='line-delete'),
]
