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


    # for field in ordering:
    #     if field[0] == '-':
    #         this_lookup = (lookup == 'gt' and 'lt' or 'gt')
    #         field = field[1:]
    #     else:
    #         this_lookup = lookup
    #     q_kwargs = dict([(f, get_model_attr(instance, f))
    #                      for f in prev_fields])
    #     key = "%s__%s" % (field, this_lookup)
    #     val = get_model_attr(instance, field)
    #     q_kwargs[key] = val
    #     q_list.append(models.Q(**q_kwargs))
    #     prev_fields.append(field)

    try:
        item = get_next_prev_item(instance, qs, ordering, lookup, prev)
        return item

    except IndexError:
        length = qs.count()
        if loop and length > 1:
            # queryset is reversed above if prev
            return qs[0]
    return None


def get_next_prev_item(instance, qs, ordering, lookup, prev=False):
    # print("POPPED ORDERING", ordering, qs)

    q_list = []
    prev_fields = []

    for field in ordering:
        if field[0] == '-':
            this_lookup = (lookup == 'gt' and 'lt' or 'gt')
            field = field[1:]
        else:
            this_lookup = lookup
        q_kwargs = dict([(f, get_model_attr(instance, f))
                         for f in prev_fields])
        key = "%s__%s" % (field, this_lookup)
        val = get_model_attr(instance, field)
        q_kwargs[key] = val
        q_list.append(models.Q(**q_kwargs))
        prev_fields.append(field)

    # remove first key from ordering, which is the primary field we are sorting after
    field = ordering.pop(0)
    if field[0] == '-':
        field = field[1:]

    val = get_model_attr(instance, field)

    # if len of ordering contains more than one key, sort by secondary key
    # last item should be always pk and is always added before
    # +1 because we popped a key before
    if len(ordering) + 1 > 1:
        # if val is not None, there is no need to sort by second key
        if val is not None:
            qs = qs.filter(reduce(models.Q.__or__, q_list))
        else:
            # Build query for secondary key lookup

            lookup2 = 'gt'
            if prev:
                lookup2 = 'lt'

            field2 = ordering[0]
            if field2[0] == '-':
                lookup2 = (lookup2 == 'gt' and 'lt' or 'gt')
                field2 = field2[1:]

            # exclude instance from queryset, so it won't appear in a queryset filtered to (field__isnull=True)
            qs = qs.filter().exclude(pk=instance.pk)
            # build filter for secondary key
            filter_term = {field2 + "__" + lookup2: get_model_attr(instance, field2)}

            if lookup == 'lt':
                # if the lookup would be (field__lt=None) the item can only be in a queryset filtered to None
                filter_term[field + "__isnull"] = True
            qs = qs.filter(**filter_term)

    # ordering had only one key left (pk), so return the matching item for that
    # no need to check if value is None, pk can't be none
    else:
        return qs.filter(reduce(models.Q.__or__, q_list))[0]

    # get the next/prev item from the queryset. IndexError is caught in the super function
    item = qs[0]

    # If field value of next/prev is same as of instance, filter to a subset with this value, ordered by secondary key
    # recursive call
    if get_model_attr(item, field) == get_model_attr(instance, field):
        filter_term = {field: val}
        qs = qs.filter(models.Q(**filter_term))

        return get_next_prev_item(instance, qs, ordering, lookup, prev)

    return item


next_in_order = partial(next_or_prev_in_order, prev=False)
prev_in_order = partial(next_or_prev_in_order, prev=True)
