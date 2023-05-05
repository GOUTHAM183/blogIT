from django.contrib import admin
from .models import Post,Rating,Comment,Tag

# Register your models here.
admin.site.register(Post)
admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(Tag)

