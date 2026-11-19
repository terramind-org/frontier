"""Large-neighbourhood search on a superpermutation's permutation path with LKH-3.

Repeatedly cut a segment of the path (chosen around a weight>=3 edge), keep both ends fixed and re-solve the
segment as an asymmetric TSP path with LKH (the two fixed ends are merged into one node, so a tour is a path).
Accept equal-or-better segments (drift across plateaus); write every strictly shorter word to disk.

Usage: python3 -I lns_lkh.py <baseline.json> <lkh-binary> <workdir> <seconds> <seed>
"""
import json, os, random, subprocess, sys, time

N = 7

def overlap_weight(a, b):
    for k in range(1, N + 1):
        if a[k:] == b[:N - k]:
            return k
    return N

def perm_path(word):
    return [word[k:k + N] for k in range(len(word) - N + 1) if len(set(word[k:k + N])) == N]

def path_word(path):
    out = [path[0]]
    for a, b in zip(path, path[1:]):
        w = overlap_weight(a, b)
        out.append(b[N - w:])
    return ''.join(out)

def solve_segment(seg, lkh, wd, seed, time_limit):
    """seg[0] and seg[-1] fixed. Returns (new_seg, cost) or None."""
    s, t = seg[0], seg[-1]
    inner = seg[1:-1]
    nodes = ['X'] + inner                 # node 0 = merged ends
    k = len(nodes)
    def cost(i, j):
        if i == j:
            return 0
        a = s if i == 0 else nodes[i]
        b = t if j == 0 else nodes[j]
        return overlap_weight(a, b)
    rows = []
    for i in range(k):
        rows.append(' '.join(str(cost(i, j)) for j in range(k)))
    prob = os.path.join(wd, 'seg.atsp')
    with open(prob, 'w') as f:
        f.write(f'NAME: seg\nTYPE: ATSP\nDIMENSION: {k}\nEDGE_WEIGHT_TYPE: EXPLICIT\nEDGE_WEIGHT_FORMAT: FULL_MATRIX\nEDGE_WEIGHT_SECTION\n')
        f.write('\n'.join(rows)); f.write('\nEOF\n')
    init = os.path.join(wd, 'init.tour')
    with open(init, 'w') as f:
        f.write(f'TYPE: TOUR\nDIMENSION: {k}\nTOUR_SECTION\n')
        f.write('\n'.join(str(i + 1) for i in range(k))); f.write('\n-1\nEOF\n')
    out = os.path.join(wd, 'out.tour')
    if os.path.exists(out):
        os.remove(out)
    par = os.path.join(wd, 'seg.par')
    with open(par, 'w') as f:
        f.write(f'PROBLEM_FILE = {prob}\nINITIAL_TOUR_FILE = {init}\nOUTPUT_TOUR_FILE = {out}\nRUNS = 1\n'
                f'MAX_TRIALS = {k}\nTIME_LIMIT = {time_limit}\nSEED = {seed}\nTRACE_LEVEL = 0\nMOVE_TYPE = 5\n'
                f'MAX_CANDIDATES = 8\n')
    subprocess.run([lkh, par], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=time_limit * 3 + 60)
    if not os.path.exists(out):
        return None
    tour = []
    with open(out) as f:
        sec = False
        for line in f:
            line = line.strip()
            if line == 'TOUR_SECTION':
                sec = True; continue
            if sec:
                v = int(line)
                if v == -1:
                    break
                tour.append(v - 1)
    z = tour.index(0)
    tour = tour[z:] + tour[:z]
    new = [s] + [nodes[i] for i in tour[1:]] + [t]
    return new

def seg_cost(seg):
    return sum(overlap_weight(a, b) for a, b in zip(seg, seg[1:]))

def main():
    base, lkh, wd, seconds, seed = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), int(sys.argv[5])
    os.makedirs(wd, exist_ok=True)
    rng = random.Random(seed)
    path = perm_path(json.load(open(base))['word'])
    assert len(path) == 5040 and len(set(path)) == 5040
    total = seg_cost(path)
    best = N + total
    print(f'start length {best}', flush=True)
    t0 = time.time(); it = 0
    while time.time() - t0 < seconds:
        it += 1
        heavy = [i for i in range(len(path) - 1) if overlap_weight(path[i], path[i + 1]) >= 3]
        c = rng.choice(heavy)
        K = rng.randint(200, 1200)
        i = max(0, c - rng.randint(0, K)); j = min(len(path) - 1, i + K)
        seg = path[i:j + 1]
        old = seg_cost(seg)
        new = solve_segment(seg, lkh, wd, rng.randint(1, 10**9), 60)
        if new is None or sorted(new) != sorted(seg):
            print(f'it {it} [{i},{j}] lkh failed', flush=True); continue
        nc = seg_cost(new)
        if nc <= old:
            path = path[:i] + new + path[j + 1:]
        L = N + seg_cost(path)
        print(f'it {it} t {time.time()-t0:.0f}s seg [{i},{j}] K {j-i+1} old {old} new {nc} length {L} heavy {len(heavy)}', flush=True)
        if L < best:
            best = L
            w = path_word(path)
            fn = os.path.join(wd, f'cand_{L}.json')
            json.dump({'word': w}, open(fn, 'w'))
            print(f'NEW BEST {L} written {fn}', flush=True)
    print(f'end best {best} iterations {it}', flush=True)

if __name__ == '__main__':
    main()
