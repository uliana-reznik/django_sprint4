from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Category, Post, Comment
from .forms import PostForm, CommentForm, UserProfileForm

User = get_user_model()


def index(request):
    post_list = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = Post.objects.filter(
        category=category,
        pub_date__lte=timezone.now(),
        is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    # Если пост не опубликован или категория не опубликована,
    # показываем только автору
    if post.author != request.user:
        post = get_object_or_404(
            Post,
            pk=post_id,
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )

    comments = post.comments.select_related('author')
    form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/detail.html', context)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        posts = Post.objects.filter(
            author=profile_user
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    else:
        posts = Post.objects.filter(
            author=profile_user,
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile_user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)

    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    context = {'post': post}
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    context = {
        'form': form,
        'comment': comment,
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)


@login_required
def edit_profile(request):
    form = UserProfileForm(request.POST or None, instance=request.user)

    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)

    context = {'form': form}
    return render(request, 'blog/user.html', context)


def registration(request):
    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('blog:index')

    context = {'form': form}
    return render(request, 'registration/registration_form.html', context)
