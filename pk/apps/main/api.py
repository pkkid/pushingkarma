# encoding: utf-8
import logging, requests, subprocess
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja import Body, Router
from ninja.errors import HttpError
from .schemas import GlobalVarsSchema, UserSchema, LoginSchema
from .schemas import ClaudeQuestionSchema, ClaudeResponseSchema
log = logging.getLogger(__name__)
router = Router()


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


@router.post('/claude', response=ClaudeResponseSchema)
def claude(request, data:ClaudeQuestionSchema=Body(...)):
    """ Ask Claude a question using the local CLI binary. """
    if not request.user.is_authenticated:
        raise HttpError(403, 'Permission denied.')
    max_prompt_chars = int(getattr(settings, 'CLAUDE_MAX_PROMPT_CHARS', 4000))
    max_response_chars = int(getattr(settings, 'CLAUDE_MAX_RESPONSE_CHARS', 20000))
    timeout_sec = int(getattr(settings, 'CLAUDE_TIMEOUT_SEC', 45))
    prompt = data.prompt.strip()
    if not prompt or len(prompt) > max_prompt_chars:
        raise HttpError(400, 'Prompt empty or too long.')
    try:
        command = [settings.CLAUDE_BIN, '-p', prompt]
        result = subprocess.run(command, capture_output=True, text=True,
            timeout=timeout_sec, check=True)
        response = result.stdout.strip()
        if len(response) > max_response_chars:
            response = response[:max_response_chars]
        return {'response': response}
    except subprocess.TimeoutExpired:
        raise HttpError(504, 'Claude request timed out.')  # noqa
    except subprocess.CalledProcessError as err:
        stderr = (err.stderr or '').strip()
        log.error('Claude CLI failed (%s): %s', err.returncode, stderr)
        raise HttpError(502, 'Claude command failed.')  # noqa
    except FileNotFoundError:
        raise HttpError(500, f'Claude binary not found: {settings.CLAUDE_BIN}')  # noqa
    except Exception as err:
        raise HttpError(500, f'Error running Claude command: {err}')  # noqa
