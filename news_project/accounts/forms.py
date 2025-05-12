from django import forms
from news.models import Profile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Создаём связанный профиль сразу после сохранения пользователя
            Profile.objects.create(user=user)
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'avatar')

class ProfileAndUserForm(forms.ModelForm):
    # Поля «избыточные» для User
    username = forms.CharField(
        label="Username",
        max_length=150,
        required=True,
        help_text="Только буквы, цифры и @/./+/-/_"
    )
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = Profile
        fields = [
            'avatar',
            'bio',
            'email'
        ]

    def __init__(self, *args, **kwargs):
        # expecting instance=profile
        super().__init__(*args, **kwargs)
        # проставляем initial для User-полей
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username).exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise forms.ValidationError("Это имя уже занято.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = User.objects.filter(email=email).exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise forms.ValidationError("Этот email уже используется.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile.save()
        return profile

class UserLoginForm(AuthenticationForm):
    # новые тексты ошибок
    error_messages = {
        'invalid_login': 'Неверное имя пользователя или пароль. Пожалуйста, попробуйте ещё раз.',
        'inactive': 'Учётная запись не активна.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Введите имя пользователя",
        })
        self.fields['password'].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Введите пароль",
        })