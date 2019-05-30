# encoding: utf-8
import graphene
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def paginated_type(objtype):
    """ Factory function returns a pagetype object for Graphene.
        Used to create the paginator object below.
    """
    class PaginatedType(graphene.ObjectType):
        page = graphene.Int()
        num_pages = graphene.Int()
        has_next = graphene.Boolean()
        has_prev = graphene.Boolean()
        objects = graphene.List(objtype)
    return PaginatedType


def paginator(queryset, pagesize, pagenum, pagetype, **kwargs):
    """ Build and return a paginator object for the specified pagetype. """
    # Get the current page from passed in arguments
    pager = Paginator(queryset, pagesize)
    try:
        page = pager.page(pagenum)
    except PageNotAnInteger:
        page = pager.page(1)
    except EmptyPage:
        page = pager.page(pager.num_pages)
    # Return the PaginatedType Graphene object
    return pagetype(page=page.number, num_pages=pager.num_pages,
        has_next=page.has_next(), has_prev=page.has_previous(),
        objects=page.object_list, **kwargs)
