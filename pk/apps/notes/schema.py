# encoding: utf-8
import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from pk.utils.graphene import paginated_type, paginator
from pk.utils.search import FIELDTYPES, SearchField, Search
from .models import Note


class NoteType(DjangoObjectType):
    class Meta:
        model = Note


NotePageType = paginated_type(NoteType)  # noqa
NOTESEARCHFIELDS = {
    'title': SearchField(FIELDTYPES.STR, 'title'),
    'body': SearchField(FIELDTYPES.STR, 'body'),
    'tags': SearchField(FIELDTYPES.STR, 'tags'),
}


class NoteQuery(ObjectType):
    note = graphene.Field(NoteType, id=graphene.Int(), slug=graphene.String())
    notes = graphene.Field(NotePageType, search=graphene.String(), page=graphene.Int())

    def resolve_note(self, info, **kwargs):
        noteid = kwargs.get('id')
        slug = kwargs.get('slug')
        if noteid: return Note.objects.get(pk=noteid)
        if slug: return Note.objects.get(slug=slug)
        return None

    def resolve_notes(self, info, search='', page=1, **kwargs):
        notes = Note.objects.order_by('-modified')
        if not info.context.user.is_authenticated:
            notes = notes.exclude(tags__icontains='private')
        if search:
            searchcls = Search(notes, NOTESEARCHFIELDS, search)
            notes = searchcls.queryset()
        return paginator(notes, 30, page, NotePageType)
