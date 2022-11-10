from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f'{self.name}'


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    text = RichTextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title}'

    def get_reply_post(self):
        replys = []
        reply = Reply.objects.filter(post_id=self)
        for r in reply:
            replys.append(r.text)
        return replys


class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    accept = models.BooleanField()

    def get_post_reply(self):
        posts = []
        post = Post.objects.filter(pk=self.post_id)
        for p in post:
            posts.append(p.title)
        return posts

    def get_category(self):
        category = Post.objects.get(pk=self.post_id)
        return category.category


class OneTimeCode(models.Model):
    user = models.CharField(max_length=256)
    code = models.CharField(max_length=10)

