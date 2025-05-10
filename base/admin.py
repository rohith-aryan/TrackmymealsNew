from django.contrib import admin
from .models import MealNutrition,MealOfTheDay,User

# Register your models here.
admin.site.register(User)
admin.site.register(MealNutrition)
admin.site.register(MealOfTheDay)