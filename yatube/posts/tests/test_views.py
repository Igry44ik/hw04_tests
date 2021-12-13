from django import forms

from django.conf import settings

from django.contrib.auth import get_user_model

from django.test import Client, TestCase

from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()

USERNAME = "Test"


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title="test-group",
            slug="test-slug",
        )
        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=cls.user,
            group=cls.group
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def tets_pages_uses_correct_template(self):
        template_pages_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse("posts:slug",
                                             args={"slug": self.group.slug}),
            "posts/profile.html": reverse("posts:profile"),
            "posts/post_detail.html": reverse("posts:post_detail",
                                              args=[self.post.id]),
            "posts/create_post.html": reverse("posts:post_create"),
        }
        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_correct_context(self):
        templates_pages_names = {
            reverse("posts:index"),
            reverse("posts:slug", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.user.username}),
        }
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context.get("page_obj")[0]
                post_author_0 = first_object.author
                post_id_0 = first_object.id
                post_text_0 = first_object.text
                post_group_0 = first_object.group.slug
                self.assertEqual(post_text_0, self.post.text)
                self.assertEqual(post_id_0, self.post.id)
                self.assertEqual(post_author_0, self.post.author)
                self.assertEqual(post_group_0, self.group.slug)

    def test_post_detail_correct_context(self):
        response = self.authorized_client.get(reverse("posts:post_detail",
                                                      args=[self.post.id]))
        first_object = response.context.get("post")
        post_author_0 = first_object.author
        post_id_0 = first_object.id
        post_text_0 = first_object.text
        post_group_0 = first_object.group.slug
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_id_0, self.post.id)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.group.slug)

    def test_post_edit_correct_context(self):
        response = self.authorized_client.get(reverse("posts:post_edit",
                                                      args=[self.post.id]))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_post_correct_context(self):
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_in_main_page(self):
        """Новый пост отображается на главной странице
            и на странице группы.
        """
        url = ((reverse("posts:index")),
               reverse("posts:slug", kwargs={"slug": self.group.slug}),)
        for urls in url:
            with self.subTest(url=url):
                response = self.authorized_client.get(urls)
                self.assertEqual(len(response.context["page_obj"]), 1)

    def test_post_in_profile_page(self):
        url = reverse("posts:profile", args=[USERNAME])
        response = self.authorized_client.get(url)
        self.assertEqual(response.context.get("author"), self.user)

    def test_post_not_in_your_group(self):
        """Новый пост попал не в свою группу."""
        url = reverse("posts:slug", kwargs={"slug": self.group.slug},)
        response = self.authorized_client.get(url)
        self.assertNotEqual(response.context.get("page_obj"), self.post)

    def test_paginator(self):
        for post in range(settings.QUANTITY_POSTS):
            Post.objects.create(
                text="Тестовый текст",
                author=self.user,
                group=self.group
            )
        url = reverse("posts:index"),
        reverse("posts:slug", kwargs={"slug": self.group.slug}),
        reverse("posts:profile", args=[USERNAME])
        for urls in url:
            with self.subTest(urls=urls):
                response = self.authorized_client.get(urls)
                self.assertEqual(len(response.context["page_obj"]),
                                 settings.QUANTITY_POSTS)
