#!/usr/bin/env python
# encoding: utf-8
import markdown
from bs4 import BeautifulSoup
from collections import defaultdict
from pk import utils
from pymdownx import github

MARKDOWN_EXTENSIONS = [
    github.GithubExtension([]),
]


class Markdown(object):
    NO_CONTENT = 'Page contains no content.'
    VALID, INVALID = 'valid', 'invalid'

    def __init__(self, text, cls=None, prefix='/', kwvars=None):
        self.text = text
        self.cls = cls
        self.prefix = prefix
        self.kwvars = kwvars or {}
        self.meta = defaultdict(dict)
        self.html = self._render_html()

    def _render_html(self):
        text = self._explicit_linefeeds(self.text)
        text = self._replace_kwvars(text)
        html = markdown.markdown(text, extensions=MARKDOWN_EXTENSIONS)
        soup = BeautifulSoup(html, 'html.parser')
        if self.cls:
            self._replace_includes(soup)
            self._replace_links(soup)
        self._syntax_hinting(soup)
        self._clean_linefeeds(soup)
        return str(soup) or self.NO_CONTENT

    def _replace_kwvars(self, text):
        for key, val in self.kwvars.items():
            text = text.replace('{{%s}}' % key, val)
        return text

    def _replace_includes(self, soup):
        for elem in soup.find_all('include'):
            slug = elem.attrs.get('href','').replace(self.prefix,'').strip('/')
            subitem = utils.get_object_or_none(self.cls, slug=slug)
            if subitem:
                kwvars = dict(elem.attrs); kwvars['text'] = elem.text.strip()
                submd = Markdown(subitem.body, self.cls, self.prefix, kwvars)
                elem.replaceWith(BeautifulSoup(submd.html, 'html.parser'))
                self.meta['includes'][slug] = self.VALID
                self._merge_submeta(submd.meta)
            else:
                href = '%s%s' % (self.prefix, slug)
                link = '<a class="invalid" href="%s">[template:%s]</a>' % (href, href)
                elem.replaceWith(BeautifulSoup(link, 'html.parser'))
                self.meta['includes'][slug] = self.INVALID

    def _replace_links(self, soup):
        for elem in soup.find_all('a'):
            if not elem.attrs.get('href','').startswith(self.prefix):
                continue
            slug = elem.attrs.get('href','').replace(self.prefix,'').strip('/')
            subitem = utils.get_object_or_none(self.cls, slug=slug)
            href = '%s%s' % (self.prefix, slug)
            if subitem:
                link = '<a href="%s">%s</a>' % (href, elem.text)
                elem.replaceWith(BeautifulSoup(link, 'html.parser'))
                # self.meta['links'][slug] = self.VALID
            else:
                link = '<a class="invalid" href="%s">%s</a>' % (href, elem.text)
                elem.replaceWith(BeautifulSoup(link, 'html.parser'))
                self.meta['links'][slug] = self.INVALID
                
    def _syntax_hinting(self, soup):
        pass

    def _explicit_linefeeds(self, text):
        text = text.replace('<br/>', '<brx/>')
        text = text.replace('<br />', '<brx/>')
        return text

    def _clean_linefeeds(self, soup):
        for elem in soup.find_all('br'):
            elem.replaceWith('\n')
        for elem in soup.find_all('brx'):
            elem.replaceWith(BeautifulSoup('<br/>', 'html.parser'))
        return soup

    def _merge_submeta(self, submeta):
        for key, slugs in submeta.items():
            for slug, data in slugs.items():
                self.meta[key][slug] = data
