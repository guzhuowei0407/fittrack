from django import forms
from .models import UserProfile, WorkoutSession, ExerciseSet, Exercise


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


class WorkoutSessionForm(forms.ModelForm):
    class Meta:
        model = WorkoutSession
        fields = ['date', 'duration_minutes', 'notes']
        widgets = {
            'date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Duration in minutes'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Workout notes (optional)'
            })
        }


class ExerciseSetForm(forms.ModelForm):
    class Meta:
        model = ExerciseSet
        fields = ['exercise', 'sets', 'reps', 'weight_kg', 'duration_seconds', 'distance_km', 'notes']
        widgets = {
            'exercise': forms.Select(attrs={'class': 'form-control'}),
            'sets': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reps': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'duration_seconds': forms.NumberInput(attrs={'class': 'form-control'}),
            'distance_km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
        }


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv',
        }),
        help_text='Upload a CSV file with your workout data'
    )

