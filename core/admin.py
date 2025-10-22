from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "gender", "age", "height_cm", "weight_kg", "fitness_level", "primary_goal_choice")

# Register your models here.
