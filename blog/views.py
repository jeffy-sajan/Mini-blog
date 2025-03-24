from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Post, Comment, SavedPost, Profile
from django import forms
from .forms import CommentForm, ProfileForm
from django.db.models import Count, Max
from django.http import JsonResponse, HttpResponse
import logging
import json
from django.views.decorators.http import require_http_methods

# Create a logger
logger = logging.getLogger(__name__)

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

def index(request):
    latest_posts = Post.objects.exclude(author__username='admin').order_by('-date_posted')[:3]
    return render(request, 'blog/index.html', {'latest_posts': latest_posts})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create or get the profile for the new user
            Profile.objects.get_or_create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('blog:login')
    else:
        form = UserCreationForm()
    return render(request, 'blog/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out!')
    return redirect('blog:home')

def blog_home(request):
    post_list = Post.objects.exclude(author__username='admin').order_by('-date_posted')
    paginator = Paginator(post_list, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/blog_home.html', {'posts': posts, 'page_obj': posts})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    saved = SavedPost.objects.filter(user=request.user, post=post).exists()
    comments = post.comments.all()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('blog:post-detail', pk=post.pk)
    else:
        form = CommentForm()
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'saved': saved
    })

@login_required(login_url=reverse_lazy('blog:login'))
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Your post has been created!')
            return redirect('blog:post-detail', pk=post.pk)
        else:
            messages.error(request, 'Invalid form data')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

@login_required(login_url=reverse_lazy('blog:login'))
def post_update(request, pk):
    try:
        post = get_object_or_404(Post, pk=pk)
    except Post.DoesNotExist:
        return HttpResponse("Post does not exist", status=404)
    
    if post.author != request.user:
        messages.error(request, 'You are not authorized to update this post.')
        return redirect('blog:post-detail', pk=pk)
        
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Your post has been updated!')
                return redirect('blog:post-detail', pk=pk)
            except Exception as e:
                logger.error(f"Error in post_update: {str(e)}")
                messages.error(request, 'Failed to update post')
        else:
            messages.error(request, 'Invalid form data')
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form})

@login_required(login_url=reverse_lazy('blog:login'))
def post_delete(request, pk):
    try:
        post = get_object_or_404(Post, pk=pk)
    except Post.DoesNotExist:
        return HttpResponse("Post does not exist", status=404)
    
    if post.author != request.user:
        messages.error(request, 'You are not authorized to delete this post.')
        return redirect('blog:post-detail', pk=pk)
        
    if request.method == 'POST':
        try:
            post.delete()
            messages.success(request, 'Your post has been deleted!')
            return redirect('blog:blog-home')
        except Exception as e:
            logger.error(f"Error in post_delete: {str(e)}")
            messages.error(request, 'Failed to delete post')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

@login_required(login_url=reverse_lazy('blog:login'))
def add_comment(request, post_pk):
    try:
        post = get_object_or_404(Post, pk=post_pk)
    except Post.DoesNotExist:
        return HttpResponse("Post does not exist", status=404)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            try:
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                messages.success(request, 'Your comment has been added!')
                return redirect('blog:post-detail', pk=post.pk)
            except Exception as e:
                logger.error(f"Error in add_comment: {str(e)}")
                messages.error(request, 'Failed to add comment')
        else:
            messages.error(request, 'Invalid form data')
    else:
        form = CommentForm()
    
    return render(request, 'blog/add_comment.html', {'form': form, 'post': post})

@login_required
def save_post(request, post_pk):
    if request.method == 'POST':
        try:
            post = get_object_or_404(Post, id=post_pk)
        except Post.DoesNotExist:
            return HttpResponse("Post does not exist", status=404)
        
        # Check if post is already saved by this user
        saved_post = SavedPost.objects.filter(user=request.user, post=post).first()
        
        if saved_post:
            # Post is already saved, remove it
            saved_post.delete()
            saved = False
        else:
            # Post is not saved, save it
            SavedPost.objects.create(user=request.user, post=post)
            saved = True
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'saved': saved})
        else:
            return redirect('blog:post-detail', pk=post_pk)

    return redirect('blog:post-detail', pk=post_pk)

@login_required
def saved_posts(request):
    saved_posts = SavedPost.objects.filter(user=request.user).order_by('-date_saved')
    return render(request, 'blog/saved_posts.html', {'saved_posts': saved_posts})

@login_required
@require_http_methods(["GET"])
def blogger_detail(request, pk):
    try:
        blogger = User.objects.get(pk=pk)
        posts = Post.objects.filter(author=blogger).order_by('-date_posted')
        saved_posts = SavedPost.objects.filter(user=request.user).select_related('post') if request.user.is_authenticated else None
        
        context = {
            'blogger': blogger,
            'posts': posts,
            'saved_posts': saved_posts
        }
        
        return render(request, 'blog/blogger_detail.html', context)
    except User.DoesNotExist:
        raise Http404("Blogger does not exist")

@login_required
@require_http_methods(["GET"])
def blogger_list(request):
    # Get all users who are not admin and have a profile
    bloggers = User.objects.filter(
        is_superuser=False,
        profile__isnull=False
    ).annotate(
        posts_count=Count('post'),
        latest_post=Max('post__date_posted')
    ).order_by('-latest_post').distinct()
    
    return render(request, 'blog/blogger_list.html', {
        'bloggers': bloggers
    })

@login_required
@require_http_methods(["GET", "POST"])
def profile_update(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('blog:blogger-detail', pk=request.user.pk)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'blog/profile_update.html', {
        'form': form,
        'profile': profile
    })
