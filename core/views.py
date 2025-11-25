from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, WorkoutSession, ExerciseSet, Exercise, PasswordResetCode
from .forms import (
    UserProfileForm,
    WorkoutSessionForm,
    ExerciseSetForm,
    RegistrationForm,
    ForgotPasswordForm,
    ResetPasswordCodeForm,
    WeightHistoryForm,
)
from django.views.decorators.cache import never_cache
from .ai_planner import generate_fitness_plan_from_profile
from django.forms import formset_factory
from django.http import JsonResponse
import json
import csv
import io
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
import hashlib, secrets, datetime as dt


@never_cache
def home(request):
    return render(request, 'home.html')


@login_required
def add_data(request):
    ExerciseSetFormSet = formset_factory(ExerciseSetForm, extra=1, can_delete=True)
    
    if request.method == 'POST':
        workout_form = WorkoutSessionForm(request.POST)
        formset = ExerciseSetFormSet(request.POST)
        
        if workout_form.is_valid() and formset.is_valid():
            # Create the workout session
            workout = workout_form.save(commit=False)
            workout.user = request.user
            workout.save()
            
            # Create exercise sets
            exercise_count = 0
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                    if form.cleaned_data.get('exercise'):  # Only save if exercise is selected
                        exercise_set = form.save(commit=False)
                        exercise_set.workout = workout
                        exercise_set.save()
                        exercise_count += 1
            
            messages.success(request, f'Workout data added successfully! Added {exercise_count} exercise(s).')
            return redirect('dashboard')
        else:
            # Show specific errors
            if not workout_form.is_valid():
                for field, errors in workout_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            messages.error(request, 'Please correct the errors below.')
    else:
        # Initialize with current time
        initial_date = timezone.now().strftime('%Y-%m-%dT%H:%M')
        workout_form = WorkoutSessionForm(initial={'date': initial_date})
        formset = ExerciseSetFormSet()
    
    # Get all exercises for the dropdown
    exercises = Exercise.objects.all().order_by('name')
    
    return render(request, 'add_data.html', {
        'workout_form': workout_form,
        'formset': formset,
        'exercises': exercises
    })


@login_required
def import_csv(request):
    from .forms import CSVImportForm
    
    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            # Check if it's a CSV file
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a valid CSV file.')
                return render(request, 'import_csv.html', {'form': form})
            
            try:
                # Read CSV file
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                
                imported_count = 0
                error_rows = []
                
                for row_num, row in enumerate(reader, start=2):  # Start from 2 (after header)
                    try:
                        # Parse the CSV row and create workout session
                        workout_date = datetime.strptime(row.get('date', ''), '%Y-%m-%d %H:%M:%S')
                        
                        # Create or get workout session
                        workout, created = WorkoutSession.objects.get_or_create(
                            user=request.user,
                            date=workout_date,
                            defaults={
                                'duration_minutes': int(row.get('duration_minutes', 0)) if row.get('duration_minutes') else None,
                                'notes': row.get('notes', '')
                            }
                        )
                        
                        # Get or create exercise
                        exercise_name = row.get('exercise', '').strip()
                        if exercise_name:
                            exercise, _ = Exercise.objects.get_or_create(
                                name=exercise_name,
                                defaults={'category': 'other', 'description': f'Imported from CSV: {exercise_name}'}
                            )
                            
                            # Create exercise set
                            ExerciseSet.objects.create(
                                workout=workout,
                                exercise=exercise,
                                sets=int(row.get('sets', 1)),
                                reps=int(row.get('reps', 0)) if row.get('reps') else None,
                                weight_kg=float(row.get('weight_kg', 0)) if row.get('weight_kg') else None,
                                duration_seconds=int(row.get('duration_seconds', 0)) if row.get('duration_seconds') else None,
                                distance_km=float(row.get('distance_km', 0)) if row.get('distance_km') else None,
                                notes=row.get('exercise_notes', '')
                            )
                            
                            imported_count += 1
                        
                    except Exception as e:
                        error_rows.append(f"Row {row_num}: {str(e)}")
                
                if imported_count > 0:
                    messages.success(request, f'Successfully imported {imported_count} exercise records.')
                
                if error_rows:
                    error_msg = "Some rows had errors:\n" + "\n".join(error_rows[:5])  # Show first 5 errors
                    if len(error_rows) > 5:
                        error_msg += f"\n... and {len(error_rows) - 5} more errors."
                    messages.warning(request, error_msg)
                
                if imported_count > 0:
                    return redirect('dashboard')
                    
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
    else:
        form = CSVImportForm()
    
    return render(request, 'import_csv.html', {'form': form})


@login_required
def export_csv(request):
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_workout_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['date', 'exercise', 'sets', 'reps', 'weight_kg', 'duration_minutes', 'duration_seconds', 'distance_km', 'notes', 'exercise_notes'])
    
    # Get all user's exercise sets with workout info
    exercise_sets = ExerciseSet.objects.filter(workout__user=request.user).select_related('workout', 'exercise').order_by('workout__date')
    
    for exercise_set in exercise_sets:
        writer.writerow([
            exercise_set.workout.date.strftime('%Y-%m-%d %H:%M:%S'),
            exercise_set.exercise.name,
            exercise_set.sets,
            exercise_set.reps or '',
            exercise_set.weight_kg or '',
            exercise_set.workout.duration_minutes or '',
            exercise_set.duration_seconds or '',
            exercise_set.distance_km or '',
            exercise_set.workout.notes or '',
            exercise_set.notes or ''
        ])
    
    return response


@login_required
def dashboard(request):
    from django.db.models import Sum
    import json
    
    # Get user's recent workouts
    recent_workouts = WorkoutSession.objects.filter(user=request.user).order_by('-date')[:10]
    
    # Calculate total exercise duration for workouts without duration_minutes
    for workout in recent_workouts:
        if not workout.duration_minutes:
            # Sum all exercise durations in seconds
            total_seconds = workout.exercise_sets.aggregate(
                total=Sum('duration_seconds')
            )['total']
            if total_seconds:
                # Convert to minutes and store as attribute
                workout.calculated_duration = round(total_seconds / 60, 1)
            else:
                workout.calculated_duration = None
    
    # Get some basic stats
    total_workouts = WorkoutSession.objects.filter(user=request.user).count()
    total_exercises = ExerciseSet.objects.filter(workout__user=request.user).count()
    
    # Build 7-day, 30-day window anchored to the latest workout date (fallback: today)
    from datetime import datetime as py_dt, time as py_time, timedelta as py_timedelta
    latest_dt = WorkoutSession.objects.filter(user=request.user).order_by('-date').values_list('date', flat=True).first()
    anchor_date = timezone.localtime(latest_dt).date() if latest_dt else timezone.localtime().date()
    
    # 7-day chart data
    last_7_days = [anchor_date - py_timedelta(days=i) for i in range(6, -1, -1)]
    daily_totals_7 = {d: 0 for d in last_7_days}
    start_dt_7 = timezone.make_aware(py_dt.combine(last_7_days[0], py_time.min))
    end_dt_7 = timezone.make_aware(py_dt.combine(last_7_days[-1], py_time.max))
    recent_range_workouts_7 = WorkoutSession.objects.filter(
        user=request.user,
        date__range=(start_dt_7, end_dt_7),
    ).order_by('date').prefetch_related('exercise_sets')
    for w in recent_range_workouts_7:
        day = timezone.localtime(w.date).date()
        minutes = 0
        if w.duration_minutes:
            minutes = int(w.duration_minutes)
        else:
            sec_total = 0
            for es in w.exercise_sets.all():
                if es.duration_seconds:
                    sec_total += es.duration_seconds
            if sec_total:
                minutes = round(sec_total / 60)
        daily_totals_7[day] = daily_totals_7.get(day, 0) + minutes
    
    chart_labels_7 = [d.strftime('%m-%d') for d in last_7_days]
    chart_values_7 = [daily_totals_7.get(d, 0) for d in last_7_days]
    
    # 30-day chart data
    last_30_days = [anchor_date - py_timedelta(days=i) for i in range(29, -1, -1)]
    daily_totals_30 = {d: 0 for d in last_30_days}
    start_dt_30 = timezone.make_aware(py_dt.combine(last_30_days[0], py_time.min))
    end_dt_30 = timezone.make_aware(py_dt.combine(last_30_days[-1], py_time.max))
    recent_range_workouts_30 = WorkoutSession.objects.filter(
        user=request.user,
        date__range=(start_dt_30, end_dt_30),
    ).order_by('date').prefetch_related('exercise_sets')
    for w in recent_range_workouts_30:
        day = timezone.localtime(w.date).date()
        minutes = 0
        if w.duration_minutes:
            minutes = int(w.duration_minutes)
        else:
            sec_total = 0
            for es in w.exercise_sets.all():
                if es.duration_seconds:
                    sec_total += es.duration_seconds
            if sec_total:
                minutes = round(sec_total / 60)
        daily_totals_30[day] = daily_totals_30.get(day, 0) + minutes
    
    chart_labels_30 = [d.strftime('%m-%d') for d in last_30_days]
    chart_values_30 = [daily_totals_30.get(d, 0) for d in last_30_days]
    
    # Weight history data (with timestamps from profile history or from weight entries)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    weight_history = []
    weight_labels = []
    
    # Get all workouts with dates for weight tracking
    all_workouts = WorkoutSession.objects.filter(user=request.user).order_by('date')
    if profile.weight_kg and all_workouts.exists():
        # For now, use current weight as the reference
        # In future, you can create a WeightHistory model to track weight changes
        current_weight = profile.weight_kg
        weight_history = [current_weight]
        weight_labels = ['Current']
    
    # Get weight history from WeightHistory model
    from .models import WeightHistory
    weight_records = WeightHistory.objects.filter(user=request.user).order_by('recorded_date')
    
    if weight_records.exists():
        weight_history = [round(w.weight_kg, 1) for w in weight_records]
        weight_labels = [w.recorded_date.strftime('%m-%d') for w in weight_records]
    elif profile.weight_kg:
        # If no history, create initial data point
        weight_history = [profile.weight_kg]
        weight_labels = ['Today']
    else:
        weight_history = []
        weight_labels = []
    
    context = {
        'recent_workouts': recent_workouts,
        'total_workouts': total_workouts,
        'total_exercises': total_exercises,
        'weekly_chart_labels': chart_labels_7,
        'weekly_chart_values': chart_values_7,
        'monthly_chart_labels': chart_labels_30,
        'monthly_chart_values': chart_values_30,
        'weight_labels': json.dumps(weight_labels),
        'weight_values': json.dumps(weight_history),
        'profile': profile,
    }
    return render(request, 'dashboard.html', context)


@login_required
def export_csv(request):
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_workout_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['date', 'exercise', 'sets', 'reps', 'weight_kg', 'duration_minutes', 'duration_seconds', 'distance_km', 'notes', 'exercise_notes'])
    
    # Get all user's exercise sets with workout info
    exercise_sets = ExerciseSet.objects.filter(workout__user=request.user).select_related('workout', 'exercise').order_by('workout__date')
    
    for exercise_set in exercise_sets:
        writer.writerow([
            exercise_set.workout.date.strftime('%Y-%m-%d %H:%M:%S'),
            exercise_set.exercise.name,
            exercise_set.sets,
            exercise_set.reps or '',
            exercise_set.weight_kg or '',
            exercise_set.workout.duration_minutes or '',
            exercise_set.duration_seconds or '',
            exercise_set.distance_km or '',
            exercise_set.workout.notes or '',
            exercise_set.notes or ''
        ])
    
    return response


@login_required
def workout_detail(request, workout_id):
    from django.db.models import Sum
    workout = get_object_or_404(WorkoutSession, id=workout_id, user=request.user)
    exercise_sets = workout.exercise_sets.all().select_related('exercise')
    
    # Calculate total duration from exercises if not set
    calculated_duration = None
    if not workout.duration_minutes:
        total_seconds = exercise_sets.aggregate(total=Sum('duration_seconds'))['total']
        if total_seconds:
            calculated_duration = round(total_seconds / 60, 1)
    
    return render(request, 'workout_detail.html', {
        'workout': workout,
        'exercise_sets': exercise_sets,
        'calculated_duration': calculated_duration
    })


@login_required
def workout_delete(request, workout_id):
    workout = get_object_or_404(WorkoutSession, id=workout_id, user=request.user)
    
    if request.method == 'POST':
        workout.delete()
        messages.success(request, 'Workout deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'workout_confirm_delete.html', {
        'workout': workout
    })


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'profile.html', {"profile": profile})


@login_required
def profile_edit(request):
    # Ensure user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')
    
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            # Use reverse to get the URL, or direct path
            return redirect('profile')
        else:
            # Form has errors, show them
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'profile_edit.html', {"form": form, "profile": profile})


def login_submit(request):
    if request.method != 'POST':
        return redirect('/')
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        auth_login(request, user)
        return redirect('/profile/')
    messages.error(request, 'Invalid username or password. Please try again.')
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


@login_required
def ai_planner(request):
    """
    AI Planner view - generates personalized fitness plan based on user profile.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    result_text = None
    error_text = None
    
    # Check if user has filled in their profile
    if not profile.gender or not profile.age or not profile.height_cm or not profile.weight_kg:
        error_text = "Please complete your profile first (Gender, Age, Height, Weight) before generating a plan. Go to Profile > Edit Profile to update your information."
        return render(request, 'ai_planner.html', {
            'profile': profile,
            'result': result_text,
            'error': error_text
        })
    
    if request.method == 'POST':
        try:
            # Generate the fitness plan using the AI planner
            result_text = generate_fitness_plan_from_profile(profile)
        except Exception as e:
            error_text = f"An error occurred while generating the plan: {str(e)}"
    
    return render(request, 'ai_planner.html', {
        'profile': profile,
        'result': result_text,
        'error': error_text
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user)
            messages.success(request, 'Registration successful. You can now sign in.')
            return redirect('/')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'No account with that email.')
                return redirect('forgot_password')
            code = f"{secrets.randbelow(1000000):06d}"
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            expires = timezone.now() + dt.timedelta(minutes=15)
            PasswordResetCode.objects.create(user=user, email=email, code_hash=code_hash, expires_at=expires)
            subject = 'Your FitTrack+ password reset code'
            body = f"Your verification code is: {code}\nIt expires in 15 minutes."
            sender = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', '')
            try:
                send_mail(subject, body, sender, [email], fail_silently=False)
                messages.success(request, 'Verification code sent to your email.')
                # In development, if using console email backend, also show the code for convenience
                if getattr(settings, 'EMAIL_BACKEND', '').endswith('console.EmailBackend'):
                    messages.info(request, f'(Dev) Your code: {code}')
            except Exception:
                messages.error(request, 'Failed to send email. Please contact support.')
            return redirect('reset_password_code')
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})


def reset_password_code(request):
    if request.method == 'POST':
        form = ResetPasswordCodeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            code = form.cleaned_data['code']
            new1 = form.cleaned_data['new_password1']
            new2 = form.cleaned_data['new_password2']
            if new1 != new2:
                messages.error(request, 'Passwords do not match.')
                return redirect('reset_password_code')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'Invalid email.')
                return redirect('reset_password_code')
            code_hash = hashlib.sha256(code.encode()).hexdigest()
            prc = PasswordResetCode.objects.filter(user=user, email=email, code_hash=code_hash, used_at__isnull=True).order_by('-created_at').first()
            if not prc or not prc.is_valid():
                messages.error(request, 'Invalid or expired code.')
                return redirect('reset_password_code')
            user.set_password(new1)
            user.save()
            prc.used_at = timezone.now()
            prc.save(update_fields=['used_at'])
            messages.success(request, 'Password reset successful. You can now sign in.')
            return redirect('/')
    else:
        form = ResetPasswordCodeForm()
    return render(request, 'reset_password_code.html', {'form': form})


@login_required
def log_weight(request):
    """Log user's weight for tracking"""
    from .models import WeightHistory
    
    if request.method == 'POST':
        form = WeightHistoryForm(request.POST)
        if form.is_valid():
            weight_entry = form.save(commit=False)
            weight_entry.user = request.user
            weight_entry.save()
            
            # Also update user profile weight
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.weight_kg = weight_entry.weight_kg
            profile.save()
            
            messages.success(request, f'Weight logged successfully: {weight_entry.weight_kg} kg')
            return redirect('dashboard')
    else:
        # Pre-fill with current weight
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        form = WeightHistoryForm(initial={'weight_kg': profile.weight_kg})
    
    return render(request, 'log_weight.html', {'form': form})
