# encoding: utf-8
import graphene
from graphene_django.types import DjangoObjectType, ObjectType
from pk.utils.graphene import paginated_type, paginator
from .models import Note


class NoteType(DjangoObjectType):
    class Meta:
        model = Note

NotePageType = paginated_type(NoteType)  # noqa


class NoteQuery(ObjectType):
    note = graphene.Field(NoteType, id=graphene.Int(), slug=graphene.String())
    notes = graphene.Field(NotePageType, page=graphene.Int())

    def resolve_note(self, info, **kwargs):
        noteid = kwargs.get('id')
        slug = kwargs.get('slug')
        if noteid: return Note.objects.get(pk=noteid)
        if slug: return Note.objects.get(slug=slug)
        return None

    def resolve_notes(self, info, page=1, **kwargs):
        if info.context.user.is_authenticated:
            notes = Note.objects.all()
        notes = Note.objects.exclude(tags__icontains='private')
        return paginator(notes, 100, page, NotePageType)
