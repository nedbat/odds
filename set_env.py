#!/usr/bin/env python3
#
# Run this like:
#
#   $ $(set_env.py)
#
# It looks through files in your tree for lines like this:
#
#   # $set_env.py: ENVVAR_NAME - Description of the environment variable.
#
# and prompts for values.  You can review, change, or delete values.

import functools
import glob
import itertools
import os
import re
import sys

# Because of the way this tool is run, all user-visible output has to go to
# stderr.  At the end, shell commands will be written to stdout.  To make this
# convenient, we redefine print as stderr.
pstdout = print
print = functools.partial(print, file=sys.stderr)

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

def set_by_num(values, n, value):
    setting_name = SETTINGS[int(n)-1][0]
    values[setting_name] = value

PROMPT = "(# value | x # | q) ::> "

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
        if cmd[0] == 'q':
            break
        if cmd[0] == 'x':
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
                    print("Need a value to set")
                    continue
        show = True

    return values

def as_exports(values):
    exports = []
    for name, value in values.items():
        if value is None:
            exports.append("export -n {}".format(name))
        else:
            exports.append("export {}={!r}".format(name, value))
    return "eval " + "; ".join(exports)

def main(args):
    find_settings(args)
    pstdout(as_exports(get_new_values(read_them())))

if __name__ == '__main__':
    main(sys.argv[1:])
