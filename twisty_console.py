# Pipe a console session into this, and it outputs a GitHub markdown version
# with the commands' output in collapsible <details> tags.
#
# clipv | python twisty_console.py "❯ " 2 | gist -p -f console.md
#
# The arguments are:
#   prompt marker: the string at the end of your prompt. This must be distinctive
#   lines before (optional): the number of extra lines in your prompt

import html
import sys

def main(prompt, nbefore=0):
    text = sys.stdin.read()
    print(make_twisty(text, prompt, int(nbefore)))

def make_twisty(text, prompt, nbefore):
    lines = text.splitlines()
    twisty = []
    twprint = twisty.append
    prompt_line_nums = [n for n, line in enumerate(lines) if prompt.rstrip() in line]

    for pnum, npnum in zip(prompt_line_nums, prompt_line_nums[1:] + [-1]):
        prompt_line = lines[pnum].partition(prompt)[2]
        if not prompt_line.strip():
            continue
        twprint(f"<details>\n<summary>{html.escape(prompt_line)}</summary>\n")
        twprint("```")
        output = "\n".join(lines[pnum+1:npnum-nbefore])
        twprint(output)
        twprint("```\n\n</details>\n")
    return "\n".join(twisty) + "\n"

main(*sys.argv[1:])
