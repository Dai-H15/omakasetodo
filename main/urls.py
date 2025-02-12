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
    path("check_task_create/<str:goal_id>", views.check_task_create, name="check_task_create")
]