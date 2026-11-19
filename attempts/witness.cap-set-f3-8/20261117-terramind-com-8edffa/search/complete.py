"""Completeness analysis: how many lines through set points each outside point would complete."""
import sys, collections
import numpy as np
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from capcore import *

idx = load_points(sys.argv[1])
assert is_cap(idx), "not a cap"
cnt = block_counts(idx)
inset = np.zeros(M, bool); inset[idx] = True
out = cnt[~inset]
print("set size", len(idx), "outside", len(out))
print("min count", out.min(), "points with count 0:", int((out == 0).sum()))
d = collections.Counter(out.tolist())
print("distribution (count: number of outside points):", dict(sorted(d.items())))
# points with count 1: the blocking pair
T = third_table()
ones = np.nonzero((~inset) & (cnt == 1))[0]
print("count-1 points:", len(ones))
