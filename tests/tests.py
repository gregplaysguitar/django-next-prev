from datetime import date

from django.test import TestCase

from .models import Post, Category

from next_prev import next_in_order, prev_in_order


class NextPrevTestCase(TestCase):
    def setUp(self):
        # add some content
        self.first_category = Category.objects.create(title='Category 1')
        self.second_category = Category.objects.create(title='Category 2')

        self.post1 = Post.objects.create(
            title='Post 1', text='Beautiful is better than ugly.',
            category=self.first_category, created=date(2015, 1, 1),
            author='Steve')
        self.post2 = Post.objects.create(
            title='Post 2', text='Simple is better than complex.',
            category=self.second_category, created=date(2015, 1, 1))
        self.post3 = Post.objects.create(
            title='Post 3',
            text='Complex is better than complicated.',
            category=self.first_category, created=date(2016, 1, 1),
            author='Mary')

    def test_default(self):
        qs = Post.objects.all()
        first = qs.first()
        self.assertEqual(first, self.post1)

        second = next_in_order(first)
        self.assertEqual(second, self.post2)

        third = next_in_order(second)
        self.assertEqual(third, self.post3)

        fourth = next_in_order(third)
        self.assertEqual(fourth, None)

        fourth_loop = next_in_order(third, loop=True)
        self.assertEqual(fourth_loop, self.post1)

        prev = prev_in_order(first)
        self.assertEqual(prev, None)

        prev_loop = prev_in_order(first, loop=True)
        self.assertEqual(prev_loop, self.post3)

    def test_custom(self):
        qs = Post.objects.all().order_by('category__title', '-created')
        first = qs.first()
        self.assertEqual(first, self.post3)

        second = next_in_order(first, qs)
        self.assertEqual(second, self.post1)

        third = next_in_order(second, qs)
        self.assertEqual(third, self.post2)

        fourth = next_in_order(third, qs)
        self.assertEqual(fourth, None)

        fourth_loop = next_in_order(third, qs, loop=True)
        self.assertEqual(fourth_loop, self.post3)

        prev = prev_in_order(first, qs)
        self.assertEqual(prev, None)

        prev_loop = prev_in_order(first, qs, loop=True)
        self.assertEqual(prev_loop, self.post2)

    def test_no_ordering(self):
        qs = Post.objects.all().order_by()

        first = qs.first()
        self.assertEqual(first, self.post1)

        second = next_in_order(first, qs)
        self.assertEqual(second, self.post2)

        third = next_in_order(second, qs)
        self.assertEqual(third, self.post3)

        fourth = next_in_order(third, qs)
        self.assertEqual(fourth, None)

        fourth_loop = next_in_order(third, qs, loop=True)
        self.assertEqual(fourth_loop, self.post1)

        prev = prev_in_order(first, qs)
        self.assertEqual(prev, None)

        prev_loop = prev_in_order(first, qs, loop=True)
        self.assertEqual(prev_loop, self.post3)

    def test_empty_ordering(self):
        qs = Category.objects.all()

        first = qs.first()
        self.assertEqual(first, self.first_category)

        second = next_in_order(first, qs)
        self.assertEqual(second, self.second_category)

        third = next_in_order(second, qs)
        self.assertEqual(third, None)

        third_loop = next_in_order(second, qs, loop=True)
        self.assertEqual(third_loop, self.first_category)

        prev = prev_in_order(first, qs)
        self.assertEqual(prev, None)

        prev_loop = prev_in_order(first, qs, loop=True)
        self.assertEqual(prev_loop, self.second_category)
        
    def test_order_on_nullable(self):
        qs = Post.objects.all().order_by('author')
        first = qs.first()
        self.assertEqual(first, self.post3)

        second = next_in_order(first, qs)
        self.assertEqual(second, self.post1)

        third = next_in_order(second, qs)
        self.assertEqual(third, self.post2)

        fourth = next_in_order(third, qs)
        self.assertEqual(fourth, None)

        fourth_loop = next_in_order(third, qs, loop=True)
        self.assertEqual(fourth_loop, self.post3)

        prev = prev_in_order(first, qs)
        self.assertEqual(prev, None)

        prev_loop = prev_in_order(first, qs, loop=True)
        self.assertEqual(prev_loop, self.post2)
