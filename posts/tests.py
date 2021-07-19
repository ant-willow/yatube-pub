from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from PIL import Image

from .models import Comment, Follow, Group, Post, User


class Test(TestCase):
    def setUp(self):
        """Предварительная настройка"""
        self.client = Client()
        self.guest = Client()
        self.text = 'initial text'
        self.user = User.objects.create_user(
            username='test_user',
            email='mail@test.ru',
            password='qwerty'
        )
        self.client.force_login(self.user)
        self.group = Group.objects.create(
            title='group',
            slug='group',
            description='test group description'
        )

    @override_settings(CACHES={
        'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}
    })
    def check_context(self, author, post_id, text, group, image=False):
        for url in (
                reverse('index'),
                reverse('group_posts', args=(group.slug,)),
                reverse('profile', args=(author,)),
                reverse('post', args=(author, post_id))
        ):
            response = self.client.get(url)
            self.assertEqual(author, response.context['post'].author)
            self.assertEqual(text, response.context['post'].text)
            self.assertEqual(group, response.context['post'].group)
            if image:
                self.assertIn('img', str(response.content))

    def test_profile(self):
        """Тест на существование страницы пользователя"""
        response = self.client.get(
            reverse('profile', args=(self.user.username,))
        )
        self.assertEqual(response.status_code, 200)

    def test_new(self):
        """Тест на возможность создания поста"""
        response = self.client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new.html')

    def test_create_post(self):
        """Тест на корректность создания поста"""
        data = {'group': self.group.id, 'text': self.text}
        self.client.post(reverse('new_post'), data, follow=True)
        self.assertEqual(Post.objects.count(), 1)
        post = self.user.posts.get(pk=1)
        self.check_context(self.user, post.id, self.text, self.group)

    def test_post_edit(self):
        """Тест на корректность изменения поста и сообщества"""
        new_text = 'edited text'
        post = Post.objects.create(
            author=self.user,
            group=self.group,
            text=self.text
        )
        new_group = Group.objects.create(
            title='new_group',
            slug='new_group',
            description='new group description'
        )
        data = {'group': new_group.id, 'text': new_text}
        self.client.post(
            reverse('post_edit', args=(self.user.username, post.id)),
            data
        )
        self.check_context(
            self.user, post.id, new_text, new_group
        )

    def test_create_post_guest(self):
        """Тест создания поста гостем"""
        response = self.guest.post(
            reverse('new_post'), {'text': 'test'}, follow=True
        )
        self.assertEqual(Post.objects.count(), 0)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_image_upload(self):
        """Тест добавления изображения в пост"""
        img = Image.new('RGB', (100, 100), color='cyan')
        uploaded = SimpleUploadedFile(
            name='small.jpg',
            content=img.tobytes('jpeg', 'RGB'),
            content_type='image/jpeg'
        )
        data = {'group': self.group.id, 'text': self.text, 'image': uploaded}
        self.client.post(reverse('new_post'), data, follow=True)
        self.assertEqual(Post.objects.count(), 1)
        post = self.user.posts.get(pk=1)
        self.check_context(
            self.user, post.id, self.text, self.group, image=True
        )

    def test_not_image_upload(self):
        """Тест загрузки неправильного формата"""
        txt = SimpleUploadedFile(
            name='small.txt',
            content=b'text',
            content_type='text/plain'
        )
        data = {'text': 'post_text', 'image': txt}
        response = self.client.post(
            reverse('new_post'), data, follow=True
        )
        error_text = ('Загрузите правильное изображение. '
                      'Файл, который вы загрузили, '
                      'поврежден или не является изображением.')
        self.assertFormError(response, 'form', 'image', error_text)

    def test_cache(self):
        """Тест работы кеша"""
        post = Post.objects.create(
            author=self.user,
            group=self.group,
            text=self.text
        )
        response = self.client.get(reverse('index'))
        key = make_template_fragment_key('index_page',
                                         [response.context['page']])
        self.assertIn(post.text, cache.get(key))
        response = self.client.get(reverse('index'))
        self.assertNotIn('post', response.context)
        self.assertTemplateNotUsed(response, 'includes/post_item.html')

    def test_404(self):
        """Тест несуществующей страницы"""
        response = self.client.get('/404/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'misc/404.html')


class TestComment(TestCase):
    """Тестирование комментариев"""
    def setUp(self):
        self.text = 'comment_text'
        self.client = Client()
        self.guest = Client()
        self.user = User.objects.create_user(
            username='test_user',
            password='qwerty'
        )
        self.post = Post.objects.create(
            author=self.user,
            text='post_text'
        )
        self.client.force_login(self.user)

    def test_add_comment(self):
        """Тест добавления комментария"""
        response = self.client.post(
            reverse('add_comment', args=(self.user.username, self.post.id)),
            {'text': self.text},
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(self.text,
                         response.context['comments'].first().text)

    def test_add_comment_guest(self):
        """Тест добавления комментария гостем"""
        response = self.guest.post(
            reverse('add_comment', args=(self.user.username, self.post.id)),
            {'text': self.text},
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 0)
        self.assertTemplateUsed(response, 'registration/login.html')


class TestFollow(TestCase):
    """Тестирование системы подписки"""
    def setUp(self):
        """Предварительная настройка"""
        self.text = 'post_text'
        self.client = Client()
        self.guest = Client()
        self.follower = User.objects.create_user(
            username='test_user_1',
            password='123'
        )
        self.following = User.objects.create_user(
            username='test_user_2',
            password='123'
        )
        self.client.force_login(self.follower)

    def test_follow(self):
        """Тест подписки"""
        self.client.get(
            reverse('profile_follow', args=(self.following.username,))
        )
        follow = Follow.objects.all()
        self.assertEqual(follow.count(), 1)
        self.assertEqual(self.follower, follow.first().user)
        self.assertEqual(self.following, follow.first().author)

    def test_unfollow(self):
        """Тест отписки"""
        Follow.objects.create(user=self.follower, author=self.following)
        self.client.get(
            reverse('profile_unfollow', args=(self.following.username,))
        )
        follow_count = Follow.objects.all().count()
        self.assertEqual(follow_count, 0)

    def test_follow_guest(self):
        """Тест подписки гостем"""
        self.guest.get(
            reverse('profile_follow', args=(self.following.username,))
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_new_post_follower(self):
        """Тест отображения нового поста в подписках"""
        post = Post.objects.create(
            author=self.following,
            text=self.text
        )
        Follow.objects.create(user=self.follower, author=self.following)
        response = self.client.get(reverse('follow_index'))
        self.assertIn('post', response.context)
        self.assertEqual(response.context['post'].text, post.text)

    def test_new_post_not_follower(self):
        """Тест отображения для не подписчика"""
        Post.objects.create(
            author=self.following,
            text=self.text
        )
        user = User.objects.create_user(
            username='test_user_3',
            password='123'
        )
        self.client.logout()
        self.client.force_login(user)
        response = self.client.get(reverse('follow_index'))
        self.assertNotIn('post', response.context)
