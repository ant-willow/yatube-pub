import json

from django import forms
from django.utils.text import slugify
from PIL import Image

from .models import Comment, Group, Post


def validate_slug(value):
    if (Group.objects.filter(slug=value).exists()):
        raise forms.ValidationError('Сообщество с таким названием уже есть!')


class PostForm(forms.ModelForm):
    """Форма добавления записи"""
    crop_data = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Post
        fields = ['image', 'text', 'group', 'crop_data']
        help_texts = {
            'group': 'Выберите сообщество',
            'text': 'Напишите что-нибудь',
            'image': 'Добавьте картинку',
        }

    def save(self):
        post = super().save(commit=False)
        json_data = self.cleaned_data.get('crop_data')
        if json_data:
            data = json.loads(json_data)
            img = self.cleaned_data['image']
            image = Image.open(img)
            x = data['x']
            y = data['y']
            w = data['width']
            h = data['height']
            cropped = image.crop((x, y, w+x, h+y))
            post.image.open()
            cropped.save(post.image)
        return post


class CommentForm(forms.ModelForm):
    """Форма добавления комментария"""
    class Meta:
        model = Comment
        fields = ['text']
        help_texts = {
            'text': 'Напишите что-нибудь'
        }


class GroupForm(forms.Form):
    """Форма добавления сообщества"""
    TITLE_MAX_LENGTH = 30
    DESCR_MAX_LENGTH = 100
    title = forms.CharField(
        max_length=TITLE_MAX_LENGTH,
        help_text=f'Название сообщества ({TITLE_MAX_LENGTH} символов)',
        validators=[validate_slug]
    )
    description = forms.CharField(
        max_length=DESCR_MAX_LENGTH ,
        widget=forms.Textarea(attrs={'rows': 5}),
        help_text=f'Описание сообщества ({DESCR_MAX_LENGTH } символов)'
    )
        # fields = ['title', 'description']
