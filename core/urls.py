# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-metric/', views.add_metric, name='add_metric'),
    path('import-csv/', views.import_csv, name='import_csv'),
    path('data/', views.data_list, name='data_list'),
    path('data/<int:pk>/', views.data_detail, name='data_detail'),
    path('data/<int:pk>/delete/', views.data_delete, name='data_delete'),
    path('stats/', views.data_stats, name='data_stats'),
    path('signup/', views.signup, name='signup'),
]