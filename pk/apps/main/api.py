# encoding: utf-8
import logging, requests
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja import Body, Router
from ninja.errors import HttpError
from pk.utils.django import cache_response
from .schemas import GlobalVarsSchema, UserSchema, LoginSchema
from .schemas import AiPromptQuestionSchema, AiPromptResponseSchema
from typing import Optional
log = logging.getLogger(__name__)
router = Router()

class AiPromptBlocked(Exception):
    pass


@router.post('/login', response=UserSchema)
def login(request, data:LoginSchema=Body(...)):
    """ Log into to the django application. """
    try:
        username = get_object_or_404(User, email=data.email).username
        user = authenticate(username=username, password=data.password)
        if user and user.is_active:
            django_login(request, user)
            log.info('Logged in as %s', user.email)
            return user
    except Exception as err:
        log.error(f'Login error: {err}')
    raise HttpError(403, 'Unknown email or password.')


@router.post('/logout', response=dict)
def logout(request):
    """ Logs the current user out. """
    django_logout(request)
    return {'status': 'Successfully logged out.'}


@router.get('/global_vars', response=GlobalVarsSchema)
def get_global_vars(request):
    """ Return global variables. """
    user = request.user if request.user.is_authenticated else None
    result = dict(**settings.GLOBALVARS)
    result['user'] = user
    return result


@router.get('/glances')
def glances(request):
    """ Proxy the Glances /api/4/all endpoint to avoid browser Private Network Access restrictions. """
    glances_url = getattr(settings, 'GLANCES_URL', 'http://192.168.4.253:61208')
    response = requests.get(f'{glances_url}/api/4/all', timeout=5)
    return response.json()


@router.post('/aiprompt', response=Optional[AiPromptResponseSchema])
@cache_response(timeout=86400, prefix='aiprompt', peruser=False, bodyarg='data')
def aiprompt(request, data:AiPromptQuestionSchema=Body(...), cache_only:bool=False):
    """ Ask Gemini a question. Pass cache_only=true to return null on a cache miss instead of
        calling the AI. This allows callers to silently check for a cached response.
    """
    if not request.user.is_authenticated:
        raise HttpError(403, 'Permission denied.')
    prompt = data.prompt.strip()
    if not prompt or len(prompt) > settings.AIPROMPT_MAX_CHARS:
        raise HttpError(400, 'Prompt empty or too long.')
    if cache_only: return None
    response = _aiprompt_gemini(prompt)
    response = response[:settings.AIPROMPT_MAX_RESPONSE]
    return {'response': response}


def _aiprompt_gemini(prompt):
    """ Ask Gemini a question and return the response text. """
    if not settings.GEMINI_API_KEY:
        raise Exception('Gemini API key not configured.')
    model = settings.GEMINI_MODEL
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    payload = {'contents': [{'role': 'user', 'parts': [{'text': prompt}]}]}
    headers = {'x-goog-api-key': settings.GEMINI_API_KEY}
    result = requests.post(url, headers=headers, json=payload, timeout=settings.AIPROMPT_TIMEOUT)
    result.raise_for_status()
    data = result.json()
    if blockreason := data.get('promptFeedback', {}).get('blockReason'):
        raise Exception(f'Prompt blocked: {blockreason}')
    return data['candidates'][0]['content']['parts'][0]['text'].strip()

