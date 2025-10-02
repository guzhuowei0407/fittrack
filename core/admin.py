#core/admin.py
from django.contrib import admin
from .models import DailyMetric

@admin.register(DailyMetric)
class DailyMetricAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'weight', 'steps', 'calories')
    list_filter = ('user',)
    search_fields = ('user__username',)