from django.urls import path
from . import views

urlpatterns = [
    path('chat', views.chat_home, name='chat_home'),
    path('thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('start-thread/', views.start_thread, name='start_thread'),
    path('search-users/', views.search_users, name='search_users'),
    path('update-status/', views.update_user_status, name='update_user_status'),
]