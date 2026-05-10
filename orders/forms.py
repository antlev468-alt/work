from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Order, Suggestion, Response


class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('client', 'Клиент'),
        ('executor', 'Исполнитель'),
        ('both', 'Клиент и Исполнитель'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Роль')
    phone = forms.CharField(max_length=20, required=False, label='Телефон')

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role', 'phone']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                phone=self.cleaned_data.get('phone', ''),
                password_hint=self.cleaned_data['password1']
            )
        return user


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['title', 'description', 'points', 'deadline']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'points': 'Баллы за выполнение',
            'deadline': 'Срок выполнения (необязательно)',
        }


class RatingForm(forms.ModelForm):
    client_rating = forms.IntegerField(
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={'min': 0, 'max': 5}),
        label='Оценка (0-5)'
    )
    client_review = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Текстовый отзыв'
    )

    class Meta:
        model = Order
        fields = ['client_rating', 'client_review']


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Почему вы подходите для этого заказа?'}),
        }
        labels = {
            'text': 'Сопроводительный текст',
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'avatar', 'skills', 'about']
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Python, Django, HTML...'}),
            'about': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Расскажите о себе...'}),
        }
        labels = {
            'phone': 'Телефон',
            'avatar': 'Фото',
            'skills': 'Навыки',
            'about': 'О себе',
        }


class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['title', 'text', 'is_public']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'title': 'Тема',
            'text': 'Предложение',
            'is_public': 'Опубликовать публично',
        }