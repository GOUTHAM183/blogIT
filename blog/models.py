from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = RichTextField(blank=True,null=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='post_like')
    dislikes = models.ManyToManyField(User, related_name='post_dislike')
    rating = models.FloatField(default=0)
    tags = models.ManyToManyField(Tag, related_name='post_tags', auto_created=False)
    is_blocked = models.BooleanField(default=False)

    

    def update_rating(self):
            ratings = Rating.objects.filter(post=self)
            if ratings:
                total_ratings = sum([rating.rating for rating in ratings])
                avg_rating = total_ratings / len(ratings)
                self.rating = avg_rating
                self.save()
    

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.pk})
    
class Rating(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    

    class Meta:
        unique_together = ('post', 'user')



class Comment(models.Model):
    post = models.ForeignKey(Post,related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' %(self.post.title,self.name)

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"pk": self.post_id})