"""
Meta Data Extension for Python-Markdown
=======================================
This extension adds Meta Data handling to markdown.
See <https://Python-Markdown.github.io/extensions/meta_data>
for documentation.
Original code Copyright 2007-2008 [Waylan Limberg](http://achinghead.com).
All changes Copyright 2008-2014 The Python Markdown Project
License: [BSD](https://opensource.org/licenses/bsd-license.php)

This file was modified to make it use TOML front matter.
"""

import re
import logging
import toml

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

log = logging.getLogger("MARKDOWN")

# Global Vars
BEGIN_RE = re.compile(r"^-{3}(\s.*)?")
END_RE = re.compile(r"^(-{3}|\.{3})(\s.*)?")


class MetaExtension(Extension):
    """ Meta-Data extension for Python-Markdown. """

    def extendMarkdown(self, md):
        """ Add MetaPreprocessor to Markdown instance. """
        md.registerExtension(self)
        self.md = md
        md.preprocessors.register(MetaPreprocessor(md), "meta", 27)

    def reset(self):
        self.md.Meta = {}


class MetaPreprocessor(Preprocessor):
    """ Get Meta-Data. """

    def run(self, lines):
        """ Parse Meta-Data and store in Markdown.Meta. """
        key = None
        if lines and BEGIN_RE.match(lines[0]):
            lines.pop(0)
            meta = ""
            while lines:
                line = lines.pop(0)
                if END_RE.match(line):
                    break
                else:
                    meta += line
                    meta += "\n"
            self.md.Meta = toml.loads(meta)
        return lines


def makeExtension(**kwargs):  # pragma: no cover
    return MetaExtension(**kwargs)
