from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Убираем help_text у полей
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone_number = cleaned_data.get('phone_number')

        if not email and not phone_number:
            raise forms.ValidationError("You must provide either an email or a phone number.")

        return cleaned_data


User = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Email or Phone Number")

    def clean_username(self):
        username = self.cleaned_data['username']
        if '@' in username:
            user = User.objects.filter(email=username).first()
        else:
            user = User.objects.filter(phone_number=username).first()

        if not user:
            raise forms.ValidationError("No user found with this email or phone number.")

        return username
