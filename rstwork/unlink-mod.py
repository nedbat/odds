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
    lines = fpath.read_text().splitlines(keepends=True)
    if not (m := re.search(r"^:mod:`!?([\w\.]+)`", lines[0])):
        return
    modname = m[1]
    changed = False
    for i, line in enumerate(lines):
        if f":mod:`{modname}`" in line:
            new_line = line.replace(f":mod:`{modname}`", f":mod:`!{modname}`")
            lines[i] = new_line
            changed = True
            if i < len(lines) - 1:
                next_line = lines[i + 1] 
                if len(next_line) == len(line) and len(set(next_line.rstrip())) == 1:
                    lines[i + 1] = next_line[0] * len(new_line.rstrip()) + next_line[-1]
    if changed:
        fpath.write_text("".join(lines))
        print(f"Updated self-references in {fpath}")

for fpath in Path(".").glob("**/*.rst"):
    fix_title_in_one_file(fpath)
    fix_self_references_in_one_file(fpath)
