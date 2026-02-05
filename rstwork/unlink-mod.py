"""
Change every module page in the CPython docs 
so that the title doesn't link to itself.
"""

import re
from pathlib import Path

# Edge cases:
# - modules with a blank line at the top.
# - modules that already had the !-prefix to suppress the link.
# - had to fix the rule length
# - pages that started with a link, but to the main module page.
#       unittest.mock-examples.rst
# - pages with slightly off names:
#       xml.sax.xmlreader is in xml.sax.reader.rst
#       xml.etree.ElementTree is in xml.etree.elementtree.rst
#       xml.parsers.expat is in pyexpat.rst
#       xml.sax.saxutils is in xml.sax.utils.rst
# - pages with two links in the title!
#       copyreg.rst

def fix_title_in_one_file(fpath):
    text = fpath.read_text().lstrip()
    if not text.startswith(":mod:`"):
        return
    if text.startswith(":mod:`!"):
        return
    lines = text.splitlines(keepends=True)
    modname = lines[0].split("`")[1]
    if modname != fpath.stem:
        print(f"WUT: {modname=}, {fpath.stem=}")
    lines[0] = lines[0].replace(":mod:`", ":mod:`!")
    lines[1] = lines[1][0] * (len(lines[0]) - 1) + "\n"
    fpath.write_text("".join(lines))
    print(f"Updated {fpath}")

def fix_self_references_in_one_file(fpath):
    text = fpath.read_text()
    top_line = text.splitlines()[0]
    if not (m := re.search(r"^:mod:`!?([\w\.]+)`", top_line)):
        return
    modname = m[1]
    newtext = text.replace(f":mod:`{modname}`", f":mod:`!{modname}`")
    # Note: this doesn't fix header underscores, those will have to be fixed by
    # hand, but there won't be many.
    if newtext != text:
        fpath.write_text(newtext)
        print(f"Updated self-references in {fpath}")

for fpath in Path(".").glob("**/*.rst"):
    fix_title_in_one_file(fpath)
    fix_self_references_in_one_file(fpath)
