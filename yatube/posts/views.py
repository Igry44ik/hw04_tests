from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.QUANTITY_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    paginator = Paginator(posts_list, settings.QUANTITY_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    profile_list = author.posts.all()
    paginator = Paginator(profile_list, settings.QUANTITY_POSTS)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "author": author,
        "page_obj": page_obj,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        "post": post,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    """Функция создания нового поста"""
    form = PostForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect("posts:profile", username=request.user)
    return render(request, "posts/create_post.html", {"form": form, })


@login_required
def post_edit(request, post_id):
    """Функция редактирования поста"""
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=post.id)

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id=post.id)
    else:
        return render(request, "posts/create_post.html",
                      {"form": form, "post": post, "is_edit": is_edit, })
