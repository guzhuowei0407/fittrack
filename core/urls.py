from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login-submit/', views.login_submit, name='login_submit'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password_code, name='reset_password_code'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('exercises/', views.exercises, name='exercises'),
    path('add/', views.add_data, name='add_data'),
    path('import/', views.import_csv, name='import_csv'),
    path('export/', views.export_csv, name='export_csv'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('ai-planner/', views.ai_planner, name='ai_planner'),
]




