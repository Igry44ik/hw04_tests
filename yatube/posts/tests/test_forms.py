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
        last_post = Post.objects.latest("id")
        self.assertEqual(last_post.text, self.post.text)
        self.assertEqual(last_post.group.id, form_data["group"])

    def test_post_edit(self):
        form_data = {
            "text": "Новый пост",
            "group": self.group.pk,
        }
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True
        )
        post_response = response.context["post"]
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post_response.text, form_data["text"])
        self.assertEqual(post_response.author, self.user)
        self.assertEqual(post_response.group.pk, form_data["group"])
        self.assertRedirects(response,
                             reverse("posts:post_detail",
                                     kwargs={"post_id": self.post.pk}))

    def test_anonymous_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
            "group": self.group.id,
        }
        response = self.client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, (reverse("users:login") + "?next="
                                        + reverse("posts:post_create")))

    def test_anonymous_edit_post(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
            "group": self.group.id,
        }
        response = self.client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, (reverse("users:login")) + "?next="
                             + (reverse("posts:post_edit",
                                        kwargs={"post_id": self.post.pk})))
        self.assertEqual(
            Post.objects.filter(
                text=form_data["text"],
                author=self.user,
                group=self.group
            ).exists()
        )
