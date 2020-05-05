# encoding: utf-8
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from pk import log


def custom_exception_handler(err, context):
    """ Custom exception handler for Django Rest Framework.
        https://www.django-rest-framework.org/api-guide/exceptions/
    """
    IGNORE_ERRORS = (NotAuthenticated,)
    if isinstance(err, IGNORE_ERRORS):
        log.warning(err)
        return Response({'detail':str(err)})
    log.exception(err)
    return Response({'detail':str(err)})
