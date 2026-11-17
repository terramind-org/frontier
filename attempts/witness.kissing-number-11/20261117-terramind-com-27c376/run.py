"""Main search (one process, one core): stage 1 blocker-set exchanges for every numerical hole class (blockers and
wider shells), stage 2 exchanges around low-conflict pool vectors, stage 3 free-backbone LNS walk with caps that grow
over the run and equal-size moves. Every neighbourhood solve is exact (max clique of the compatibility graph of all
pool vectors compatible with the fixed part). Any configuration larger than 604 is saved and exact-checked at once.
Usage: run.py <reps file> <budget seconds> <seed>"""
import sys, os, json, time, random
sys.path.insert(0, os.path.dirname(__file__))
from lns import *
reps, budget, seed = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
walk_only = len(sys.argv) > 4 and sys.argv[4] == 'walk'  # second process: stage 3 only, own log files
tag = '' if not walk_only else f'-walk{seed}'
T0 = time.time()
rng = random.Random(seed); nrng = np.random.default_rng(seed)
OUT = 'out' if not walk_only else f'out-walk{seed}'
os.makedirs(OUT, exist_ok=True)
log = open(f'logs/run{tag}.log', 'a')
rec = open(f'logs/run{tag}-records.jsonl', 'a')
fs = FreeSet(reps)
S = Search(fs, log, OUT)
def left(): return budget - (time.time() - T0)
def P(s): S.p(s)
stats = {'solves': 0, 'optimal': 0, 'timeout': 0, 'error': 0, 'improved': 0, 'moves': 0}
def run_nbhd(R, label, tl=60.0, move=False):
    res = S.solve_nbhd(R, label, tl=tl, move=move, seed=rng.randrange(1 << 30))
    res['t'] = round(time.time() - T0, 1); res['X'] = len(S.X()); res['distinct_states'] = len(S.visited)
    rec.write(json.dumps(res) + '\n'); rec.flush()
    stats['solves'] += 1
    st = res['status']
    stats['optimal' if st == 'OPTIMAL' else 'timeout' if st == 'TIMEOUT' else 'error'] += 1
    if res.get('improved'):
        stats['improved'] += 1
        X = S.X(); save(f'{OUT}/candidate-{len(X)}.json', X, 'exact configuration from lns run.py')
        P(f'CANDIDATE {len(X)} saved {OUT}/candidate-{len(X)}.json: run bun frontier diagnose on it')
    if res.get('moved'): stats['moves'] += 1
    return res
P(f'START run.py reps={reps} budget={budget}s seed={seed}')
# ---- stage 1: blocker-set exchanges
H = json.load(open('holes.json'))
P(f'STAGE1 blocker-set exchanges over {len(H)} hole classes')
for hi, h in enumerate([] if walk_only else H):
    if left() < budget * 0.75: break
    X = S.X(); F = as_float(X) / 6.0; x = np.array(h['x'])
    c = F @ x; mc = c.max()
    for delta in (1e-7, 0.01, 0.03, 0.06, 0.1):
        R = [X[i] for i in np.nonzero(c >= mc - delta)[0]]
        res = run_nbhd(R, f'hole{hi}-maxcos{mc:.5f}-delta{delta}', tl=90)
        if res['free'] > 20000 or res['status'] != 'OPTIMAL': break
    P(f'hole class {hi} done')
# ---- stage 2: exchanges around low-conflict pool vectors (conflict set plus growing cap around the vector)
low = []
with open(reps) as f:
    for line in f:
        t = line.split()
        nc = int(t[23])
        if 2 <= nc <= 12:
            low.append((nc, tuple(int(a) for a in t[:22])))
low.sort()
P(f'STAGE2 {len(low)} low-conflict orbit representatives (2..12 conflicts)')
for nc, v in ([] if walk_only else low):
    if left() < budget * 0.6: break
    X = S.X()
    for m in (nc, 20, 40, 55, 65, 75):
        if m < nc: continue
        R = cap(X, as_float([v])[0], m)
        res = run_nbhd(R, f'lowconf{nc}-m{m}', tl=60)
        if res['free'] > 15000 or res['status'] != 'OPTIMAL': break
# ---- stage 3: LNS walk
P('STAGE3 LNS walk')
freemax = 4000; it = 0
while left() > 60:
    it += 1
    X = S.X()
    kind = rng.choice(['member', 'member', 'random', 'hole'])
    if kind == 'member':
        c = as_float([rng.choice(X)])[0]
    elif kind == 'random':
        c = nrng.normal(size=11)
    else:
        c = np.array(rng.choice(H)['x'])
    m = 50 if not walk_only else rng.choice([55, 60, 65, 70])
    last = None
    while True:
        R = cap(X, c, m)
        tl = min(120.0, max(10.0, left() - 30))
        res = run_nbhd(R, f'walk{it}-{kind}-m{m}', tl=tl, move=True)
        if res.get('improved') or res.get('moved'): break
        if res['status'] != 'OPTIMAL' or res['free'] > freemax: break
        m += 5
        if left() < 60: break
    if it % 10 == 0:
        el = time.time() - T0
        freemax = int(4000 + 16000 * min(1.0, el / budget))
        P(f'PROGRESS it={it} elapsed={el:.0f}s X={len(S.X())} best={S.best} distinct_states={len(S.visited)} E={len(S.E)} stats={stats} freemax={freemax}')
P(f'END elapsed={time.time()-T0:.0f}s best={S.best} distinct_states={len(S.visited)} stats={stats}')
json.dump({'best': S.best, 'distinct_states': len(S.visited), 'stats': stats, 'elapsed': time.time() - T0}, open(f'logs/run{tag}-summary.json', 'w'))
save(f'{OUT}/final-state.json', S.X(), 'final LNS state')
fs.close()
