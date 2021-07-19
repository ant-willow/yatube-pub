
import json

from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Paginator
from django.db.models import Count, Exists, OuterRef
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
# from django.utils.text import slugify
from PIL import Image
from pytils.translit import slugify

from .forms import CommentForm, GroupForm, PostForm
from .models import (Activity, Comment, Follow, FollowGroup, Group, Like, Post,
                     User)


def set_paginator(request, posts, pages):
    """Настройка паджинатора"""
    paginator = Paginator(posts, pages)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return paginator, page


def follow_count(user, author):
    following_count = Follow.objects.filter(user=author).count()
    foll_list = Follow.objects.filter(author=author)
    follows = foll_list.filter(user=user) if user.is_authenticated else None
    follower_count = foll_list.count()
    follower_group_count = FollowGroup.objects.filter(user=author).count()
    return {
        'follows': follows,
        'follower_count': follower_count,
        'following_count': following_count,
        'follower_group_count': follower_group_count
    }


def post_annotate(request, post_list):
    like_exist = (Like.objects.filter(
        post=OuterRef('pk'),
        user=request.user.is_authenticated and request.user
    ))
    return (post_list
            .annotate(num_likes=Count('liked', distinct=True))
            .annotate(is_liked=Exists(like_exist))
            .annotate(num_comments=Count('comments', distinct=True)))


def page_not_found(request, exception):
    return render(request, "misc/404.html",
                  {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


def index(request):
    """Возвращает 10 последних записей."""
    post_list = Post.objects.select_related('author', 'group').all()
    post_list = post_annotate(request, post_list)
    paginator, page = set_paginator(request, post_list, 10)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator} 
    )


def groups_overview(request):
    """Возвращает страницу со списком сообществ"""
    follow_exist = (FollowGroup.objects.filter(
        user=request.user.is_authenticated and request.user,
        group=OuterRef('pk')
    ))
    group_list = Group.objects.all().annotate(is_followed=Exists(follow_exist))
    return render(request, 'groups_overview.html', 
                  {'group_list': group_list})
 

def group_posts(request, slug):
    """Возвращает 10 последних постов по сообществу или ошибку 404."""
    user=request.user.is_authenticated and request.user
    group = get_object_or_404(Group, slug=slug)
    group.is_followed = (group.group_following
                         .filter(user=user).exists())
    post_list = group.posts.select_related('author').all()
    post_list = post_annotate(request, post_list)
    paginator, page = set_paginator(request, post_list, 10)
    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'paginator': paginator}
    )


def profile(request, username):
    """Возвращает профиль пользователя"""
    author = get_object_or_404(User, username=username)
    post_list = post_annotate(request, author.posts.all())
    paginator, page = set_paginator(request, post_list, 10)
    follow = follow_count(request.user, author)
    activity = Activity.objects.filter(user=author).first()
    last_seen = activity.time if activity else None
    return render(
        request,
        'profile.html',
        {'author': author, 'paginator': paginator,
         'page': page, 'follow': follow, 'last_seen': last_seen}
    )


def post_view(request, username, post_id):
    """Возвращает страницу просмотра конкретной записи"""
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    post.num_likes = Like.objects.filter(post=post_id).count()
    post.is_liked = (request.user.likes
                     .filter(post=post_id).exists())
    follow = follow_count(request.user, post.author)
    activity = Activity.objects.filter(user=post.author).first()
    last_seen = activity.time if activity else None
    comments = post.comments.all()
    post.num_comments = comments.count()
    form = CommentForm()
    return render(
        request,
        'post.html',
        {'post': post, 'form': form,
         'comments': comments, 'follow': follow,
         'last_seen': last_seen}
    )


@login_required
def new_post(request):
    """Возвращает страницу добавления записи / добавляет запись"""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save()
        post.author = request.user
        post.save()
        return redirect('/')
    return render(request, 'new.html', {'form': form})


@login_required
def new_group(request):
    """Возвращает страницу добавления зсообщества / добавляет сообщество"""
    form = GroupForm(request.POST or None)
    if form.is_valid():
        Group.objects.get_or_create(slug= slugify(form.cleaned_data['title']), **form.cleaned_data)
        return redirect(reverse('groups_overview'))
    return render(request, 'new_group.html', {'form': form})


@login_required
def post_edit(request, username, post_id):
    """Возвращает страницу редактирования записи / изменяет запись"""
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if request.user != post.author:
        return redirect(reverse('post', args=(username, post_id)))
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        post = form.save()
        post.save()
        return redirect(reverse('post', args=(username, post_id)))
    return render(request, 'new.html', {'form': form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    """Добавление комментария к записи"""
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(reverse('post', args=(username, post_id)))

@login_required
def del_comment(request, username, post_id, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.author:
        comment.delete()
    return redirect(reverse('post', args=(username, post_id)))


@login_required
def liked_posts(request):
    """Возвращает избранные записи"""
    likes = request.user.likes.select_related('post')
    post_list = Post.objects.filter(pk__in=likes.values('post')).select_related('author')
    post_list = post_annotate(request, post_list)
    paginator, page = set_paginator(request, post_list, 10)
    return render(request, "liked_posts.html",
                  {'page': page, 'paginator': paginator})


@login_required
def follow_index(request):
    """Возвращает записи избранных авторов"""
    follow_list = request.user.follower.all()
    post_list = (Post.objects.select_related('author', 'group')
                 .filter(author__following__in=follow_list))
    post_list = post_annotate(request, post_list)
    paginator, page = set_paginator(request, post_list, 10)
    return render(request, "follow.html",
                  {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    """Подписывает пользователя на автора"""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect(reverse('profile', args=(username,)))


@login_required
def profile_unfollow(request, username):
    """Отписывает пользователя от автора"""
    author = get_object_or_404(User, username=username)
    request.user.follower.filter(author=author).delete()
    return redirect(reverse('profile', args=(username,)))


@login_required
def post_like(request):
    """Создает лайки"""
    post = get_object_or_404(Post, pk=int(request.GET.get('post_id', False)))
    Like.objects.get_or_create(user=request.user, post=post or None)
    num_likes = request.GET['num_likes']
    num = int(num_likes or 0) + 1
    data = {
        'num_likes': num,
        'is_liked': 'True'
    }
    return JsonResponse(data)


@login_required
def post_remove_like(request):
    """Удаляет лайки"""
    post = get_object_or_404(Post, pk=int(request.GET.get('post_id', False)))
    get_object_or_404(Like, user=request.user, post=post).delete()
    num_likes = request.GET['num_likes']
    num = int(num_likes) - 1 or ''
    data = {
        'num_likes': num,
        'is_liked': 'False'
    }
    return JsonResponse(data)


@login_required
def follow_groups(request):
    """Возвращает записи избранных сообществ"""
    follow_list = request.user.group_follower.all()
    post_list = (Post.objects.select_related('group')
                 .filter(group__group_following__in=follow_list))
    post_list = post_annotate(request, post_list)
    paginator, page = set_paginator(request, post_list, 10)
    return render(request, 'follow_groups.html',
                  {'page': page, 'paginator': paginator})


@login_required
def group_follow(request, slug):
    """Подписывает пользователя на сообщество"""
    url = request.GET.get('overview', False)
    group = get_object_or_404(Group, slug=slug)
    FollowGroup.objects.get_or_create(user=request.user, group=group)
    return (redirect(reverse('groups_overview')) if url
            else redirect(reverse('group_posts', args=(slug,))))


@login_required
def group_unfollow(request, slug):
    """Отписывает пользователя от сообщества"""
    url = request.GET.get('overview', False)
    group = get_object_or_404(Group, slug=slug)
    request.user.group_follower.filter(group=group).delete()
    return (redirect(reverse('groups_overview')) if url
            else redirect(reverse('group_posts', args=(slug,))))

