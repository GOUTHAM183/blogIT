from django.urls import path
from admin_panel.views import view_posts,block_user,unblock_user,custom_admin_panel,block_post,unblock_post,restrict_posts

urlpatterns = [
    path('custom_admin_panel/', custom_admin_panel, name='custom_admin_panel'),
    path('view_posts/', view_posts, name='view_posts'),
    path('restrict_posts/', restrict_posts, name='restrict_posts'),
    path('block_user/<int:user_id>/', block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', unblock_user, name='unblock_user'),
    path('block_post/<int:post_id>/', block_post, name='block_post'),
    path('unblock_post/<int:post_id>/', unblock_post, name='unblock_post'),
]
    

