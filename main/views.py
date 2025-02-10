from django.http.response import JsonResponse
from django.shortcuts import render, redirect, HttpResponse, reverse
from main.form import CreateGoalForm
from main.models import Goal
import secrets
import asyncio
from asgiref.sync import sync_to_async
import time
from django.core.paginator import Paginator
# Create your views here.

def index(request):
    return render(request, 'main/index.html')


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
            asyncio.create_task(sync_to_async(create_task, thread_sensitive=False)(goal))
            return redirect("check_goal", goal_id=goal.goal_id)

    return render(request, "main/create_goal.html", contexts)


def check_goal(request, goal_id):
    if request.method == "POST":
        try:
            goal = Goal.objects.get(goal_id=goal_id, user=request.user)
        except Goal.DoesNotExist:
            return HttpResponse("不正な操作です")
        if goal.is_created:
            return JsonResponse(
                {"is_created": True, "next": reverse("goal_created", kwargs = { "goal_id": goal_id})}
            )
        else:
            return JsonResponse({"is_created": False})
    return render(request, "main/check_goal.html", {"goal_id": goal_id})


def goal_created(request, goal_id):
    contexts = {}
    try:
        goal = Goal.objects.get(goal_id=goal_id, user=request.user)
    except Goal.DoesNotExist:
        return HttpResponse("不正な操作です")
    contexts["goal"] = goal
    return render(request, "main/goal_created.html", contexts)


def goal_list(request):
    contexts = {}
    goals = Goal.objects.filter(user=request.user)
    paginator = Paginator(goals, 10)
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
    return render(request, "main/goal_list.html", contexts)

def create_task(goal):
    print("creating.")
    for _ in range(15):
        time.sleep(1)
    goal.is_created = True
    goal.save()
    print("created.")


