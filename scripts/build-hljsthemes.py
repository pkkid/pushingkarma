#!/usr/bin/env python
"""
Build Highlight.js Themes
Build namespaced Highlight.js base16 themes into a single CSS output file.
"""
import os, textwrap, sys
import logging as log
from os.path import dirname, abspath

logformat = '%(asctime)-.19s %(module)16s:%(lineno)-3s %(levelname)-7s %(message)s'
log.basicConfig(stream=sys.stdout, level=log.INFO, format=logformat)

ROOT = dirname(dirname(abspath(__file__)))
HLJSDIR = f'{ROOT}/node_modules/highlight.js/styles/base16'
DESTFILE = f'{ROOT}/vue/assets/hljsthemes.css'
_ = lambda path: path.replace(ROOT, '')


if __name__ == '__main__':
    content = ''
    # Read minified files into content string
    for filename in sorted(os.listdir(HLJSDIR)):
        if filename.endswith('.min.css'):
            name = filename.split('.')[0]
            with open(f'{HLJSDIR}/{filename}', 'r') as handle:
                tcontent = textwrap.indent(handle.read(), '  ')
                content += f"[theme='{name}'] {{\n{tcontent}\n}}\n"
    # Write content string to DESTFILE
    log.info(f'Saving {_(DESTFILE)}')
    with open(DESTFILE, 'w') as handle:
        handle.write(content)
