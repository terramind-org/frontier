"""Own sum-free checker (written for this task). Usage: check.py file [K]. Files: JSON {"colors": [...]} or text of ints."""
import json, sys
def load_any(p):
    t = open(p).read().strip()
    if t.startswith('{'): return json.loads(t)['colors']
    return [int(x) for x in t.split()]
def count_viol(cols, K=None):
    n = len(cols); cls = {}
    for i, c in enumerate(cols): cls.setdefault(c, []).append(i + 1)
    bad = 0
    for c, mem in cls.items():
        s = set(mem)
        for i, a in enumerate(mem):
            for b in mem[i:]:
                if a + b > n: break
                if a + b in s: bad += 1
    rng = bad if K is None else bad + sum(1 for c in cols if not (0 <= c < K))
    return rng
def mirror_mismatch(cols, Ssum):
    n = len(cols); return sum(1 for x in range(1, n + 1) if 1 <= Ssum - x <= n and x < Ssum - x and cols[x-1] != cols[Ssum-x-1])
if __name__ == '__main__':
    cols = load_any(sys.argv[1]); K = int(sys.argv[2]) if len(sys.argv) > 2 else None
    print('N', len(cols), 'colours', sorted(set(cols)), 'violations', count_viol(cols, K))
