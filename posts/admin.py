from django.contrib import admin

from .models import Comment, Group, Like, Post


class PostAdmin(admin.ModelAdmin):
    """Управление постами в админке"""
    list_display = ('pk', 'text', 'image', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Управление сообществами в админке"""
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('pk', 'title', 'slug', 'description')


class CommentAdmin(admin.ModelAdmin):
    """Управление комментариями в админке"""
    list_display = ('pk', 'text', 'created', 'author', 'post')
    search_fields = ('text',)


class LikeAdmin(admin.ModelAdmin):
    """Управление лайками в админке"""
    list_display = ('pk', 'user', 'post')


admin.site.register(Like, LikeAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
