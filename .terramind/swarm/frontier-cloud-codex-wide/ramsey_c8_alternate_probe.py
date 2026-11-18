#!/usr/bin/env python3
"""Select a degree-sequence-proven nonisomorphic 42-vertex g6 seed."""
import hashlib, json, sys
from itertools import combinations

def g6(line):
    n = ord(line[0]) - 63
    assert n == 42
    bits = [(ord(c) - 63 >> s) & 1 for c in line[1:] for s in range(5, -1, -1)]
    a = [[0] * n for _ in range(n)]; k = 0
    for i in range(1, n):
        for j in range(i): a[i][j] = a[j][i] = bits[k]; k += 1
    return a
def rows(a): return ["".join(map(str, r)) for r in a]
def good(a):
    return not any(len({a[i][j] for i, j in combinations(s, 2)}) == 1 for s in combinations(range(42), 5))
def main():
    exoo = [[int(x) for x in line.strip()] for line in open(sys.argv[1]) if line.strip()]
    want = sorted(map(sum, exoo)); data = [x.strip() for x in open(sys.argv[2]) if x.strip()]
    out = {"source_sha256": hashlib.sha256(open(sys.argv[2], "rb").read()).hexdigest(),
           "graphs_in_source": len(data), "exoo_degree_sequence": want}
    for line_no, line in enumerate(data):
        a = g6(line); deg = sorted(map(sum, a))
        if deg != want:
            assert good(a)
            out.update({"selected_line": line_no, "selected_g6": line,
                        "selected_degree_sequence": deg, "k5_free": True,
                        "nonisomorphism_certificate": "degree sequences differ"})
            open(sys.argv[3], "w").write("\n".join(rows(a)) + "\n")
            break
    else: raise RuntimeError("no degree-sequence-distinct graph found")
    json.dump(out, open(sys.argv[4], "w"), indent=2, sort_keys=True); print(json.dumps(out, sort_keys=True))
if __name__ == "__main__": main()
