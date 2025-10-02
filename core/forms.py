from django import forms
from .models import DailyMetric

class DailyMetricForm(forms.ModelForm):
    class Meta:
        model = DailyMetric
        fields = ['date', 'weight', 'steps', 'calories']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}
        labels = {'date': 'date', 'weight': 'weight (kg)', 'steps': 'steps', 'calories': 'calories'}

class UploadFileForm(forms.Form):
    file = forms.FileField(label="select CSV file")