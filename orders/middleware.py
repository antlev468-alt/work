from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import translation

class CheckUserExistsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if not User.objects.filter(id=request.user.id).exists():
                from django.contrib.auth import logout
                logout(request)
                messages.error(request, 'Ваш аккаунт был удалён.')
                return redirect('login')

        # Установка языка из куки
        lang = request.COOKIES.get('django_language', 'ru')
        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        return self.get_response(request)