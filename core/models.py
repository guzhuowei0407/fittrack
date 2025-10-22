from django.db import models
from django.contrib.auth.models import User


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

# Create your models here.
