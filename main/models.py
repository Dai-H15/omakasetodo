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
    start_date = models.DateField(auto_now_add=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    inappropriate_flag = models.BooleanField(default=False)
    task_creating = models.BooleanField(default=False)


class Task(models.Model):
    task_id = models.CharField(max_length=200, default="default")
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    start_date = models.DateField(blank=True, null=True)
    description = models.TextField()
    priority = models.IntegerField()
    done_flag = models.BooleanField(default=False)
    is_create_task_help = models.BooleanField(default=False)
    task_help_create_completed = models.BooleanField(default=False)


class TaskHelp(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="Task_help")
    title = models.CharField(max_length=200, default="default")
    help_text = models.TextField()
    related_url = models.TextField()