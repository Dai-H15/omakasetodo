from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, HttpResponse, reverse
from django.utils import timezone
from main.form import CreateGoalForm, TaskForm
from main.models import Goal, Task
import secrets
import asyncio
from asgiref.sync import sync_to_async
import time
from django.core.paginator import Paginator
from openai_app.views import goal_moderation, task_fetch


# Create your views here.

def index(request):
    return render(request, 'main/index.html')


@login_required
async def create_goal(request):
    user = await request.auser()
    contexts = {}
    contexts["async_func"] = True
    contexts["user"] = user
    contexts["form"] = CreateGoalForm()
    if request.method == "POST":
        form = CreateGoalForm(request.POST)
        if form.is_valid():
            goal = await Goal.objects.acreate(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                goal_id=secrets.token_urlsafe(32),
                user=user,
            )
            asyncio.create_task(sync_to_async(moderate_goal, thread_sensitive=False)(goal))
            return redirect("check_goal", goal_id=goal.goal_id)

    return render(request, "main/create_goal.html", contexts)


@login_required
def check_goal(request, goal_id):
    if request.method == "POST":
        try:
            goal = Goal.objects.get(goal_id=goal_id, user=request.user)
        except Goal.DoesNotExist:
            return return_error_page(request)
        if goal.is_created:
            if goal.inappropriate_flag:
                res = {
                    "is_created": True,
                    "inappropriate_flag": True,
                }
            else:
                res = {
                    "is_created": True,
                    "inappropriate_flag": False,
                    "next": reverse("goal_created", kwargs = { "goal_id": goal_id})
                }

        else:
            res = {"is_created": False}
        return JsonResponse(res)
    return render(request, "main/check_goal.html", {"goal_id": goal_id})


@login_required
def goal_created(request, goal_id):
    contexts = {}
    try:
        goal = Goal.objects.get(goal_id=goal_id, user=request.user)
    except Goal.DoesNotExist:
        return return_error_page(request)
    contexts["goal"] = goal
    return render(request, "main/goal_created.html", contexts)


@login_required
def goal_list(request):
    contexts = {}
    goals = Goal.objects.filter(user=request.user,inappropriate_flag=False)
    paginator = Paginator(goals, 8)
    if "page" in request.GET:
        try:
            page = int(request.GET["page"])
        except ValueError:
            page = 1
        if page < paginator.num_pages + 1:
            page = request.GET["page"]
    else:
        page = 1
    goals = paginator.get_page(page)
    contexts["goals"] = goals
    contexts["pages"] = range(1, paginator.num_pages + 1)
    contexts["current"] = int(page)
    return render(request, "main/goal_list.html", contexts)


@login_required
def goal_delete(request, goal_id):
    try:
        goal = Goal.objects.get(goal_id=goal_id, user=request.user)
    except Goal.DoesNotExist:
        return return_error_page(request)
    contexts = {}
    contexts["goal"] = goal
    if request.method == "POST":
        goal.delete()
        return redirect("goal_list")
    return render(request, "main/goal_delete.html", contexts)


@login_required
def goal_display(request, goal_id):
    contexts = {}
    goal = Goal.objects.get(goal_id=goal_id, user=request.user)
    contexts["goal"] = goal
    if goal.task_creating is True and goal.is_completed is False:
        contexts["not_completed_task_num"] = goal.tasks.filter(done_flag=False).count()
        if contexts["not_completed_task_num"] == 0:
            contexts["task_all_completed"] = True
    return render(request, "main/goal_display.html", contexts)


def return_error_page(request):
    return render(request, "main/error_page.html")

@login_required
def task_list(request, goal_id):
    contexts = {}
    if "task_done_set" in request.session:
        del request.session["task_done_set"]
        contexts["task_done_set"] = True
    try:
        goal = Goal.objects.get(goal_id = goal_id,user = request.user)
    except Goal.DoesNotExist:
        return return_error_page(request)
    contexts["goal"] = goal
    tasks = Task.objects.filter(goal = goal).order_by("priority").order_by("done_flag")
    contexts["tasks"] = tasks
    contexts["task_len"] = len(tasks)
    return render(request, "main/task_list.html", contexts)


@login_required
async def create_task(request, goal_id):
    contexts = {}
    try:
        goal = await Goal.objects.aget(goal_id=goal_id, user=request.user, task_creating=False)
    except Goal.DoesNotExist:
        return return_error_page(request)
    contexts["goal"] = goal
    asyncio.create_task(sync_to_async(task_fetch, thread_sensitive=False)(goal))
    goal.task_creating = True
    await goal.asave()
    return render(request, "main/create_task_send.html", contexts)

@login_required
def check_task_create(request, goal_id):
    if request.method == "POST":
        try:
            goal = Goal.objects.get(goal_id=goal_id, user=request.user, task_creating=True)
        except Goal.DoesNotExist:
            return return_error_page(request)
        if Task.objects.filter(goal=goal).exists():
            result = {"is_created": True}
        else:
            result = {"is_created": False}
        return JsonResponse(result)
    return return_error_page(request)


@login_required
def goal_achievement(request, goal_id):
    contexts = {}
    try:
        goal = Goal.objects.get(goal_id=goal_id, user=request.user, is_completed=False)
    except Goal.DoesNotExist:
        return return_error_page(request)
    contexts["goal"] = goal
    if request.method == "POST":
        goal.end_date = timezone.now()
        goal.is_completed = True
        goal.save()
        return redirect("goal_list")
    return render(request, "main/goal_achievement.html", contexts)


@login_required
def task_display(request,goal_id, task_id):
    contexts = {}
    try:
        goal = Goal.objects.get(goal_id=goal_id, user=request.user)
    except Goal.DoesNotExist:
        return return_error_page(request)
    try:
        task = Task.objects.get(goal=goal, task_id=task_id)
    except Task.DoesNotExist:
        return return_error_page(request)
    contexts["goal"] = goal
    contexts["task"] = task
    form = TaskForm(initial={
        "title": task.title,
        "description": task.description,
        "start_date": task.start_date,
        "done_flag":task.done_flag,
        "priority": task.priority
    })
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task.start_date = form.cleaned_data.get("start_date")
            task.priority = form.cleaned_data.get("priority")
            task.done_flag = form.cleaned_data.get("done_flag")
            task.save()
            contexts["saved"] = True
    contexts["form"] = form
    return render(request, "main/task_display.html", contexts)


@login_required
def task_done(request, goal_id, task_id):
    try:
        goal = Goal.objects.get(goal_id=goal_id, user=request.user)
    except Goal.DoesNotExist:
        return return_error_page(request)
    try:
        task = Task.objects.get(goal=goal, task_id=task_id)
    except Task.DoesNotExist:
        return return_error_page(request)
    task.done_flag = True
    task.save()
    request.session["task_done_set"] = True
    return redirect("task_list",goal_id=goal_id)


def moderate_goal(goal):
    print("creating.")
    goal.inappropriate_flag = goal_moderation(goal)
    goal.is_created = True
    goal.save()
    print("created.")


