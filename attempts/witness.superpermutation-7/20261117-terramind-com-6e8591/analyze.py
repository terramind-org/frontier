"""Parse a superpermutation into its permutation path and edge weights; report weight counts and 1-/2-cycle structure."""
import json, sys
from collections import Counter

def perm_path(word, n=7):
    path, pos = [], []
    for k in range(len(word) - n + 1):
        w = word[k:k + n]
        if len(set(w)) == n:
            path.append(w); pos.append(k)
    return path, pos

def overlap_weight(a, b):
    n = len(a)
    for k in range(1, n + 1):
        if a[k:] == b[:n - k]:
            return k
    return n

def main():
    word = json.load(open(sys.argv[1]))['word']
    path, pos = perm_path(word)
    print('length', len(word), 'perm windows', len(path), 'distinct', len(set(path)))
    w = [pos[i + 1] - pos[i] for i in range(len(path) - 1)]
    print('sum of position steps + 7 =', sum(w) + 7)
    print('step weights:', sorted(Counter(w).items()))
    # direct overlap weights between consecutive perms (should equal the steps when no repeats)
    dw = [overlap_weight(path[i], path[i + 1]) for i in range(len(path) - 1)]
    print('direct weights:', sorted(Counter(dw).items()), 'mismatch', sum(1 for a, b in zip(w, dw) if a != b))
    heavy = [i for i, x in enumerate(w) if x >= 3]
    print('weight>=3 edges at path indices (first 40):', heavy[:40])
    # 1-cycle runs: maximal runs of weight-1 steps
    runs, cur = [], 1
    for x in w:
        if x == 1: cur += 1
        else: runs.append(cur); cur = 1
    runs.append(cur)
    print('weight-1 run lengths:', sorted(Counter(runs).items()))
    # 2-cycles: segments between weight>=3 steps
    seg, cur = [], 1
    for x in w:
        if x <= 2: cur += 1
        else: seg.append(cur); cur = 1
    seg.append(cur)
    print('runs between weight>=3 steps (perm counts):', sorted(Counter(seg).items()))

if __name__ == '__main__':
    main()
