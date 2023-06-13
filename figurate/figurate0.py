import itertools

def intersect_monotonic_sequences(*seqs):
    """Find numbers that appear in all sequences.

    `seqs` must be monotonic integer sequences.
    """
    # A list of lists.  First element is the latest number
    # from the sequence, third element is the sequence.
    # Second element is a tie-breaker so we don't try to 
    # compare the sequences themselves when sorting.
    work = [[next(seq), i, seq] for i, seq in enumerate(seqs)]
    work.sort()
    # v0 is the smallest value we've gotten from any sequence.
    v0 = work[0][0]
    while True:
        # If all of the sequences produced the same number,
        # we found what we're looking for.
        if all(item[0] == v0 for item in work):
            print(f"{v0:,}")
        # Sort the work so we look at the smallest number next.
        work.sort()
        v0 = work[0][0] = next(work[0][2])


# Centered number formulas

def centered_4(n):
    return n**2 + (n - 1)**2

def centered_6(n):
    return n**3 - (n - 1)**3

def centered_10(n):
    return 5 * n**2 - 5 * n + 1

intersect_monotonic_sequences(
    map(centered_4, itertools.count(1)),
    map(centered_6, itertools.count(1)),
    map(centered_10, itertools.count(1)),
)
