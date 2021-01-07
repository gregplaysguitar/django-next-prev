# -*- coding: utf-8 -*-

from functools import partial

from django.db import models

if not locals().get('reduce'):
    from functools import reduce

__version__ = '1.1.0'
VERSION = tuple(map(int, __version__.split('.')))


def get_model_attr(instance, attr):
    """Example usage: get_model_attr(instance, 'category__slug')"""
    for field in attr.split('__'):
        instance = getattr(instance, field)
    return instance


def next_or_prev_in_order(instance, qs=None, prev=False, loop=False):
    """Get the next (or previous with prev=True) item for instance, from the
       given queryset (which is assumed to contain instance) respecting
       queryset ordering. If loop is True, return the first/last item when the
       end/start is reached. """

    if qs is None:
        qs = instance.__class__.objects.all()

    if prev:
        qs = qs.reverse()
        lookup = 'lt'
    else:
        lookup = 'gt'

    q_list = []
    prev_fields = []

    if qs.query.extra_order_by:
        ordering = qs.query.extra_order_by
    elif qs.query.order_by:
        ordering = qs.query.order_by
    elif qs.query.get_meta().ordering:
        ordering = qs.query.get_meta().ordering
    else:
        ordering = []

    ordering = list(ordering)

    # if the ordering doesn't contain pk, append it and reorder the queryset
    # to ensure consistency
    if 'pk' not in ordering and '-pk' not in ordering:
        ordering.append('pk')
        qs = qs.order_by(*ordering)

    for field in ordering:
        if field[0] == '-':
            this_lookup = (lookup == 'gt' and 'lt' or 'gt')
            field = field[1:]
        else:
            this_lookup = lookup
        q_kwargs = dict([(f, get_model_attr(instance, f))
                         for f in prev_fields])
        key = "%s__%s" % (field, this_lookup)
        q_kwargs[key] = get_model_attr(instance, field)
        q_list.append(models.Q(**q_kwargs))
        prev_fields.append(field)
    try:
        return qs.filter(reduce(models.Q.__or__, q_list))[0]
    except IndexError:
        length = qs.count()
        if loop and length > 1:
            # queryset is reversed above if prev
            return qs[0]
    return None


next_in_order = partial(next_or_prev_in_order, prev=False)
prev_in_order = partial(next_or_prev_in_order, prev=True)
