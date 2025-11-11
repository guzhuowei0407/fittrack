from django.contrib import admin
from .models import UserProfile, Exercise, WorkoutSession, ExerciseSet


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'age', 'height_cm', 'weight_kg', 'fitness_level']
    list_filter = ['gender', 'fitness_level', 'primary_goal_choice']
    search_fields = ['user__username', 'user__email']


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'description']


class ExerciseSetInline(admin.TabularInline):
    model = ExerciseSet
    extra = 1


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'duration_minutes']
    list_filter = ['date', 'user']
    search_fields = ['user__username', 'notes']
    inlines = [ExerciseSetInline]


@admin.register(ExerciseSet)
class ExerciseSetAdmin(admin.ModelAdmin):
    list_display = ['workout', 'exercise', 'sets', 'reps', 'weight_kg']
    list_filter = ['exercise', 'workout__date']
    search_fields = ['exercise__name', 'workout__user__username']
