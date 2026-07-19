from django.urls import path

from . import views

urlpatterns = [
    path('', views.contact_list, name='contact_list'),
    path('<int:contact_id>/edit/', views.contact_edit, name='contact_edit'),
    path('<int:contact_id>/delete/', views.contact_delete, name='contact_delete'),
    path('add/', views.contact_create, name='contact_add'),
    path('import/', views.contact_import, name='contact_import'),
]
