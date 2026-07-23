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

    distance = models.FloatField(null=True)
    run_time_seconds = models.IntegerField(null=True)
    speed = models.FloatField(blank=True, null=True)

class AthleteInfo(models.Model):
    goals = models.TextField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)


class Challenge(models.Model):
    full_name = models.TextField()
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)



class Position(models.Model):
    run = models.IntegerField()
    latitude = models.DecimalField(max_digits=7, decimal_places=4)
    longitude = models.DecimalField(max_digits=8, decimal_places=4)
    date_time = models.DateTimeField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)

class CollectibleItem(models.Model):
    name = models.TextField()
    uid = models.TextField()
    latitude = models.DecimalField(max_digits=7, decimal_places=4)
    longitude = models.DecimalField(max_digits=8, decimal_places=4)
    picture = models.URLField()
    value = models.IntegerField()
    items = models.ManyToManyField(User,  related_name='collectibleitems')

class Subscribe(models.Model):
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, related_name='athlete')
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coach')