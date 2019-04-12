# -*- coding: utf-8 -*-

from functools import partial

from django.db import models

if not locals().get('reduce'):
    from functools import reduce

__version__ = '1.0.1'
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

    if not qs:
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

    # TODO do this recursively ?

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

    try:
        field = ordering[0]
        val = get_model_attr(instance, field)
        qss = qs
        print("ORDERING", ordering)
        print("INSTANCE", instance)
        print("FV", field, val)
        if val is not None:
            qss = qs.filter(reduce(models.Q.__or__, q_list))
        else:
            qss = qs.filter().exclude(pk=instance.pk)
            if prev:
                print("PREV of NULLL")
                filterterm = {field + "__isnull": True, "pk__lt":instance.pk}
                qss = qss.filter(**filterterm)
            else:
                print("NEXT of NULL")
                qss = qss.filter(pk__gt=instance.pk)


        item = qss[0]
        print(instance)
        print("VAL", val, field)
        print(item, instance)
        print(get_model_attr(item, field), get_model_attr(instance, field))
        print(get_model_attr(item, "pk") , get_model_attr(instance, "pk"))
        print("Yo")
        print(qss)

        if get_model_attr(item, field) == get_model_attr(instance, field):
            print("same", item, get_model_attr(item, field), instance, get_model_attr(instance, field))
            print("QK", q_kwargs)
            print("QL", q_list)
            filterterm = {field: val}
            print("FILTER", filterterm)
            qss = qss.filter(models.Q(**filterterm))
            print("new QS", qss)
            field2 = ordering[1]
            lookup = "gt"
            if field2[0] == "-":
                if prev:
                    lookup = "gt"
                else:
                    lookup = "lt"
                field2 = field2[1:]
            else:
                if prev:
                    lookup = "lt"

            print("FIELD", field2)
            filterterm = {}
            if prev:
                filterterm = {field2 + "__" + lookup: get_model_attr(instance, field2)}
                # item = qss.filter(**filterterm).first()

            else:
                filterterm = {field2 + "__" + lookup: get_model_attr(instance, field2)}
                # item = qss.filter(**filterterm).first()
            print("FILTERTERM", filterterm)
            qss = qss.filter(**filterterm)
            print(qss)
            item = qss.first()

        return item

    except IndexError:
        length = qs.count()
        if loop and length > 1:
            # queryset is reversed above if prev
            return qs[0]
    return None


next_in_order = partial(next_or_prev_in_order, prev=False)
prev_in_order = partial(next_or_prev_in_order, prev=True)
