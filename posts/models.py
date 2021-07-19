from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

      
class Group(models.Model):
    """Модель Group."""
    
    title = models.CharField(
        max_length=100,
        verbose_name='Название сообщества'
    )
    slug = models.SlugField(unique=True)
    description = models.TextField(
        verbose_name='Описание сообщества'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель Пост"""
    text = models.TextField(verbose_name='Текст записи')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Сообщество',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='posts/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.text

    class Meta:
        """Meta опции"""
        ordering = ['-pub_date']


class Comment(models.Model):
    """Модель Комментарий"""
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария'
    )

    def __str__(self):
        return self.text

    class Meta:
        """Meta опции"""
        ordering = ['-created']


class Follow(models.Model):
    """Модель Подписка"""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ['user', 'author']


class FollowGroup(models.Model):
    """Модель Подписка Сообщество"""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='group_follower',
        on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Сообщество',
        related_name='group_following',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ['user', 'group']


class Like(models.Model):
    """Модель Лайк"""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='likes',
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        related_name='liked',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ['user', 'post']


class Activity(models.Model):
    """Модель Активность"""
    user = models.OneToOneField(
        User,
        verbose_name='Пользователь',
        related_name='seen',
        unique=True,
        on_delete=models.CASCADE
    )
    time = models.DateTimeField(
        verbose_name='Дата посещения',
        blank=True,
        null=True
    )
