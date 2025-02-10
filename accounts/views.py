from django.shortcuts import render, redirect
from accounts.forms import CustomUserCreateForm, CustomUserLoginForm
from django.contrib.auth import login
import secrets

# Create your views here.

def signup(request):
    contexts = {}
    contexts["form"] = CustomUserCreateForm()
    if request.method == "POST":
        form = CustomUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_id = secrets.token_urlsafe(32)
            user.save()
            login(request, user)
            return redirect("index")
        else:
            contexts["form"] = form
    return render(request, "accounts/signup.html", contexts)


def login_view(request):
    contexts = {}
    contexts["form"] = CustomUserLoginForm()
    return render(request, "accounts/login.html", contexts)