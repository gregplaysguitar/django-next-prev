from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Post(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created = models.DateField()
    text = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('created', 'title')
