from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Profile, Order, Message, Suggestion, Notification, Response, PointsHistory
from .forms import UserRegistrationForm, OrderForm, RatingForm, ResponseForm, ProfileEditForm, SuggestionForm
from django.utils.translation import activate
from django.conf import settings
from django.utils import translation
from django.utils import translation
from django.shortcuts import redirect
from django.utils import translation


def create_notification(user, text, link=None):
    Notification.objects.create(user=user, text=text, link=link)


from django.utils import translation

def set_language(request):
    lang = request.GET.get('lang', 'ru')
    if lang not in ['ru', 'en', 'kk']:
        lang = 'ru'
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    response.set_cookie('django_language', lang, max_age=365*24*60*60)
    return response

def add_points(user, amount, description):
    profile = Profile.objects.get_or_create(user=user)[0]
    profile.total_points += amount
    profile.save()
    PointsHistory.objects.create(user=user, amount=amount, description=description)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна!')
            return redirect('orders:order_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'orders/register.html', {'form': form})


@login_required
def order_list(request):
    orders = Order.objects.all()
    search = request.GET.get('search', '')
    if search:
        orders = orders.filter(title__icontains=search)
    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)
    points_from = request.GET.get('points_from', '')
    points_to = request.GET.get('points_to', '')
    if points_from:
        orders = orders.filter(points__gte=int(points_from))
    if points_to:
        orders = orders.filter(points__lte=int(points_to))
    orders = orders.order_by('-created_at')
    is_admin = request.user.is_superuser
    return render(request, 'orders/order_list.html', {
        'orders': orders, 'is_admin': is_admin,
        'search': search, 'status_filter': status,
        'points_from': points_from, 'points_to': points_to,
    })


@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = request.user
            order.save()
            messages.success(request, 'Заказ создан!')
            return redirect('orders:order_list')
    else:
        form = OrderForm()
    return render(request, 'orders/create_order.html', {'form': form})


@login_required
def respond_order(request, order_id):
    """Отклик на заказ"""
    order = get_object_or_404(Order, id=order_id, status='new')
    if order.client == request.user:
        messages.error(request, 'Нельзя откликнуться на свой заказ.')
        return redirect('orders:order_list')
    if Response.objects.filter(order=order, executor=request.user).exists():
        messages.error(request, 'Вы уже откликнулись.')
        return redirect('orders:order_list')
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            resp = form.save(commit=False)
            resp.order = order
            resp.executor = request.user
            resp.save()
            create_notification(order.client, f'📩 {request.user.username} откликнулся на заказ "{order.title}"')
            messages.success(request, 'Отклик отправлен!')
            return redirect('orders:order_list')
    else:
        form = ResponseForm()
    return render(request, 'orders/respond.html', {'form': form, 'order': order})


@login_required
def order_responses(request, order_id):
    """Заказчик видит отклики"""
    order = get_object_or_404(Order, id=order_id, client=request.user)
    responses = order.responses.all()
    return render(request, 'orders/responses.html', {'order': order, 'responses': responses})


@login_required
def accept_response(request, response_id):
    """Заказчик выбирает исполнителя"""
    resp = get_object_or_404(Response, id=response_id, order__client=request.user, order__status='new')
    order = resp.order
    order.executor = resp.executor
    order.status = 'in_progress'
    order.save()
    create_notification(resp.executor, f'🎉 Вас выбрали исполнителем заказа "{order.title}"!')
    messages.success(request, f'Исполнитель {resp.executor.username} назначен!')
    return redirect('orders:order_list')


@login_required
def take_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'new':
        messages.error(request, 'Этот заказ уже нельзя взять.')
        return redirect('orders:order_list')
    order.status = 'in_progress'
    order.executor = request.user
    order.save()
    create_notification(order.client, f'🔔 {request.user.username} взял ваш заказ "{order.title}"')
    messages.success(request, f'Вы взяли заказ "{order.title}"!')
    return redirect('orders:order_list')


@login_required
def complete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.executor != request.user and not request.user.is_superuser:
        messages.error(request, 'Вы не можете отметить этот заказ.')
        return redirect('orders:order_list')
    order.status = 'done'
    order.save()
    create_notification(order.client, f'✅ {request.user.username} выполнил заказ "{order.title}". Оцените работу!')
    messages.success(request, f'Заказ "{order.title}" выполнен!')
    return redirect('orders:order_list')


@login_required
def rate_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, client=request.user, status='done')
    if request.method == 'POST':
        form = RatingForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            order.status = 'rated'
            order.save()
            if order.executor:
                profile, _ = Profile.objects.get_or_create(user=order.executor)
                profile.completed_orders += 1
                profile.update_rating(order.client_rating)
                add_points(order.executor, order.points, f'Заказ "{order.title}"')
                create_notification(order.executor, f'⭐ Заказ "{order.title}" оценён на {order.client_rating}/5. +{order.points} баллов!')
            messages.success(request, f'Оценка {order.client_rating}/5 поставлена!')
            return redirect('orders:order_list')
    else:
        form = RatingForm(instance=order)
    return render(request, 'orders/rate_order.html', {'form': form, 'order': order})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.client != request.user and not request.user.is_superuser:
        messages.error(request, 'Вы не можете отменить этот заказ.')
        return redirect('orders:order_list')
    order.status = 'cancelled'
    order.save()
    messages.success(request, f'Заказ "{order.title}" отменён!')
    return redirect('orders:order_list')


@login_required
def delete_order(request, order_id):
    if not request.user.is_superuser:
        messages.error(request, 'Только админ может удалять заказы.')
        return redirect('orders:order_list')
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    messages.success(request, 'Заказ удалён!')
    return redirect('orders:order_list')


@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    client_orders = Order.objects.filter(client=request.user)
    executor_orders = Order.objects.filter(executor=request.user)
    points_history = PointsHistory.objects.filter(user=request.user).order_by('-created_at')[:20]
    return render(request, 'orders/profile.html', {
        'profile': profile,
        'client_orders': client_orders,
        'executor_orders': executor_orders,
        'points_history': points_history,
    })


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён!')
            return redirect('orders:profile')
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'orders/edit_profile.html', {'form': form})


def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Аккаунт удалён.')
        return redirect('orders:order_list')
    return render(request, 'orders/delete_account.html')


@login_required
def chat(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.user != order.client and request.user != order.executor:
        messages.error(request, 'Нет доступа к чату.')
        return redirect('orders:order_list')
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(order=order, sender=request.user, text=text)
        return redirect('orders:chat', order_id=order.id)
    if request.GET.get('format') == 'json':
        msgs = list(order.messages.all().order_by('created_at').values('sender__username', 'text', 'created_at'))
        data = [{'sender': m['sender__username'], 'text': m['text'], 'time': m['created_at'].strftime('%H:%M')} for m in msgs]
        return JsonResponse({'messages': data})
    chat_messages = order.messages.all().order_by('created_at')
    return render(request, 'orders/chat.html', {'order': order, 'chat_messages': chat_messages})


@login_required
def notifications(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:30]
    return render(request, 'orders/notifications.html', {'notifications': notifs})


@login_required
def mark_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect('orders:notifications')


@login_required
def unread_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def suggestion_list(request):
    suggestions = Suggestion.objects.filter(is_public=True).order_by('-created_at')
    user_suggestions = Suggestion.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/suggestions.html', {'suggestions': suggestions, 'user_suggestions': user_suggestions})


@login_required
def create_suggestion(request):
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            sug = form.save(commit=False)
            sug.user = request.user
            sug.save()
            messages.success(request, 'Предложение отправлено!')
            return redirect('orders:suggestion_list')
    else:
        form = SuggestionForm()
    return render(request, 'orders/create_suggestion.html', {'form': form})


@login_required
def like_suggestion(request, suggestion_id):
    suggestion = get_object_or_404(Suggestion, id=suggestion_id)
    if request.user in suggestion.likes.all():
        suggestion.likes.remove(request.user)
    else:
        suggestion.likes.add(request.user)
    return redirect('orders:suggestion_list')


@login_required
def update_suggestion_status(request, suggestion_id):
    if not request.user.is_superuser:
        messages.error(request, 'Только админ может менять статус.')
        return redirect('orders:suggestion_list')
    suggestion = get_object_or_404(Suggestion, id=suggestion_id)
    if request.method == 'POST':
        suggestion.status = request.POST.get('status', 'new')
        suggestion.admin_comment = request.POST.get('admin_comment', '')
        suggestion.save()
        messages.success(request, f'Статус обновлён!')
    return redirect('orders:suggestion_list')