"""
Admonition extension for Python-Markdown
========================================
Adds rST-style admonitions. Inspired by [rST][] feature with the same name.
[rST]: http://docutils.sourceforge.net/docs/ref/rst/directives.html#specific-admonitions  # noqa
See <https://Python-Markdown.github.io/extensions/admonition>
for documentation.
Original code Copyright [Tiago Serafim](https://www.tiagoserafim.com/).
All changes Copyright The Python Markdown Project
License: [BSD](https://opensource.org/licenses/bsd-license.php)

This file was modified to make it compatible with the Bulma CSS framework.
"""

from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
import xml.etree.ElementTree as etree
import re


class AdmonitionExtension(Extension):
    """ Admonition extension for Python-Markdown. """

    def extendMarkdown(self, md):
        """ Add Admonition to Markdown instance. """
        md.registerExtension(self)

        md.parser.blockprocessors.register(
            AdmonitionProcessor(md.parser), "custom-admonition", 105
        )


class AdmonitionProcessor(BlockProcessor):

    CLASSNAME = "message"
    CLASSNAME_TITLE = "message-header"
    CLASSNAME_BODY = "message-body"
    RE = re.compile(r'(?:^|\n)!!! ?([\w\-]+(?: +[\w\-]+)*)(?: +"(.*?)")? *(?:\n|$)')
    RE_SPACES = re.compile("  +")

    def test(self, parent, block):
        sibling = self.lastChild(parent)
        return self.RE.search(block) or (
            block.startswith(" " * self.tab_length)
            and sibling is not None
            and sibling.get("class", "").find(self.CLASSNAME) != -1
        )

    def run(self, parent, blocks):
        sibling = self.lastChild(parent)
        block = blocks.pop(0)
        m = self.RE.search(block)

        if m:
            block = block[m.end() :]  # removes the first line

        block, theRest = self.detab(block)

        if m:
            klass, title = self.get_class_and_title(m)
            outer_div = etree.SubElement(parent, "div")
            outer_div.set("class", "{} {}".format(self.CLASSNAME, klass))
            if title:
                p = etree.SubElement(outer_div, "p")
                p.text = title
                p.set("class", self.CLASSNAME_TITLE)
            div = etree.SubElement(outer_div, "div")
            div.set("class", "{}".format(self.CLASSNAME_BODY))
        else:
            div = sibling

        self.parser.parseChunk(div, block)

        if theRest:
            # This block contained unindented line(s) after the first indented
            # line. Insert these lines as the first block of the master blocks
            # list for future processing.
            blocks.insert(0, theRest)

    def get_class_and_title(self, match):
        klass, title = match.group(1).lower(), match.group(2)
        klass = self.RE_SPACES.sub(" ", klass)
        if title is None:
            # no title was provided, use the capitalized classname as title
            # e.g.: `!!! note` will render
            # `<p class="admonition-title">Note</p>`
            title = klass.split(" ", 1)[0].capitalize()
        elif title == "":
            # an explicit blank title should not be rendered
            # e.g.: `!!! warning ""` will *not* render `p` with a title
            title = None
        return klass, title


def makeExtension(**kwargs):  # pragma: no cover
    return AdmonitionExtension(**kwargs)
