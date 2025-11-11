from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
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


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, validators=[EmailValidator()])

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-control form-control-lg",
            "placeholder": "Your username",
        })
        self.fields["email"].widget.attrs.update({
            "class": "form-control form-control-lg",
            "placeholder": "name@email.com",
        })
        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "At least 8 characters",
            "id": "id_password1",
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Re-enter password",
            "id": "id_password2",
        })


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(required=True, validators=[EmailValidator()])
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({
            "class": "form-control form-control-lg",
            "placeholder": "name@email.com",
        })


class ResetPasswordCodeForm(forms.Form):
    email = forms.EmailField(required=True, validators=[EmailValidator()])
    code = forms.CharField(max_length=6)
    new_password1 = forms.CharField(widget=forms.PasswordInput())
    new_password2 = forms.CharField(widget=forms.PasswordInput())
