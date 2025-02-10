from django.urls import path, include
from main import views
urlpatterns = [
    path("", views.index, name="index"),
    path("create_goal/", views.create_goal, name="create_goal"),
    path("check_goal/<str:goal_id>", views.check_goal, name="check_goal"),
    path("goal_created/<str:goal_id>", views.goal_created, name="goal_created"),
    path("goal_list/", views.goal_list, name="goal_list"),
]