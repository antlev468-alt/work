from django.shortcuts import redirect
from django.contrib import messages

class CheckUserExistsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            from django.contrib.auth.models import User
            if not User.objects.filter(id=request.user.id).exists():
                messages.error(request, 'Ваш аккаунт был удалён.')
                return redirect('login')
        return self.get_response(request)