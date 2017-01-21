#! /usr/bin/env python

import re
from docutils.core import publish_parts

rx_comments = re.compile(r'/\*.*?\*/\n', re.DOTALL)
rx_blanks = re.compile(r'\n\n\n')

try:
    ifd = open('README.rst', 'r')
    data = ifd.read()
    ifd.close()
    parts = publish_parts(data, writer_name="html")
    html = parts['html_body']
    stylesheet = parts['stylesheet']
    stylesheet = rx_comments.sub('', stylesheet)
    stylesheet = re.sub('\n\n\n', '\n', stylesheet)
    stylesheet = re.sub('\n\n', '\n', stylesheet)
    gallery_css = "img.gallery { padding:5px; border:2px; margin:2px; }\n"
    stylesheet = re.sub('</style>', gallery_css + '</style>', stylesheet)

except Exception:
    print "Error converting to html"

else:
    ofd = open('README.html', 'w')
    ofd.write(stylesheet)
    ofd.write(html)
    ofd.close()
