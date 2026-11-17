"""Known-answer calibration for the schur7-r2 encoder and solver wrapper. Writes logs/calib.jsonl."""
import json, random, sys
from schur import *
log = open('logs/calib.jsonl', 'a')
def rec(name, out, expect):
    o = {k: v for k, v in out.items() if k != 'cols'}
    o.update(name=name, expect=expect, utc=utc(), passed=(out['status'] == expect))
    if 'cols' in out:
        o['violations'] = len(violations(out['cols']))
        o['passed'] = o['passed'] and o['violations'] == 0
    print(json.dumps(o), flush=True); log.write(json.dumps(o) + '\n'); log.flush()
    return out
base = load('baseline.json')
# checker
broken = list(base); broken[1] = broken[0]
print('checker baseline', len(violations(base)), 'broken', len(violations(broken)), flush=True)
log.write(json.dumps(dict(name='checker', baseline=len(violations(base)), broken=len(violations(broken)), utc=utc())) + '\n')
save('broken.json', broken)
# small known answers (no symmetry breaking, all free)
rec('K3_N13', solve(Instance(13, 3), 60), 'SAT')
rec('K3_N14', solve(Instance(14, 3), 60), 'UNSAT')
rec('K4_N44', solve(Instance(44, 4), 120), 'SAT')
rec('K4_N45', solve(Instance(45, 4), 400), 'UNSAT')
# Rowley mode at 1696: base 1..536 fixed, 537 colour 6, mirror x -> 1697 - x; no phases
o = rec('rowley_base_mirror_1696', solve(rowley_modes(1696, base[:536], mirror_S=1697), 300), 'SAT')
if 'cols' in o: save('calib_rowley1696.json', o['cols']); print('diff from baseline', sum(a != b for a, b in zip(o['cols'], base)))
# planted: free 300 random positions of the middle without phases, must refill
rnd = random.Random(1)
free = set(rnd.sample(range(537, 1161), 300))
fixed = {x: base[x - 1] for x in range(1, 1697) if x not in free}
o = rec('planted_free300_1696', solve(Instance(1696, 7, fixed=fixed), 300), 'SAT')
if 'cols' in o: save('calib_planted.json', o['cols'])
# 3-divisibility: full mirror x -> 1698 - x at N = 1697 forces 566 + 566 = 1132 monochromatic
o = rec('full_mirror_1698_N1697_free', solve(Instance(1697, 7, mirrors=[(x, 1698 - x) for x in range(1, 849)]), 60), 'UNSAT')
