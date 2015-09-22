#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from pk import utils


@require_POST
def user_login(request):
    try:
        test = utils.get_object_or_none(User, email=request.POST.get('email'))
        passwd = request.POST.get('password')
        user = authenticate(username=test.username, password=passwd)
        if not user or not user.is_active:
            return utils.response_json_error('Invalid username or password.')
        login(request, user)
        return utils.response_json_success()
    except Exception as err:
        return utils.response_json_error(str(err))


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return utils.response_json_success()
        return utils.response_json_error(form.errors)
    form = PasswordChangeForm(request.user)
    form.fields['old_password'].label = 'Current Password'
    form.fields['new_password1'].label = 'New Password'
    form.fields['new_password2'].label = 'Confirm Password'
    return utils.response_modal(dict(form=form))
