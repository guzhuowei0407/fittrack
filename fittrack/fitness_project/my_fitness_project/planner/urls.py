# planner/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # When users visit the website root directory, call the generate_plan function from views.py
    path('', views.generate_plan, name='home'),
]