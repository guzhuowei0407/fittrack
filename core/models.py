#core/models.py
from django.db import models
from django.contrib.auth.models import User

class DailyMetric(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="user")
    date = models.DateField(verbose_name="date")
    weight = models.FloatField(verbose_name="weight (kg)")
    steps = models.IntegerField(null=True, blank=True, verbose_name="steps")
    calories = models.IntegerField(null=True, blank=True, verbose_name="calories")

    class Meta:
        unique_together = [('user', 'date')]
        ordering = ['date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"