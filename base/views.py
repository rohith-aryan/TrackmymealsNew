# myapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .helper import fetch_nutrition_from_api
from .models import MealNutrition, MealOfTheDay, DailyIntake, User
from django.contrib.auth.decorators import login_required
from datetime import date
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, CalorieGoalForm

from django.contrib import messages

# Import your SignUpForm here

def home_view(request):
    # Initialize the forms
    login_form = AuthenticationForm()
    signup_form = SignUpForm()

    if request.method == 'POST':
        # If login form submitted
        if 'login' in request.POST:
            login_form = AuthenticationForm(data=request.POST)  # Initialize with POST data
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('daily_intake_summary')  # Redirect to your app's homepage
        # If signup form submitted
        elif 'signup' in request.POST:  # Check for a 'signup' identifier
            signup_form = SignUpForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)  # Log in the user after signup
                return redirect('daily_intake_summary')  # Redirect to your app's homepage

    return render(request, 'base/home.html', {'login_form': login_form, 'form': signup_form})


@login_required
def edit_calorie_goal(request):
    user = request.user

    if request.method == 'POST':
        form = CalorieGoalForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('daily_intake_summary')  # Redirect to summary page after saving
    else:
        form = CalorieGoalForm(instance=user)  # Pre-fill with current user's calorie goal

    return render(request, 'base/edit_calorie_goal.html', {'form': form})
# def signup(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             try:
#                 # Log the user in automatically after signup
#                 login(request, user)
#                 messages.success(request, f'Account created successfully! Welcome, {user.username}.')
#                 return redirect('daily_intake_summary')  # Redirect to your app's homepage
#             except Exception as e:
#                 messages.error(request, 'There was an issue logging in. Please try logging in manually.')
#                 return redirect('login')
#     else:
#         form = SignUpForm()
    
#     return render(request, 'base/signup.html', {'form': form})


# def login_view(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('daily_intake_summary')  # Redirect to your app's homepage
#     else:
#         form = AuthenticationForm()
#     return render(request, 'base/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('home')

@login_required
def log_meal(request):
    # Check if there is an existing daily intake record for today
    daily_intake_exists = DailyIntake.objects.filter(user=request.user, date=date.today()).exists()

    if request.method == 'POST':
        meal_name = request.POST.get('meal_name').strip().lower()  # Normalize name
        meal_type = request.POST.get('meal_type')
        quantity = float(request.POST.get('quantity', 1))  # Default to 1 if not provided

        # Only fetch calorie_goal if there is no record for today
        calorie_goal = None
        if not daily_intake_exists:
            calorie_goal = float(request.POST.get('calorie_goal'))

        # Check if the meal exists in the database
        meal = MealNutrition.objects.filter(name__iexact=meal_name).first()

        if not meal:
            # If the meal does not exist, fetch from the API
            api_data = fetch_nutrition_from_api(meal_name)

            if api_data:
                total_nutrition = {
                    'name': '',
                    'calories': 0,
                    'protein_g': 0,
                    'carbohydrates_total_g': 0,
                    'fiber_g': 0,
                    'fat_total_g': 0,
                    'serving_size_g': 0
                }

                for item in api_data.get('items', []):
                    total_nutrition['name'] += item.get('name', '') + ', '
                    total_nutrition['calories'] += item.get('calories', 0)
                    total_nutrition['protein_g'] += item.get('protein_g', 0)
                    total_nutrition['carbohydrates_total_g'] += item.get('carbohydrates_total_g', 0)
                    total_nutrition['fiber_g'] += item.get('fiber_g', 0)
                    total_nutrition['fat_total_g'] += item.get('fat_total_g', 0)
                    total_nutrition['serving_size_g'] += item.get('serving_size_g', 0)

                total_nutrition['name'] = total_nutrition['name'].rstrip(', ')

                meal = MealNutrition.objects.create(
                    name=total_nutrition['name'].lower().strip(),
                    calories=total_nutrition['calories'],
                    protein_g=total_nutrition['protein_g'],
                    carbohydrates_total_g=total_nutrition['carbohydrates_total_g'],
                    fiber_g=total_nutrition['fiber_g'],
                    fat_total_g=total_nutrition['fat_total_g'],
                    serving_size_g=total_nutrition['serving_size_g'],
                )
            else:
                return render(request, 'base/log_meal.html', {'error': 'Meal not found in API.'})

        # Log the meal in the daily intake
        daily_intake, created = DailyIntake.objects.get_or_create(user=request.user, date=date.today())
        daily_intake.total_calories += meal.calories * quantity
        daily_intake.total_protein_g += meal.protein_g * quantity
        daily_intake.total_carbohydrates_g += meal.carbohydrates_total_g * quantity
        daily_intake.total_fiber_g += meal.fiber_g * quantity

        # Only set calorie goal if not already set (new record)
        if not daily_intake_exists and calorie_goal:
            daily_intake.calorie_goal = calorie_goal

        daily_intake.save()

        MealOfTheDay.objects.create(
            user=request.user,
            meal=meal,
            meal_type=meal_type,
            quantity=quantity,
        )

        return redirect('daily_intake_summary')

    return render(request, 'base/log_meal.html', {'daily_intake_exists': daily_intake_exists})



@login_required
def daily_intake_summary(request):
    # Fetch the meals of the day for the current user
    meals = MealOfTheDay.objects.filter(user=request.user).all()

    # Initialize total values
    total_calories = 0
    total_protein_g = 0
    total_carbohydrates_g = 0
    total_fiber_g = 0

    # Calculate total intake from meals
    for meal in meals:
        total_calories += meal.meal.calories
        total_protein_g += meal.meal.protein_g
        total_carbohydrates_g += meal.meal.carbohydrates_total_g
        total_fiber_g += meal.meal.fiber_g

    # Calculate remaining calories
    remaining_calories = request.user.calorie_goal - total_calories

    # Create a daily intake summary (if necessary)
    daily_intake = {
        'total_calories': total_calories,
        'total_protein_g': total_protein_g,
        'total_carbohydrates_g': total_carbohydrates_g,
        'total_fiber_g': total_fiber_g,
    }

    return render(request, 'base/daily_intake_summary.html', {
        'daily_intake': daily_intake,
        'meals': meals,
        'remaining_calories': remaining_calories,
        'calorie_goal': request.user.calorie_goal,
    })


@login_required
def delete_meal(request, meal_id):
    if request.method == 'POST':
        meal = get_object_or_404(MealOfTheDay, id=meal_id, user=request.user)
        meal.delete()  # Delete the meal
        return redirect('daily_intake_summary') 