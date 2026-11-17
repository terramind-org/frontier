"""Known-answer test of the equal-size move mode of mclq (run 2026-11-17T20:27Z, during the search, from the scratch
directory). Puncture the 604 at one vector r; in the cap of 30 members of X around r (r's slot counted as free) a
30-set different from the current one must exist (swap a member for r); the move mode must find it."""
import sys; sys.path.insert(0, 'src')
from lns import *
fs = FreeSet('reps_mixedB.txt')
ext = [i for i, v in enumerate(V604) if any(v[1::2])]
for r in (ext[7], 100):
    X = [v for i, v in enumerate(V604) if i != r]
    R = cap(X, as_float([V604[r]])[0], 30)
    Rp = {IDX[v] for v in R} | {r}
    cand = fs.query(Rp, [])
    cur = {i for i, v in enumerate(cand) if v in set(R)}
    st, val, ch, nodes, ne, ts = clique(cand, 30, 1, excl=cur, seed=5, tl=30)
    chosen = [cand[i] for i in ch]
    ok = exact_valid([v for v in X if v not in set(R)] + chosen)
    print(f'{utc()} CALIB move-mode removed={r} free={len(cand)} status={st} size={len(ch)} differs={set(chosen) != set(R)} exact={ok}')
fs.close()
