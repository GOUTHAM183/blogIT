from django.urls import path
from .views import (
    PostListView,
    PostDeleteView,
    PostDetailView,
    PostUpdateView,
    PostCreateView,
    UserPostListView,
    AddCommentView,
)
from . import views


urlpatterns = [
    path("", PostListView.as_view(), name="home"),
    path("user/<str:username>", UserPostListView.as_view(), name="user-posts"),
    path("post/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("post/<int:pk>/update/", PostUpdateView.as_view(), name="post-update"),
    path("post/<int:pk>/delete/", PostDeleteView.as_view(), name="post-delete"),
    path("post/new/", PostCreateView.as_view(), name="post-create"),
    path("about/", views.about, name="about"),
    path("post/<int:pk>/comment/",AddCommentView.as_view(),name='add_comment'),
    path('post/<int:pk>/like/', views.PostLike, name='post-like'),
    path("search/", views.search, name="search"),
    path('post/<int:pk>/dislike/', views.PostDislike, name='post-dislike'),
    path('rate_post/<int:pk>/', views.rate_post, name='rate-post'),
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    # URL for the tag detail view
    path('tag/<str:tag_name>/', views.tagged_posts, name='tagged_posts'),
    path('tags/<int:pk>/', views.TagDetailView.as_view(), name='tag-detail'),
]

