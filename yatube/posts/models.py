from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField("Описание")

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField("Текст поста", help_text="Введите текст поста")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="posts", verbose_name="Автор")
    group = models.ForeignKey(Group, on_delete=models.CASCADE,
                              related_name="posts", verbose_name="Группа",
                              blank=True, null=True,
                              help_text="Выберите группу")

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self) -> str:
        return self.text
