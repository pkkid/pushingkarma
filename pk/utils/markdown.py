#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import gfm, re
from collections import defaultdict
from pk import utils


class Markdown(object):
    NO_CONTENT = 'Page contains no content.'
    VALID, INVALID = 'valid', 'invalid'

    def __init__(self, text, cls=None, prefix='/'):
        self.text = text
        self.cls = cls
        self.prefix = prefix
        self.meta = defaultdict(dict)
        self.html = self._render_html()

    def _render_html(self):
        html = gfm.markdown(self.text)
        if self.cls:
            html = self._replace_includes(html)
            html = self._replace_links(html)
        html = self._remove_linefeeds(html)
        return html or self.NO_CONTENT

    def _replace_includes(self, html):
        regex = '(<include\s+href=[\'"]%s([a-z_0-9]+)[\'"]\s*/>)' % self.prefix
        for match, slug in re.findall(regex, html):
            subitem = utils.get_object_or_none(self.cls, slug=slug)
            if subitem:
                submd = Markdown(subitem.body, self.cls)
                subhtml = submd.html
                html = html.replace(match, subhtml, 1)
                self.meta['includes'][slug] = self.VALID
                self._merge_submeta(submd.meta)
            else:
                href = '%s%s' % (self.prefix, slug)
                link = '<a class="invalid" href="%s">[template:%s]</a>' % (href, href)
                html = html.replace(match, link)
                self.meta['includes'][slug] = self.INVALID
        return html

    def _replace_links(self, html):
        regex = '(<a\s+href=[\'"]%s([a-z_0-9]+)[\'"]>(.+?)</a>)' % self.prefix
        for match, slug, txt in re.findall(regex, html):
            subitem = utils.get_object_or_none(self.cls, slug=slug)
            href = '%s%s' % (self.prefix, slug)
            if subitem:
                link = '<a href="%s">%s</a>' % (href, txt)
                html = html.replace(match, link)
                self.meta['links'][slug] = self.VALID
            else:
                link = '<a class="invalid" href="%s">%s</a>' % (href, txt)
                html = html.replace(match, link)
                self.meta['links'][slug] = self.INVALID
        return html

    def _remove_linefeeds(self, html):
        return html.replace('<br />', '\n')

    def _merge_submeta(self, submeta):
        for key, slugs in submeta.items():
            for slug, data in slugs.iter():
                self.meta[key][slug] = data
