from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created = models.DateField()
    text = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('created', 'title')
