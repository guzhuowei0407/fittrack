# planner/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # 当用户访问网站根目录时，调用 views.py 里的 generate_plan 函数
    path('', views.generate_plan, name='home'),
]