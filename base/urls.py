from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('logout/', views.custom_logout, name='logout'),
    path('log_meal/', views.log_meal, name='log_meal'),
    path('daily_intake_summary/', views.daily_intake_summary, name='daily_intake_summary'),
     path('delete_meal/<int:meal_id>/', views.delete_meal, name='delete_meal'),
     path('edit_calorie_goal/', views.edit_calorie_goal, name='edit_calorie_goal'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Django's built-in logout view
]