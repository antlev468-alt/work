from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


class Profile(models.Model):
    ROLE_CHOICES = [
        ('client', 'Клиент'),
        ('executor', 'Исполнитель'),
        ('both', 'Клиент и Исполнитель'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True, null=True)
    rating = models.FloatField(default=0, verbose_name='Рейтинг')
    total_ratings = models.IntegerField(default=0, verbose_name='Всего оценок')
    completed_orders = models.IntegerField(default=0, verbose_name='Выполнено заказов')
    total_points = models.IntegerField(default=0, verbose_name='Всего баллов')
    password_hint = models.CharField(max_length=128, blank=True, null=True, verbose_name='Пароль')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    skills = models.TextField(blank=True, null=True, verbose_name='Навыки')
    about = models.TextField(blank=True, null=True, verbose_name='О себе')

    def update_rating(self, new_rating):
        self.total_ratings += 1
        self.rating = round((self.rating * (self.total_ratings - 1) + new_rating) / self.total_ratings, 1)
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('done', 'Выполнен'),
        ('rated', 'Оценен'),
        ('cancelled', 'Отменён'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название заказа')
    description = models.TextField(verbose_name='Описание')
    points = models.IntegerField(default=0, verbose_name='Баллы за выполнение')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='Срок выполнения')

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders_as_client', verbose_name='Клиент')
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_as_executor', verbose_name='Исполнитель')

    client_rating = models.IntegerField(null=True, blank=True, verbose_name='Оценка')
    client_review = models.TextField(blank=True, null=True, verbose_name='Текстовый отзыв')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    def is_overdue(self):
        if self.deadline and self.status in ['new', 'in_progress']:
            return timezone.now() > self.deadline
        return False

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class Response(models.Model):
    """Отклик на заказ"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='responses')
    executor = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Сопроводительный текст', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['order', 'executor']

    def __str__(self):
        return f"{self.executor.username} → {self.order.title}"


class Message(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.text[:30]}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    text = models.CharField(max_length=500, verbose_name='Текст')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    link = models.CharField(max_length=200, blank=True, null=True, verbose_name='Ссылка')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.text[:50]}"


class PointsHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField(verbose_name='Количество баллов')
    description = models.CharField(max_length=300, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.amount} баллов"


class Suggestion(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новое'),
        ('reviewed', 'Рассмотрено'),
        ('done', 'Выполнено'),
        ('rejected', 'Отклонено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    title = models.CharField(max_length=200, verbose_name='Тема')
    text = models.TextField(verbose_name='Предложение')
    is_public = models.BooleanField(default=True, verbose_name='Публичное')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    admin_comment = models.TextField(blank=True, null=True, verbose_name='Комментарий админа')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    likes = models.ManyToManyField(User, related_name='liked_suggestions', blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.user.username}: {self.title}"