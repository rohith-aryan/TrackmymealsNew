from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Custom user model extending AbstractUser
class User(AbstractUser):
    calorie_goal = models.FloatField(default=2000.0)  # Default calorie goal

    def __str__(self):
        return self.username


class MealNutrition(models.Model):
    name = models.CharField(max_length=255)
    calories = models.FloatField(null=True)  # Allow null values
    serving_size_g = models.FloatField(null=True)  # Allow null values
    fat_total_g = models.FloatField(null=True)  # Allow null values
    fat_saturated_g = models.FloatField(null=True)  # Allow null values
    protein_g = models.FloatField(null=True)  # Allow null values
    sodium_mg = models.FloatField(null=True)  # Allow null values
    potassium_mg = models.FloatField(null=True)  # Allow null values
    cholesterol_mg = models.FloatField(null=True)  # Allow null values
    carbohydrates_total_g = models.FloatField(null=True)  # Allow null values
    fiber_g = models.FloatField(null=True)  # Allow null values
    sugar_g = models.FloatField(null=True)  # Allow null values

    def __str__(self):
        return self.name

class MealOfTheDay(models.Model):
    MEAL_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snacks', 'Snacks'),
        ('dinner', 'Dinner'),
    ]

    meal_type = models.CharField(max_length=50, choices=MEAL_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meals')
    meal = models.ForeignKey(MealNutrition, on_delete=models.CASCADE, related_name='meal_of_day')
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.FloatField(default=1.0)  # Quantity consumed (optional)

    def __str__(self):
        return f"{self.user.username} - {self.meal_type} - {self.meal.name}"


class DailyIntake(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_intakes')
    date = models.DateField(default=timezone.now)  # Set to current date by default
    total_calories = models.FloatField(default=0.0)
    total_protein_g = models.FloatField(default=0.0)
    total_carbohydrates_g = models.FloatField(default=0.0)
    total_fiber_g = models.FloatField(default=0.0)
    weight_kg = models.FloatField(null=True, blank=True)  # Optional weight entry

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique_daily_intake')
        ]

    def update_totals(self, meals=None):
        """Update daily totals based on meals consumed."""
        if meals is None:
            meals = MealOfTheDay.objects.filter(user=self.user, created_at__date=self.date)

        self.total_calories = sum(meal.meal.calories * meal.quantity for meal in meals)
        self.total_protein_g = sum(meal.meal.protein_g * meal.quantity for meal in meals)
        self.total_carbohydrates_g = sum(meal.meal.carbohydrates_total_g * meal.quantity for meal in meals)
        self.total_fiber_g = sum(meal.meal.fiber_g * meal.quantity for meal in meals)
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.date}"
