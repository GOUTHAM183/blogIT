from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect
from .models import Post,Comment,Rating,Tag
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q 
from django.views.generic import (
    ListView,
    DeleteView,
    UpdateView,
    CreateView,
    DetailView,
)
from django.urls import reverse_lazy,reverse
from django.http import JsonResponse
from pymongo import MongoClient
from django.contrib import messages
from django.views.decorators.http import require_POST

client = MongoClient()
db = client['bloggit']
posts = db['blog_post_likes']

@login_required
def PostLike(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        if request.user in post.dislikes.all():
            post.dislikes.remove(request.user)
    return HttpResponseRedirect(reverse('post-detail', args=[str(pk)]))




@login_required
def PostDislike(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.user in post.dislikes.all():
        post.dislikes.remove(request.user)
    else:
        post.dislikes.add(request.user)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
    return HttpResponseRedirect(reverse('post-detail', args=[str(pk)]))




def home(request):
    context = {"posts": Post.objects.all()}
    return render(request, "blog/home.html", context)


class PostListView(ListView):
    model = Post
    template_name = "blog/home.html"
    context_object_name = "posts"
    ordering = ["-date_posted"]
    
    
@login_required
def tagged_posts(request, tag_name):
    posts = Post.objects.filter(tags__name=tag_name)
    context = {'posts': posts, 'tag_name': tag_name}
    return render(request, 'blog/tagged_posts.html', context)

def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        posts = Post.objects.filter(Q(title__icontains=searched) | Q(tags__name__icontains=searched)).distinct()
        return render(request,'blog/search.html',{'searched':searched,'posts':posts})
    else:
        return render(request,'blog/search.html',{})

class UserPostListView(ListView):
    model = Post
    template_name = "blog/user_posts.html"  # <app>/<model>_<viewtype>.html
    context_object_name = "posts"
    

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        return Post.objects.filter(author=user).order_by("-date_posted")


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['num_likes'] = post.likes.count()
        context['num_dislikes'] = post.dislikes.count()
        context['ratings'] = self.object.ratings.all()
        return context



class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        # Get the tags input from the form and split them by comma
        tags = self.request.POST['tags'].split(",")
        # Save the post instance to the database before adding tags
        response = super().form_valid(form)
        post = self.object  # Get the post instance
        
        # Loop through the tags and add them to the post's tags field
        for tag in tags:
            tag = tag.strip()
            tag_obj, created = Tag.objects.get_or_create(name=tag)
            post.tags.add(tag_obj)
        
        return response



class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        # Get the tags input from the form and split them by comma
        tags = self.request.POST['tags'].split(",")
        # Save the post instance to the database before adding tags
        response = super().form_valid(form)
        post = self.object  # Get the post instance
        # Clear existing tags before adding new ones
        post.tags.clear()
        # Loop through the tags and add them to the post's tags field
        for tag in tags:
            # Strip leading/trailing spaces from the tag
            tag = tag.strip()
            # Check if the tag already exists, if not create a new one
            tag_obj, created = Tag.objects.get_or_create(name=tag)
            # Add the tag to the post's tags field
            post.tags.add(tag_obj)
        return response
    
    def get_initial(self):
        # Get the tags of the current post as a comma-separated string
        tags = ', '.join(tag.name for tag in self.object.tags.all())
        # Set the initial value for the 'tags' field in the form
        return {'tags': tags}

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user





class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = "/"

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        else:
            return False


def about(request):
    return render(request, "blog/about.html", {"title": "About"})


class AddCommentView(CreateView):
    model = Comment
    template_name = 'blog/add_comment.html'
    fields = ["name","body"]
    

    
    def form_valid(self, form):
        form.instance.post_id = self.kwargs['pk']
        return super().form_valid(form)

        success_url = "/post/post_id"
    


@login_required
@require_POST
def rate_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        rating = int(request.POST['rating'])
        user = request.user
        
        try:
            # Check if the user has already rated this post
            user_rating = Rating.objects.get(user=user, post=post)
            user_rating.rating = rating
            user_rating.save()
            messages.success(request, 'Your rating has been updated successfully!')
        except Rating.DoesNotExist:
            # If the user has not rated the post before, create a new rating object
            user_rating = Rating(user=user, post=post, rating=rating)
            user_rating.save()
            messages.success(request, 'Thank you for rating this post!')

        post.update_rating()
        return redirect(reverse('post-detail', kwargs={'pk': post.pk}))
    
    else:
        # If the request is not POST, return a JsonResponse with the post's current rating
        context = {
            'rating_avg': post.rating_avg(),
            'rating_count': post.rating_count(),
        }
        return JsonResponse(context)
    
class TagListView(ListView):
    model = Tag
    template_name = 'blog/tag_list.html'  # Replace with your template name
    context_object_name = 'tags'
     # Set your desired number of tags per page

class TagDetailView(DetailView):
    model = Tag
    template_name = 'blog/tag_detail.html'  # Replace with your template name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(tags=self.object)
        return context