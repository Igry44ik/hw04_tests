from django.contrib.auth import get_user_model

from django.test import Client, TestCase

from django.urls import reverse

from posts.forms import PostForm

from ..models import Group, Post

User = get_user_model()

USERNAME = "Test-User"


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug="test-slug",
            description="Тестовое описание"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text="Тестовый текст"
        )
        cls.form = PostForm()

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                                               args=[USERNAME]))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit(self):
        test_post = Post.objects.create(
            text="Тестовый текст",
            author=self.user,
        )
        form_data = {
            "text": "Новый пост",
            "group": self.group.pk,
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": test_post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response,
                             reverse("posts:post_detail",
                                     kwargs={"post_id": test_post.pk}))
        self.assertTrue(Post.objects.filter(
            text='Новый пост',
            group__slug="test-slug").exists())
