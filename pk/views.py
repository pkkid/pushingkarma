# encoding: utf-8
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from pk import log, utils
from pk.utils import auth
from .models import AccountSerializer


@ensure_csrf_cookie
def index(request, tmpl='index.html'):
    return utils.response(request, tmpl, {})


class AccountViewSet(viewsets.ViewSet):
    queryset = User.objects.filter(pk=-1)
    serializer_class = AccountSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def list(self, request, *args, **kwargs):
        serializer = AccountSerializer(self.request.user, context={'request':request})
        return Response(serializer.data)

    @list_route(methods=['post'])
    def login(self, request, *args, **kwargs):
        try:
            email = request.POST.get('email')
            passwd = request.POST.get('password')
            code = request.POST.get('code')
            user = (auth.auth_google(request, code) if code
                else auth.auth_django(request, email, passwd))
            if user and user.is_active:
                serializer = AccountSerializer(user, context={'request':request})
                return Response(serializer.data)
        except Exception as err:
            log.error(err, exc_info=1)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @list_route(methods=['post'])
    def logout(self, request, *args, **kwargs):
        logout(request)
        return Response({'status': 'Successfully logged out.'})
