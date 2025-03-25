#!/usr/bin/env python
# Make Themes
# Utility function creates all these in the highlight.js/styles/base16 directory
# and copies all the themes to a single vue/assests/hightlightjs-themes.js file.
# Each theme will be namespaced within a [theme='<theme-name>'] that must be
# included at or before the <pre> tag in the html element.
import os, textwrap
from os.path import dirname, abspath

ROOTDIR = f'{dirname(abspath(__file__))}/node_modules/highlight.js/styles/base16'
DESTFILE = f'{dirname(abspath(__file__))}/vue/assets/hljs-themes.css'


def make_themes():
    content = ''
    for filename in sorted(os.listdir(ROOTDIR)):
        if filename.endswith('.min.css'):
            name = filename.split('.')[0]
            with open(f'{ROOTDIR}/{filename}', 'r') as handle:
                tcontent = textwrap.indent(handle.read(), '  ')
                content += f"[theme='{name}'] {{\n{tcontent}\n}}\n"
    with open(DESTFILE, 'w') as handle:
        handle.write(content)

if __name__ == '__main__':
    make_themes()
