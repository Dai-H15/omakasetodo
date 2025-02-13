from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from accounts.forms import CustomUserCreateForm, CustomUserLoginForm
from django.contrib.auth import login, logout, authenticate
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
    if request.method == "POST":
        form = CustomUserLoginForm(request, data=request.POST)
        contexts["form"] = form
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
            return redirect("index")
        else:
            print(form.errors)
    return render(request, "accounts/login.html", contexts)

@login_required
def logout_view(request):
    logout(request)
    return redirect("index")
