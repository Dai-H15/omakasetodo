from django.urls import path, include
from main import views
urlpatterns = [
    path("", views.index, name="index"),
    path("create_goal/", views.create_goal, name="create_goal"),
    path("check_goal/<str:goal_id>", views.check_goal, name="check_goal"),
    path("goal_created/<str:goal_id>", views.goal_created, name="goal_created"),
    path("goal_list/", views.goal_list, name="goal_list"),
    path("goal_delete/<str:goal_id>", views.goal_delete, name="goal_delete"),
    path("goal_display/<str:goal_id>", views.goal_display, name="goal_display"),
    path("task_list/<str:goal_id>", views.task_list, name="task_list"),
    path("create_task/<str:goal_id>", views.create_task, name="create_task"),
    path("check_task_create/<str:goal_id>", views.check_task_create, name="check_task_create"),
    path("goal_achievement/<str:goal_id>", views.goal_achievement, name="goal_achievement"),
    path("task_display/<str:goal_id>/<str:task_id>", views.task_display, name="task_display"),
    path("task_done/<str:goal_id>/<str:task_id>", views.task_done, name="task_done"),
    path("task_help_display/<str:goal_id>/<str:task_id>", views.task_help_display, name="task_help_display"),
    path("create_task_help/<str:goal_id>/<str:task_id>", views.create_task_help, name="create_task_help"),
    path("check_task_help_create/<str:goal_id>/<str:task_id>", views.check_task_help_create, name="check_task_help_create"),
    path("today_task/", views.today_task, name="today_task"),

]