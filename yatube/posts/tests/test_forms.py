from django.contrib.auth import get_user_model

from django.test import Client, TestCase

from django.urls import reverse

from posts.forms import PostCreateForm

from ..models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст"
        )
        cls.group = Group.objects.create(
            title="Тестовая группа"
        )
        cls.form = PostCreateForm()

        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
            "group": "Тестовая группа",
        }
        response = self.authorized_client.post(
            reverse("posts:post_create", args={"slug": "test-slug"}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse("posts:index"))
        self.assertEqual(Post.objects.count, posts_count + 1)

    def test_post_edit(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
            "group": "Тестовая группа",
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse("posts:post_detail",
                                               args=[self.post.id]))
        self.assertEqual(Post.objects.count, posts_count)
