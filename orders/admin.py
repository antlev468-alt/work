from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Order, Profile, Suggestion, Notification, PointsHistory, Response, Message


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'get_role', 'get_password_hint', 'get_rating', 'get_points', 'is_active',
                    'date_joined']
    list_filter = ['is_active', 'profile__role']
    search_fields = ['username', 'email', 'profile__password_hint']

    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except:
            return '-'

    get_role.short_description = 'Роль'

    def get_password_hint(self, obj):
        try:
            return obj.profile.password_hint
        except:
            return '-'

    get_password_hint.short_description = 'Пароль'

    def get_rating(self, obj):
        try:
            return f"{obj.profile.rating}/5"
        except:
            return '-'

    get_rating.short_description = 'Рейтинг'

    def get_points(self, obj):
        try:
            return obj.profile.total_points
        except:
            return '-'

    get_points.short_description = 'Баллы'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'executor', 'status', 'points', 'deadline', 'client_rating', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'client__username', 'executor__username']


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['order', 'executor', 'created_at']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'password_hint', 'rating', 'completed_orders', 'total_points']
    list_filter = ['role']
    search_fields = ['user__username', 'password_hint']
    readonly_fields = ['password_hint']


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'is_public', 'created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'is_read', 'created_at']


@admin.register(PointsHistory)
class PointsHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'description', 'created_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['order', 'sender', 'text', 'created_at']