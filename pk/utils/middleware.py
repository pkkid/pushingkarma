# encoding: utf-8
import re

class CleanHTMLMiddleware(object):

    def process_response(self, request, response):
        if response.status_code == 200:
            if response['content-type'].startswith('text/html'):
                response.content = self.cleanHTML(response.content)
        return response

    def cleanHTML(self, content):
        newhtml, indent, script = [], 0, False
        for line in content.decode('utf8').split('\n'):
            stripped = line.strip()
            if not stripped: continue
            if '</script>' in stripped: script = False
            if '</pre>' in stripped: script = False
            if script:
                newhtml.append(line)
                continue
            if not script:
                newindent = indent
                newindent += len(re.findall(r'\<\w+', stripped))
                newindent -= len(re.findall(r'\</\w+', stripped))
                newindent -= len(re.findall(r'/\>', stripped))
                indent = min(indent, newindent)
            newhtml.append('%s%s' % (' '*(indent*2), stripped))
            if 'text/javascript' in stripped: script = True
            if '<pre' in stripped: script = True
            indent = newindent
        return '\n'.join(newhtml)
