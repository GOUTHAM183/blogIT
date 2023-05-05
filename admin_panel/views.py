from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from blog.models import Post
from django.contrib.auth.decorators import user_passes_test

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect

from django.contrib.admin.views.decorators import staff_member_required

User = get_user_model()

@login_required
def view_posts(request):
    posts = Post.objects.all()
    return render(request, 'admin_panel/view_posts.html', {'posts': posts})

def custom_admin_panel(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    users = User.objects.all().exclude(id=request.user.id)
    

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')

        user = User.objects.get(id=user_id)

        if action == 'block':
            user.is_active = False
            user.save()
        elif action == 'unblock':
            user.is_active = True
            user.save()

        return redirect('/custom_admin_panel/')

    context = {'users': users}
    return render(request, 'admin_panel/custom_admin_panel.html', context)

def restrict_posts(request):
    if not request.user.is_superuser:
        return redirect('home')

    posts = Post.objects.all()

    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        action = request.POST.get('action')

        post = Post.objects.get(id=post_id)

        if action == 'block':
            post.is_blocked = True
            post.save()
        elif action == 'unblock':
            post.is_blocked = False
            post.save()

        return redirect('restrict_posts')

    context = {'posts': posts}
    return render(request, 'admin_panel/restrict_posts.html', context)




def block_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = False
    user.save()
    return redirect('custom_admin_panel')

def unblock_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return redirect('custom_admin_panel')

@login_required
@staff_member_required
def block_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.is_blocked = True
    post.save()
    return redirect('restrict_posts')

@login_required
@staff_member_required
def unblock_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.is_blocked = False
    post.save()
    return redirect('restrict_posts')