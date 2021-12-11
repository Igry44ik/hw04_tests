from django.contrib.auth import get_user_model

from django.test import TestCase, Client

from django.urls import reverse

from posts.models import Post, Group


User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        response = self.guest_client.get("/about/author/")
        self.assertEqual(response.status_code, 200)

    def test_tech(self):
        response = self.guest_client.get("/about/tech/")
        self.assertEqual(response.status_code, 200)


USERNAME = "Test"
TESTSLUG = "Test-slug"


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title="Тестовый заголовок",
            slug="test-slug",
            description="Тестовый текст"
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.user,
            group=cls.group
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desired_location_authorized(self):
        """Страница /group/<slug>/ доступна любому пользователю."""
        response = self.guest_client.get("/group/test-slug/")
        self.assertEqual(response.status_code, 200)

    def test_username_url_exists_at_desired_location(self):
        """Страница /posts/profile/ доступна любому пользователю."""
        response = self.guest_client.get(reverse("posts:profile",
                                                 args=[USERNAME]))
        self.assertEqual(response.status_code, 200)

    def test_post_id_url_exists_at_desired_location(self):
        """Страница /posts/post_detail/ доступна любому пользователю."""
        response = self.guest_client.get(reverse("posts:post_detail",
                                                 args=[self.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location_authorized(self):
        """Страница /posts/<post_id>/edit/ доступна только автору поста"""
        response = self.authorized_client.get(reverse("posts:post_edit",
                                                      args=[self.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_post_create_url_exists_at_desired_location_authorized(self):
        """Страница /posts/create/ доступна только авторизированному
        пользователю
        """
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        """Несуществующая страница"""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            "posts/index.html": "/",
            "posts/create_post.html": "/create/",
            "posts/group_list.html": "/group/test-slug/",
            "posts/profile.html": reverse("posts:profile", args=[USERNAME]),
            "posts/post_detail.html": reverse("posts:post_detail",
                                              args=[self.post.id]),
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_post_edit_correct_template(self):
        response = self.authorized_client.get(reverse("posts:post_edit",
                                              args=[self.post.id]))
        self.assertTemplateUsed(response, "posts/create_post.html")
