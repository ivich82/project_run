from django.db import models
from django.contrib.auth.models import User

class Run(models.Model):
    created_at = models.DateField(auto_now_add=True)
    comment = models.TextField()
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)

    STATUS_CHOICES = [
        ('init', 'The race has been initialized'),
        ('in_progress', 'The race has started'),
        ('finished', 'The race is over')
    ]

    status = models.CharField(
        choices=STATUS_CHOICES,
        default='init'
    )

class AthleteInfo(models.Model):
    goals = models.TextField(blank=True)
    weight = models.IntegerField(blank=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)