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

    def __init__(self, text, cls=None, prefix='/'):
        self.text = text
        self.cls = cls
        self.prefix = prefix
        self.meta = defaultdict(set)

    @property
    def html(self):
        if getattr(self, '_html', None) is None:
            self._html = gfm.markdown(self.text)
            if self.cls:
                self._html = self._replace_includes(self._html)
                self._html = self._replace_links(self._html)
            self._html = self._remove_linefeeds(self._html)
        for key in self.meta:
            self.meta[key] = list(self.meta[key])
        return self._html or self.NO_CONTENT

    @property
    def includes(self):
        valid = list(self.meta['valid_includes'])
        invalid = list(self.meta['invalid_includes'])
        return list(set(valid + invalid))

    def _replace_includes(self, html):
        regex = '(<include\s+href=[\'"]%s([a-z_0-9]+)[\'"]\s*/>)' % self.prefix
        for match, slug in re.findall(regex, html):
            subitem = utils.get_object_or_none(self.cls, slug=slug)
            if subitem:
                submd = Markdown(subitem.body, self.cls)
                subhtml = submd.html
                html = html.replace(match, subhtml, 1)
                self.meta['valid_includes'].add(slug)
                for key in submd.meta:
                    self.meta[key].union(submd.meta[key])
            else:
                href = '%s%s' % (self.prefix, slug)
                link = '<a class="invalid" href="%s">[template:%s]</a>' % (href, href)
                html = html.replace(match, link)
                self.meta['invalid_includes'].add(slug)
        return html

    def _replace_links(self, html):
        regex = '(<a\s+href=[\'"]%s([a-z_0-9]+)[\'"]>(.+?)</a>)' % self.prefix
        for match, slug, txt in re.findall(regex, html):
            subitem = utils.get_object_or_none(self.cls, slug=slug)
            href = '%s%s' % (self.prefix, slug)
            if subitem:
                link = '<a href="%s">%s</a>' % (href, txt)
                html = html.replace(match, link)
                self.meta['valid_links'].add(slug)
            else:
                link = '<a class="invalid" href="%s">%s</a>' % (href, txt)
                html = html.replace(match, link)
                self.meta['invalid_links'].add(slug)
        return html

    def _remove_linefeeds(self, html):
        return html.replace('<br />', '\n')
