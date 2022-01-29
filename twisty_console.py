# clipv | python twisty-console.py | gist -p -f console.md

import sys

PROMPT = "❯ "
NBEFORE = 2

text = sys.stdin.read().splitlines()
prompt_line_nums = [n for n, line in enumerate(text) if PROMPT.rstrip() in line]

for pnum, npnum in zip(prompt_line_nums, prompt_line_nums[1:] + [-1]):
    prompt_line = text[pnum].partition(PROMPT)[2]
    if not prompt_line.strip():
        continue
    print(f"<details>\n<summary>{prompt_line}</summary>\n")
    print("```")
    output = "\n".join(text[pnum+1:npnum-NBEFORE])
    print(output)
    print("```\n\n</details>\n")
