import dataclasses
import itertools
import sys
import time
from typing import Callable

class OnceEvery:
    """An object whose .now() method is true once every N seconds."""
    def __init__(self, seconds):
        self.delta = seconds
        self.last_true = 0

    def now(self):
        right_now = time.time()
        ret = right_now - self.last_true >= self.delta
        if ret:
            self.last_true = right_now
        return ret

@dataclasses.dataclass
class WorkItem:
    """One unit of a sequence in progress."""
    result: int
    fn: Callable[[int], int]
    n: int
    
    def __lt__(self, other):
        return self.result < other.result

def n_values(fns, work):
    """Get the values of n, but in the order of the functions."""
    original_order = sorted(work, key=lambda w: fns.index(w.fn))
    ns = " ".join(str(w.n) for w in original_order)
    return ns


PRINT_EVERY = int(1e14)
PRINT_PAUSE = 1

def intersect_monotonic_sequences(starts, fns):
    blanks = " " * 30
    work = sorted(WorkItem(fn(start), fn, start) for start, fn in zip(starts, fns))
    result0 = work[0].result
    upto = (result0 // PRINT_EVERY) * PRINT_EVERY
    last_shown = result0
    should_print = OnceEvery(PRINT_PAUSE)
    try:
        while True:
            if result0 > upto:
                if should_print.now():
                    ns = n_values(fns, work)
                    print(f"  -> {result0:,};  \u0394={result0 - last_shown:.1e};  ns = {ns}{blanks}", end="\r")
                    last_shown = result0
                upto += PRINT_EVERY
            if result0 == work[1].result and all(w.result == result0 for w in work):
                ns = n_values(fns, work)
                print(f"{result0:,}; ns = {ns}{blanks}")
            work.sort()
            work[0].n = next_n = work[0].n + 1
            result0 = work[0].result = work[0].fn(next_n)
    except KeyboardInterrupt:
        print("\n")
        raise

def centered_4(n):
    return n**2 + (n - 1)**2

def centered_6(n):
    return n**3 - (n - 1)**3

def centered_10(n):
    return 5 * n**2 - 5 * n + 1

fns = [
    centered_4,
    centered_6,
    centered_10,
]

if len(sys.argv) > 1:
    starts = list(map(int, sys.argv[1:]))
    assert len(starts) == len(fns)
else:
    starts = [1] * len(fns)

intersect_monotonic_sequences(starts, fns)
