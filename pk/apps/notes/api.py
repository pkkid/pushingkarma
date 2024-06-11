# encoding: utf-8
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from pk.utils.apiutils import DynamicFieldsSerializer
from pk.utils.apiutils import ModelViewSetWithUserPermissions
from pk.utils.search import FIELDTYPES, SearchField, Search
from .models import Note

NOTESEARCHFIELDS = {
    'title': SearchField(FIELDTYPES.STR, 'title'),
    'body': SearchField(FIELDTYPES.STR, 'body'),
    'tags': SearchField(FIELDTYPES.STR, 'tags'),
}


class NoteSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Note
        fields = ('id','title','tags','body','created','modified','url','weburl')

    def get_tags(self, note):
        return note.list_tags()


class NotesViewSet(ModelViewSetWithUserPermissions):
    queryset = Note.objects.order_by('-modified')
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    list_fields = ['id','url','weburl','title','tags','created','modified']

    def list(self, request, *args, **kwargs):
        searchdata = {}
        searchstr = request.GET.get('search')
        notes = Note.objects.order_by('-modified')
        if not request.user.is_authenticated:
            notes = notes.exclude(tags__icontains='private')
        if searchstr:
            search = Search(notes, NOTESEARCHFIELDS, searchstr)
            notes = search.queryset()
            searchdata = {'searchstr':searchstr, 'errors':search.errors, 'datefilters': search.datefilters}
        page = self.paginate_queryset(notes)
        serializer = NoteSerializer(page, context={'request':request}, many=True, fields=self.list_fields)
        response = self.get_paginated_response(serializer.data)
        response.data.update(searchdata)
        response.data.move_to_end('results')
        return response

    def retrieve(self, request, *args, **kwargs):
        # Check we have permission to view this note
        instance = self.get_object()
        if instance.is_private():
            if request.user != instance.user or not request.user.is_superuser:
                raise PermissionDenied
        return super(ModelViewSetWithUserPermissions, self).retrieve(request, *args, **kwargs)
