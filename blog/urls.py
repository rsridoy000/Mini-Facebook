from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('feed/', views.feed_view, name='feed'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('profile/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/read/', views.mark_all_read, name='mark_all_read'),
]
