from datetime import date

from django.test import TestCase

from .models import Post, Category

from next_prev import next_in_order, prev_in_order


class NextPrevTestCase(TestCase):
    def setUp(self):
        # add some content
        first_category = Category.objects.create(title='Category 1')
        second_category = Category.objects.create(title='Category 2')

        self.post1 = Post.objects.create(
            title='Post 1', text='Beautiful is better than ugly.',
            category=first_category, created=date(2015, 1, 1))
        self.post2 = Post.objects.create(
            title='Post 2', text='Simple is better than complex.',
            category=second_category, created=date(2015, 1, 1))
        self.post3 = Post.objects.create(
            title='Post 3',
            text='Complex is better than complicated.',
            category=first_category, created=date(2016, 1, 1))

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
