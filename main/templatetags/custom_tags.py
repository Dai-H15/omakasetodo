from django import template
from django.utils.safestring import mark_safe

from main.models import Goal

register = template.Library()

@register.simple_tag
def check_task_all_done(goal: Goal):
    if goal.is_completed:
        return mark_safe('<i class="bi bi-check2-circle fs-2 text-success"></i>')
    tasks = goal.tasks.all()
    for task in tasks:
        if not task.done_flag:
            return mark_safe('<i class="bi bi-pencil text-danger fs-2"></i>')
    return mark_safe('<i class="bi bi-info-circle fs-2 text-info"></i>')
