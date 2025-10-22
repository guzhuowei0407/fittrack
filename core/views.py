from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserProfileForm
from django.views.decorators.cache import never_cache


@never_cache
def home(request):
    return render(request, 'home.html')


def add_data(request):
    return render(request, 'add_data.html')


def import_csv(request):
    return render(request, 'import_csv.html')


def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {"profile": profile})


@login_required
def profile_edit(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'profile_edit.html', {"form": form})


def login_submit(request):
    if request.method != 'POST':
        return redirect('/')
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        auth_login(request, user)
        return redirect('/profile/')
    return redirect('/')


def logout_view(request):
    auth_logout(request)
    return redirect('/')

@login_required
def exercises(request):
    items = [
        {"key": "pushup", "name": "Push-up", "desc": "Keep a straight line from head to heels; lower chest near floor; elbows ~45°.", "youtube_id": "I9fsqKE5XHo"},
        {"key": "situp", "name": "Sit-up", "desc": "Engage core to lift torso; avoid pulling with neck or lower back.", "youtube_id": "pCX65Mtc_Kk"},
        {"key": "squat", "name": "Squat", "desc": "Hips back, knees track over toes (not far past); spine neutral.", "youtube_id": "2t3Ab7a2ZM4"},
        {"key": "bench", "name": "Bench Press", "desc": "Stable chest/shoulders/elbows; bar path vertically down and up.", "youtube_id": "hWbUlkb5Ms4"},
        {"key": "deadlift", "name": "Deadlift", "desc": "Flat back; coordinate knees and hips; bar travels close to legs.", "youtube_id": "ZaTM37cfiDs"},
        {"key": "plank", "name": "Plank", "desc": "Body in a straight line; avoid hips too high or sagging.", "youtube_id": "6LqqeBtFn9M"},
        {"key": "pullup", "name": "Pull-up", "desc": "Control the rhythm up and down; use assisted variations if needed.", "youtube_id": "eGo4IYlbE5g"},
        {"key": "lunges", "name": "Lunges", "desc": "Front and back knee at safe angles; front knee not beyond toes.", "youtube_id": "1LuRcKJMn8w"},
        {"key": "burpee", "name": "Burpee", "desc": "Combine squat, push-up, and jump in a smooth sequence.", "youtube_id": "NCqbpkoiyXE"},
        {"key": "climbers", "name": "Mountain Climbers", "desc": "Fast and stable pace; use core to control body.", "youtube_id": "cnyTQDSE884"},
        {"key": "jumprope", "name": "Jump Rope", "desc": "Use wrists to turn rope; light on toes with quick rebounds.", "youtube_id": "wqN5bRkZPK0"},
        {"key": "rowing", "name": "Rowing Machine", "desc": "Drive sequence: legs → body → arms; recover in reverse order.", "youtube_id": "ZN0J6qKCIrI"},
    ]
    return render(request, 'exercises.html', {"items": items})

