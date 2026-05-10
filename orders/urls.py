from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('register/', views.register, name='register'),
    path('create/', views.create_order, name='create_order'),
    path('respond/<int:order_id>/', views.respond_order, name='respond_order'),
    path('responses/<int:order_id>/', views.order_responses, name='order_responses'),
    path('accept/<int:response_id>/', views.accept_response, name='accept_response'),
    path('take/<int:order_id>/', views.take_order, name='take_order'),
    path('complete/<int:order_id>/', views.complete_order, name='complete_order'),
    path('rate/<int:order_id>/', views.rate_order, name='rate_order'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('chat/<int:order_id>/', views.chat, name='chat'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read/<int:notif_id>/', views.mark_read, name='mark_read'),
    path('notifications/count/', views.unread_count, name='unread_count'),
    path('suggestions/', views.suggestion_list, name='suggestion_list'),
    path('suggestions/create/', views.create_suggestion, name='create_suggestion'),
    path('suggestions/like/<int:suggestion_id>/', views.like_suggestion, name='like_suggestion'),
    path('suggestions/update/<int:suggestion_id>/', views.update_suggestion_status, name='update_suggestion_status'),
]