#!/usr/bin/env python3
#
# Run this like:
#
#   $ $(set_env.py FILE-GLOB ...)
#
# It looks through the specificed files for lines like this:
#
#   # $set_env.py: ENVVAR_NAME - Description of the environment variable.
#
# and prompts for values.  You can review, change, or delete values.
#
# Because it changes environment variables, you must run it inside $() as
# shown.  This is handy in your shell startup file:
#
#   alias set_env='$(set_env.py $(git ls-files))'

import contextlib
import glob
import os
import re
import sys

SETTINGS = []

def find_settings(args):
    args = args or ["*.py", "**/*.py"]
    line_pattern = r"\$set_env.py: (\w+) - (.*)"
    settings = set()
    filenames = [fname for glb in args for fname in glob.glob(glb, recursive=True)]
    for filename in filenames:
        with open(filename) as f:
            try:
                for line in f:
                    m = re.search(line_pattern, line)
                    if m:
                        settings.add(m.groups())
            except UnicodeDecodeError:
                # Probably wasn't a text file, ignore it.
                pass

    print(f"Read {len(filenames)} files")
    global SETTINGS
    SETTINGS = sorted(settings)

def read_them():
    values = {}
    for name, _ in SETTINGS:
        values[name] = os.environ.get(name)
    return values

def show_them(values):
    for i, (name, description) in enumerate(SETTINGS, start=1):
        value = values[name]
        if value is None:
            eq = ' '
            value = ''
        else:
            eq = '='
            value = repr(value)
        print("{:2d}: {:>30s} {} {:12s}   {}".format(i, name, eq, value, description))

def get_by_num(values, n):
    setting_name = SETTINGS[int(n)-1][0]
    return values[setting_name]

def set_by_num(values, n, value):
    setting_name = SETTINGS[int(n)-1][0]
    values[setting_name] = value

PROMPT = "(# [value] | x # ... | ? | q)> "
HELP = """\
Commands:
    "#" means a number of an environment variable, from 1 to {maxnum}.

    # value         - Give a value to a variable.
    #               - Toggle a variable between empty and '1'
    x # # ...       - Unset variables
    ?               - Show this help
    q               - Quit
"""

def get_new_values(values):
    show = True
    while True:
        if show:
            show_them(values)
            show = False
            print("")
        print(PROMPT, end='')
        sys.stderr.flush()
        try:
            cmd = input("").strip().split()
        except EOFError:
            print("\n")
            break
        if not cmd:
            continue
        elif cmd[0] == 'q':
            break
        elif cmd[0] == '?':
            print(HELP.format(maxnum=len(SETTINGS)))
        elif cmd[0] == 'x':
            if len(cmd) < 2:
                print("Need numbers of entries to delete")
                continue
            try:
                nums = map(int, cmd[1:])
            except ValueError:
                print("Need numbers of entries to delete")
                continue
            else:
                for num in nums:
                    set_by_num(values, num, None)
        else:
            try:
                num = int(cmd[0])
            except ValueError:
                print("Don't understand option {!r}".format(cmd[0]))
                continue
            else:
                if len(cmd) >= 2:
                    set_by_num(values, num, " ".join(cmd[1:]))
                else:
                    if get_by_num(values, num):
                        value = None
                    else:
                        value = '1'
                    set_by_num(values, num, value)
        show = True

    return values

def as_exports(values):
    exports = []
    for name, value in values.items():
        if value is None:
            exports.append("typeset +x {}".format(name))
        else:
            exports.append("export {}={!r}".format(name, value))
    return "eval " + "; ".join(exports)

def main(args):
    # All output has to go to stderr. Stdout will be executed.
    with contextlib.redirect_stdout(sys.stderr):
        find_settings(args)
        exports = as_exports(get_new_values(read_them()))
    print(exports)

if __name__ == '__main__':
    main(sys.argv[1:])
