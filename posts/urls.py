from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_posts'),

    path('groups/follow/', views.follow_groups, name='follow_groups'),
    path('groups/new/', views.new_group, name='new_group'),
    path('group/<slug:slug>/follow/', views.group_follow, name='group_follow'),
    path('group/<slug:slug>/unfollow/',
         views.group_unfollow, name='group_unfollow'),
    
    path('groups/', views.groups_overview, name='groups_overview'),
    path('new/', views.new_post, name='new_post'),
    path('follow/', views.follow_index, name='follow_index'),
    path('like/', views.post_like, name='post_like'),
    path('removelike/', views.post_remove_like, name='post_remove_like'),
    path('liked/', views.liked_posts, name='liked_posts'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/edit/',
         views.post_edit, name='post_edit'),
    path('<str:username>/<int:post_id>/comment',
         views.add_comment, name='add_comment'),
    path('<str:username>/<int:post_id>/remove-comment/<int:comment_id>',
         views.del_comment, name='del_comment'),
    path('<str:username>/follow/',
         views.profile_follow, name='profile_follow'),
    path('<str:username>/unfollow/',
         views.profile_unfollow, name='profile_unfollow'),
]
