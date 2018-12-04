import csv
import os.path
import sys
import textwrap

import colorama
from colorama import Fore, Back, Style

COMMENTS_FILE = "comments.csv"

def read_comments():
    comments = {}
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE) as f:
            for r in csv.reader(f):
                comments[int(r[0])] = r[1]
    return comments

def write_comments(comments):
    with open(COMMENTS_FILE, "w") as f:
        writer = csv.writer(f)
        for k in sorted(comments):
            writer.writerow((k, comments[k]))

def add_comment(comments, rownum, comment):
    old_comment = comments.get(rownum, '')
    if old_comment:
        old_comment += "\n"
    comment = old_comment + comment
    comments[rownum] = comment.strip()
    write_comments(comments)

def print_row(d):
    print(f"\n{Fore.YELLOW}{'#'*100}{Fore.RESET}")
    next_post = ""
    for k, v in d.items():
        v = "\n".join(textwrap.fill(p, width=100) for p in v.splitlines())
        v = v.strip()
        if "\n" in v:
            pre = "\n"
            sep = "\n"
        else:
            pre = ""
            sep = ":\t"

        print(f"{next_post or pre}{Style.BRIGHT}{k}{Style.NORMAL}{sep}{v}")
        next_post = pre

def main():
    colorama.init()

    fname = sys.argv[1]

    with open(fname) as f:
        rows = list(csv.DictReader(f))

    rows.insert(0, {})  # Fieldnames
    rows.insert(0, {})  # 1-origin

    print(f"{len(rows)-1} rows, numbered 2-{len(rows)-1}")

    comments = read_comments()

    row = 2
    last_shown = None

    while True:
        if row != last_shown:
            print_row(rows[row])
            comment = comments.get(row, "")
            if comment:
                print(f"\n{Fore.YELLOW}Comment:{Fore.RESET} {comment}\n")
            last_shown = row

        try:
            cmd = input(f"{Style.BRIGHT}{row}{Style.NORMAL} >> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break
        if not cmd:
            continue
        elif cmd == "q":
            # Quit.
            break
        elif cmd == "s":
            # Show the row again.
            last_shown = None
        elif cmd == "n":
            # Next row.
            if row >= len(rows)-1:
                print("@end")
            else:
                row += 1
        elif cmd == "p":
            # Previous row.
            if row == 2:
                print("@begin")
            else:
                row -= 1
        elif cmd.startswith("c"):
            # Write a comment.
            comment = cmd.partition(" ")[-1]
            add_comment(comments, row, comment)
        else:
            # A number to jump to.
            try:
                nrow = int(cmd)
            except ValueError:
                print(f"Didn't understand {cmd!r}")
            else:
                if 2 <= nrow <= len(rows)-1:
                    row = nrow
                else:
                    print(f"There are {len(rows)} rows")

main()
