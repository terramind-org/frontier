"""Push line (core 2) of the schur7-r2 search: climb N above the best verifier-accepted value.

State: cur = largest N with a saved valid colouring; pool = (name, base 1..536, colouring) of bases that reached cur.
Each round, for target N in cur+1 .. cur+3 and a pool base, try (all with 537 -> colour 6, colour 6 kept off 1..536):
  symN    - base fixed, mirror x -> N+1-x on all of 1..N (only when N+1 is not 0 mod 3: if N+1 = 3t then t + t = 2t
            = N+1-t is forced monochromatic);
  softN_F - base fixed on 1..F only (F in 450, 400, 300), 1..536 otherwise free, mirror x -> N+1-x;
  nearN   - when N+1 = 3t: as symN but without the mirror pairs (t, 2t+1)...: the mirror is dropped for x in
            [t - W, t + W] and their images (W = 40), everything else mirrored;
  freeN   - base fixed on 1..536, everything above free, no mirror (longer limit).
A round with no SAT generates new pool bases by freeing part of a pool base and solving the symmetric (or near-
symmetric) instance at cur with random seeds, so each new base reaches cur by construction.
Every call -> logs/push.jsonl (status, rc, seconds, conflicts). Every SAT colouring is saved and checked.
usage: push.py DEADLINE SEED START.json [START.json ...]
"""
import json, os, random, sys, time
from schur import *

DEADLINE, SEED = float(sys.argv[1]), int(sys.argv[2])
rnd = random.Random(SEED)
os.makedirs('push', exist_ok=True); os.makedirs('best', exist_ok=True)
LOG = open('logs/push.jsonl', 'a')
def log(**kw):
    kw['utc'] = utc(); kw = {k: v for k, v in kw.items() if k != 'cols'}
    LOG.write(json.dumps(kw) + '\n'); LOG.flush(); print(json.dumps(kw), flush=True)

pool = []
for p in sys.argv[3:]:
    c = load(p); assert not violations(c)
    pool.append((os.path.basename(p)[:-5], c[:536], c))
cur = max(len(c) for _, _, c in pool)
pool = [x for x in pool if len(x[2]) == cur]
seen = {tuple(b) for _, b, _ in pool}

def mirror_pairs(N, skip=()):
    return [(x, N + 1 - x) for x in range(1, (N + 1) // 2 + 1) if x != N + 1 - x and x not in skip and N + 1 - x not in skip]

def structural(N, base, F, mirror=True, W=40, m=536, pivot=True):
    """base fixed on 1..F, colour 6 forbidden on 1..m (and their mirror images), 537 -> 6 if pivot."""
    fixed = {i + 1: base[i] for i in range(F)}
    if pivot: fixed[537] = 6
    forbid = {x: {6} for x in range(F + 1, m + 1)}
    mir = []
    if mirror:
        skip = set()
        if (N + 1) % 3 == 0:
            t = (N + 1) // 3
            skip = set(range(t - W, t + W + 1))
        mir = mirror_pairs(N, skip)
    return Instance(N, 7, mirrors=mir, fixed=fixed, forbid=forbid)

def attempt(N, name, base, mode, inst, tl):
    o = solve_bin(inst, min(tl, max(1, DEADLINE - time.time())), seed=rnd.randrange(1 << 30), tag='push')
    extra = {}
    if o['status'] == 'SAT':
        v = len(violations(o['cols'])); extra['violations'] = v
        path = f'push/{name}_{mode}_N{N}.json'; save(path, o['cols']); extra['saved'] = path
        if v == 0:
            save(f'best/N{N}_{name}_{mode}.json', o['cols'])
    log(event='TRY', N=N, base=name, mode=mode, **o, **extra)
    return o

def modes_for(N, base, colr):
    out = []
    tag = 'sym' if (N + 1) % 3 else 'near'
    out.append((tag, structural(N, base, 536), 45))
    for F, m in ((300, 450), (200, 350), (150, 300)):
        out.append((f'{tag}_F{F}_m{m}', structural(N, base, F, m=m, pivot=False), 75))
    # non-mirrored top windows of the pool colouring: 1..len-w fixed, the rest and the new integers free
    for w in (300, 500, 700, 900):
        L = len(colr)
        out.append((f'win{w}', Instance(N, 7, fixed={x: colr[x - 1] for x in range(1, L - w + 1)}), 60))
    out.append(('free', Instance(N, 7, fixed={i + 1: base[i] for i in range(536)}), 90))
    return out

def gen_base():
    global gen
    gen += 1
    sname, sbase, scol = rnd.choice(pool)
    f = rnd.choice([0.1, 0.2, 0.35, 0.5])
    freed = set(x for x in range(1, 537) if rnd.random() < f)
    fixed = {x: sbase[x - 1] for x in range(1, 537) if x not in freed}
    inst = structural(cur, [0] * 536, 0)
    inst.fixed.update(fixed)
    o = solve_bin(inst, 60, seed=rnd.randrange(1 << 30), tag='pgen')
    rec = dict(event='GEN', src=sname, frac=f, nfree=len(freed), N=cur)
    if o['status'] == 'SAT' and not violations(o['cols']):
        nb = o['cols'][:536]
        if tuple(nb) in seen:
            log(**rec, dup=True, **o); return None
        seen.add(tuple(nb))
        nname = f'p{SEED}_{gen:04d}'
        save(f'push/{nname}_N{cur}.json', o['cols'])
        pool.append((nname, nb, o['cols']))
        log(**rec, base=nname, ham_src=sum(a != b for a, b in zip(nb, sbase)), **o)
        return pool[-1]
    log(**rec, **o)
    return None

log(event='START', seed=SEED, cur=cur, pool=[n for n, _, _ in pool])
gen = 0
while time.time() < DEADLINE - 20:
    improved = False
    fresh = None
    for _ in range(4):
        if time.time() > DEADLINE - 20: break
        fresh = gen_base() or fresh
        if fresh: break
    name, base, colr = fresh or rnd.choice(pool)
    for N in range(cur + 1, cur + 3):
        for mode, inst, tl in modes_for(N, base, colr):
            if time.time() > DEADLINE - 20: break
            o = attempt(N, name, base, mode, inst, tl)
            if o['status'] == 'SAT' and not violations(o['cols']):
                cur = N; pool = [(name, base, o['cols'])]; improved = True
                log(event='NEW_BEST', N=N, base=name, mode=mode)
                break
        if improved: break
log(event='END', cur=cur)
