"""Known-answer calibration: puncture the 604 (1 extension vector, 1 backbone vector, 3 scattered vectors) and
require (a) the LNS cap solve and (b) a blocker-set style solve around the hole left by a removed vector to restore
604 exactly; also a broken copy must be rejected by the exact checker."""
import sys, os, time
sys.path.insert(0, 'src')
from lns import *
log = open('logs/calibrate.log', 'a')
os.makedirs('calib', exist_ok=True)
def P(s): print(f'{utc()} {s}', file=log, flush=True); print(s, flush=True)
X = V604
ok, why = exact_valid(X); P(f'baseline exact_valid {ok} {why}')
bad = list(X); bad[603] = bad[0]
ok2, why2 = exact_valid(bad); P(f'broken copy (vector 603 := vector 0) exact_valid {ok2} {why2}')
bad2 = list(X); v = list(bad2[5]); v[0] -= 1; bad2[5] = tuple(v)
P(f'broken copy (one coordinate changed) exact_valid {exact_valid(bad2)}')
fs = FreeSet(sys.argv[1])
ext = [i for i, v in enumerate(X) if any(v[1::2])]
back = [i for i, v in enumerate(X) if not any(v[1::2])]
cases = [('p1-ext', [ext[7]]), ('p1-back', [back[100]]), ('p3', [ext[50], back[3], back[400]])]
for name, rem in cases:
    for m in (30, 50):
        s = Search(fs, log, 'calib', gone=rem)
        start = len(s.X())
        # one cap per removed vector, centred on the removed vector's direction (the hole it leaves)
        for r in rem:
            Rset = cap(s.X(), as_float([V604[r]])[0], m)
            res = s.solve_nbhd(Rset, f'calib-{name}-m{m}-cap-at-{r}', tl=60, move=False)
        P(f'CALIB {name} m={m}: start {start} -> {len(s.X())} restored={len(s.X()) == 604} exact={exact_valid(s.X())}')
    # blocker-set form: R = every member of X with cosine >= 1/2 - 1e-9 to the removed vector, i.e. what blocks it
    s = Search(fs, log, 'calib', gone=rem)
    for r in rem:
        F = as_float(s.X()); c = as_float([V604[r]])[0]
        R = [v for v, cs in zip(s.X(), F @ c / 36.0) if cs >= 0.5 - 1e-9]
        s.solve_nbhd(R, f'calib-{name}-blockers-of-{r}', tl=60, move=False)
    P(f'CALIB {name} blocker-form: -> {len(s.X())} restored={len(s.X()) == 604}')
save('calib/restored.json', s.X(), 'calibration restore')
fs.close()
