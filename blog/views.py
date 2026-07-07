from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Post, Comment, Profile, Notification
from .forms import RegisterForm, PostForm, CommentForm, ProfileForm


# ─── Helper: Create Notification ─────────────────────────────────────────────
def create_notification(recipient, sender, notif_type, post=None):
    """Create a notification only if sender != recipient."""
    if recipient != sender:
        Notification.objects.get_or_create(
            recipient=recipient,
            sender=sender,
            notif_type=notif_type,
            post=post,
            is_read=False,
        )


# ─── Home ─────────────────────────────────────────────────────────────────────
def home(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 9)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, 'blog/home.html', {'posts': posts})


# ─── Feed ─────────────────────────────────────────────────────────────────────
@login_required
def feed_view(request):
    following_users = request.user.following.all()
    post_list = Post.objects.filter(author__in=following_users)
    paginator = Paginator(post_list, 9)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, 'blog/feed.html', {'posts': posts})


# ─── Post Detail ─────────────────────────────────────────────────────────────
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    comment_form = CommentForm()
    is_liked = False

    if request.user.is_authenticated:
        is_liked = post.likes.filter(id=request.user.id).exists()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            # Notification: someone commented on your post
            create_notification(post.author, request.user, 'comment', post)
            messages.success(request, 'Comment added successfully!')
            return redirect('post_detail', pk=pk)

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
        'total_likes': post.total_likes(),
    }
    return render(request, 'blog/post_detail.html', context)


# ─── Post Create ─────────────────────────────────────────────────────────────
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Create New Post'})


# ─── Post Edit ───────────────────────────────────────────────────────────────
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, 'You can only edit your own posts!')
        return redirect('home')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', pk=pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Edit Post'})


# ─── Post Delete ─────────────────────────────────────────────────────────────
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, 'You can only delete your own posts!')
        return redirect('home')
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('home')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


# ─── Like Post ───────────────────────────────────────────────────────────────
@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        # Notification: someone liked your post
        create_notification(post.author, request.user, 'like', post)
    return JsonResponse({'liked': liked, 'total_likes': post.total_likes()})


# ─── Comment Delete ───────────────────────────────────────────────────────────
@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    if comment.author != request.user:
        messages.error(request, 'You can only delete your own comments!')
        return redirect('post_detail', pk=post_pk)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
    return redirect('post_detail', pk=post_pk)


# ─── Register ────────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Account created successfully.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'blog/register.html', {'form': form})


# ─── Login ───────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'blog/login.html', {'form': form})


# ─── Logout ──────────────────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')


# ─── Profile ─────────────────────────────────────────────────────────────────
def profile_view(request, username):
    target_user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=target_user)
    posts = Post.objects.filter(author=target_user)

    is_following = False
    if request.user.is_authenticated:
        is_following = profile.followers.filter(id=request.user.id).exists()

    if request.method == 'POST':
        if not request.user.is_authenticated or request.user != target_user:
            messages.error(request, 'You are not authorized to edit this profile.')
            return redirect('profile_view', username=username)
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_view', username=username)
    else:
        form = ProfileForm(instance=profile)

    context = {
        'profile_user': target_user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'followers_count': profile.followers.count(),
        'following_count': target_user.following.count(),
        'form': form,
    }
    return render(request, 'blog/profile.html', context)


# ─── Toggle Follow ───────────────────────────────────────────────────────────
@login_required
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({'error': 'You cannot follow yourself'}, status=400)

    profile, created = Profile.objects.get_or_create(user=target_user)
    if profile.followers.filter(id=request.user.id).exists():
        profile.followers.remove(request.user)
        followed = False
    else:
        profile.followers.add(request.user)
        followed = True
        # Notification: someone followed you
        create_notification(target_user, request.user, 'follow')

    return JsonResponse({
        'followed': followed,
        'followers_count': profile.followers.count(),
        'following_count': request.user.following.count(),
    })


# ─── Notifications ────────────────────────────────────────────────────────────
@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(recipient=request.user)
    # Mark all as read when page is opened
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'blog/notifications.html', {'notifications': notifs})


@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})
