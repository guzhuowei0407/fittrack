from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "avatar",
            "gender",
            "age",
            "height_cm",
            "weight_kg",
            "fitness_level",
            "primary_goal_choice",
        ]

