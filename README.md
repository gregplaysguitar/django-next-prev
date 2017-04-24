Django utility to retrieve the next or previous object, given a current object
and a queryset.

See <http://gregbrown.co.nz/code/django-next-prev/> for more details.

[![Circle CI](https://circleci.com/gh/gregplaysguitar/django-next-prev.svg?style=svg)](https://circleci.com/gh/gregplaysguitar/django-next-prev)
[![codecov](https://codecov.io/gh/gregplaysguitar/django-next-prev/branch/master/graph/badge.svg)](https://codecov.io/gh/gregplaysguitar/django-next-prev)
[![Latest Version](https://img.shields.io/pypi/v/django-next-prev.svg?style=flat)](https://pypi.python.org/pypi/django-next-prev/)


## Installation

Download the source from https://pypi.python.org/pypi/django-next-prev/
and run `python setup.py install`, or:

    > pip install django-next-prev

Django 1.8 or higher is required.


## Quick start

Given this models.py:

```python
from django.db import models

class Category(models.Model):
    title = models.CharField(max_length=100)

class Post(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created = models.DateField()
    text = models.TextField()

    class Meta:
        ordering = ('created', 'title')
```   

You can do the following

```python
from next_prev import next_in_order, prev_in_order
from .models import Post

# default ordering
first = Post.objects.first()
second = next_in_order(first)
last = prev_in_order(first, loop=True)

# custom ordering
qs = Post.objects.all().order_by('-created')
newest = qs.first()
second_newest = next_in_order(newest, qs=qs)
oldest = prev_in_order(newest, qs=qs, loop=True)
```
