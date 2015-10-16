#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import gfm, re
from pk import utils

INCLUDE_REGEX = '(<include\shref=[\'"]/p/([a-z0-9_/]+)[\'"]\s*/>)'
INCLUDE_INVALID = '<a class="invalid" href="/p/%s">[template:%s]</a>'
LINK_REGEX = '(<a\shref=[\'"]/p/([a-z0-9_/]+)[\'"]>(.+?)</a>)'
LINK_VALID = '<a href="/p/%s">%s</a>'
LINK_INVALID = '<a class="invalid" href="/p/%s">%s</a>'
NO_CONTENT = 'Page contains no content.'


def text_to_html(text):
    text = gfm.markdown(text)
    text, included = _replace_includes(text)
    text = _replace_invalid_links(text)
    text = _remove_linefeeds(text)
    return text or NO_CONTENT, included


def _replace_includes(text):
    from pk.models import Page
    included = set()
    for match, href in re.findall(INCLUDE_REGEX, text):
        included.add(href)
        page = utils.get_object_or_none(Page, slug=href)
        if page:
            subhtml = text_to_html(page.body)[0]
            text = text.replace(match, subhtml, 1)
        else:
            link = INCLUDE_INVALID % (href, href)
            text = text.replace(match, link)
    return text, sorted(included)


def _replace_invalid_links(text):
    from pk.models import Page
    for match, href, txt in re.findall(LINK_REGEX, text):
        page = utils.get_object_or_none(Page, slug=href)
        if page:
            link = LINK_VALID % (href, txt)
            text = text.replace(match, link)
        else:
            link = LINK_INVALID % (href, txt)
            text = text.replace(match, link)
    return text


def _remove_linefeeds(text):
    return text.replace('<br />', '\n')
