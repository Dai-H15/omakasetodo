from django.db import models
from accounts.models import CustomUser

# Create your models here.

class Goal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='goals')
    goal_id = models.CharField(max_length=200, default="default")
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_created = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    inappropriate_flag = models.BooleanField(default=False)


class Task(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    start_date = models.DateField(blank=True, null=True)
    description = models.TextField()
    priority = models.IntegerField()
    done_flag = models.BooleanField(default=False)
