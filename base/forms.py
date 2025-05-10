from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    # Override the clean_password2 method to remove password validation
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return password2

    # Override the save method to hash the password without validation
    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # Hash the password
        if commit:
            user.save()
        return user
    

class CalorieGoalForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['calorie_goal']  # Include the calorie_goal field
        widgets = {
            'calorie_goal': forms.NumberInput(attrs={'step': '0.1'}),
        }
        labels = {
            'calorie_goal': 'New Calorie Goal',
        }
