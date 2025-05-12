from django import forms
from .models import Comment
from django.contrib.auth import get_user_model

User = get_user_model()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Comment',
                'maxlength': 400,
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name *',
                'maxlength': 100,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email *',
                'maxlength': 100,
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # если пользователь аутентифицирован, убираем поля name/email
        if user and user.is_authenticated:
            self.fields.pop('name')
            self.fields.pop('email')