from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )

    FITNESS_LEVEL_CHOICES = (
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    )

    GOAL_CHOICES = (
        ("fat_loss", "Fat Loss"),
        ("muscle_gain", "Muscle Gain"),
        ("endurance", "Endurance"),
        ("general_fitness", "General Fitness"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    gender = models.CharField(max_length=16, choices=GENDER_CHOICES, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    fitness_level = models.CharField(max_length=16, choices=FITNESS_LEVEL_CHOICES, blank=True)
    primary_goal_choice = models.CharField(max_length=32, choices=GOAL_CHOICES, blank=True)

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"


class Exercise(models.Model):
    """Exercise types that users can perform"""
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=[
        ('strength', 'Strength Training'),
        ('cardio', 'Cardio'),
        ('flexibility', 'Flexibility'),
        ('other', 'Other')
    ], default='strength')
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class WorkoutSession(models.Model):
    """A workout session record"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date.strftime('%Y-%m-%d %H:%M')}"


class ExerciseSet(models.Model):
    """Individual set within a workout"""
    workout = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='exercise_sets')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField(default=1)
    reps = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)  # For cardio exercises
    distance_km = models.FloatField(null=True, blank=True)  # For running, cycling etc.
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.exercise.name} - {self.sets} sets"


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_codes")
    email = models.EmailField()
    code_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self) -> bool:
        return self.used_at is None and timezone.now() < self.expires_at


class WeightHistory(models.Model):
    """Track user's weight changes over time"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="weight_history")
    weight_kg = models.FloatField()
    recorded_date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['recorded_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.weight_kg}kg on {self.recorded_date}"
