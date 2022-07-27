from django import forms
from .models import Order
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserUpdateForm(UserCreationForm):
    tel = forms.CharField(max_length=20, required=False)
    avatar = forms.ImageField(required=False)
    # username = forms.CharField(max_length=100)
    # email = forms.EmailField(required=False)
    # password1 = forms.CharField(widget=forms.PasswordInput())
    # password2 = forms.CharField(widget=forms.PasswordInput())
    # first_name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ('username', 'tel', 'email', 'first_name', 'avatar', 'password1', 'password2')


class UserRegistrationForm(UserCreationForm):
    tel = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'tel', 'email', 'password1', 'password2')


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = (
             'address', 'payment_method',  'city', 'delivery_method'
        )


class AuthForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class RestorePasswordForm(forms.Form):
    email = forms.EmailField()