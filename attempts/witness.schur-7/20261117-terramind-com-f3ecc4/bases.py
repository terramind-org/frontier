"""Many-bases line (core 1) of the schur7-r2 search.

Loop until the deadline:
  1. Generate a new 6-colour sum-free base of 1..536 (or keep only 1..m of a source and free m+1..536) by a SAT
     call that frees part of a source base, forces at least D changes among the freed positions, and uses random
     phases. Generator kinds:
       joint   - solved jointly with Rowley's mirrored 1696 structure (so the base reproduces 1696 by construction);
       alone   - a 6-colour partition of 1..536 only (Rowley's round-1 gap: does an arbitrary base reproduce 1696?).
  2. Validate: fix the base, 537 -> colour 6, mirror x -> 1697 - x, solve the middle 538..1159 at N = 1696.
     SAT must come back and the decoded colouring must have 0 violations (saved for `bun frontier diagnose`).
  3. Only for passing bases, attempt:
       shift1697  - N = 1697, base and 537 mirrored by x -> 1698 - x onto 1161..1697, middle 538..1160 free;
       sym1698    - N = 1698, fully symmetric x -> 1699 - x (Rowley's method one order up; 1699 is not 0 mod 3);
       free1697   - N = 1697, base fixed, everything above 536 free, no mirror;
       partial1697- N = 1697, base fixed, 537 -> 6, mirror x <-> 1698 - x for 567..848 only, 1132..1697 free.
     (Full mirror x -> 1698 - x at N = 1697 is impossible: 566 + 566 = 1132 = 1698 - 566; calibrated.)
Every call is logged to logs/bases.jsonl with status, seconds, conflicts; every SAT colouring is saved.
"""
import json, os, random, sys, time
from schur import *

DEADLINE = float(sys.argv[1])          # unix time
SEED = int(sys.argv[2])
rnd = random.Random(SEED)
os.makedirs('bases', exist_ok=True); os.makedirs('sols', exist_ok=True)
LOG = open('logs/bases.jsonl', 'a')
T_VALID, T_MODE = 90, 75

def log(**kw):
    kw['utc'] = utc()
    kw = {k: v for k, v in kw.items() if k != 'cols'}
    LOG.write(json.dumps(kw) + '\n'); LOG.flush(); print(json.dumps(kw), flush=True)

rowley = load('baseline.json')
bases = {}            # tuple(base) -> name
sources = [('rowley', rowley)]   # valid symmetric 1696 colourings usable as sources
bases[tuple(rowley[:536])] = 'rowley'

def rand_phases(inst):
    return [l if rnd.random() < 0.5 else -l for l in range(1, inst.nvars + 1)]

def differ_clauses(inst, src, positions, D, top):
    """at least D of `positions` take a colour different from src: atleast-D over literals -v(x, src[x])."""
    from pysat.card import CardEnc, EncType
    lits = [-inst.v(x, src[x - 1]) for x in positions]
    D = min(D, len(lits))
    enc = CardEnc.atleast(lits=lits, bound=D, top_id=top, encoding=EncType.seqcounter)
    return enc.clauses

def gen_joint(src, kind):
    """Symmetric 1696 colouring with Rowley structure, part of src's base freed."""
    if kind == 'frac':
        f = rnd.choice([0.2, 0.35, 0.5, 0.7, 1.0])
        freed = sorted(x for x in range(1, 537) if rnd.random() < f)
        desc = f'frac{f}'
    elif kind == 'window':
        L = rnd.choice([60, 120, 200, 300]); a = rnd.randint(1, 537 - L)
        freed = list(range(a, a + L)); desc = f'window{a}-{a+L-1}'
    else:  # short base: keep 1..m, free m+1..536
        m = rnd.choice([300, 350, 400, 450, 500]); freed = list(range(m + 1, 537)); desc = f'short{m}'
    fs = set(freed)
    fixed = {x: src[x - 1] for x in range(1, 537) if x not in fs}
    fixed[537] = 6
    forbid = {x: {6} for x in fs}
    inst = Instance(1696, 7, mirrors=[(x, 1697 - x) for x in range(1, 849)], fixed=fixed, forbid=forbid)
    D = max(1, min(len(freed) // 4, rnd.choice([10, 25, 50, 100, 150])))
    extra = differ_clauses(inst, src, freed, D, inst.nvars)
    o = solve_bin(inst, T_VALID, seed=rnd.randrange(1 << 30), extra=extra, tag='gen')
    return o, desc, D, len(freed)

def gen_alone(src):
    """6-colour sum-free partition of 1..536 differing from src in >= D of a freed window/fraction."""
    f = rnd.choice([0.3, 0.5, 1.0])
    freed = sorted(x for x in range(1, 537) if rnd.random() < f)
    fs = set(freed)
    inst = Instance(536, 6, fixed={x: src[x - 1] for x in range(1, 537) if x not in fs})
    D = rnd.choice([20, 50, 100])
    extra = differ_clauses(inst, src, freed, D, inst.nvars)
    o = solve_bin(inst, 60, seed=rnd.randrange(1 << 30), extra=extra, tag='gen')
    return o, f'alone-frac{f}', D, len(freed)

def ham(a, b):
    return sum(x != y for x, y in zip(a, b))

def modes(name, base, full):
    m = 536
    res = {}
    specs = {
        'shift1697': lambda: rowley_modes(1697, base, mirror_S=1698, mirror_range=range(1, m + 2)),
        'sym1698': lambda: rowley_modes(1698, base, mirror_S=1699, mirror_range=range(1, 850)),
        'free1697': lambda: Instance(1697, 7, fixed={i + 1: c for i, c in enumerate(base)}),
        'partial1697': lambda: Instance(1697, 7, mirrors=[(x, 1698 - x) for x in range(567, 849)],
                                        fixed={**{i + 1: c for i, c in enumerate(base)}, 537: 6}),
        # soft symmetric: only 1..400 of the base fixed, 401..536 free but colour 6 kept off them, 537 -> 6
        'sym1698soft400': lambda: Instance(1698, 7, mirrors=[(x, 1699 - x) for x in range(1, 850)],
                                           fixed={**{i + 1: base[i] for i in range(400)}, 537: 6},
                                           forbid={x: {6} for x in range(401, 537)}),
        'sym1699soft400': lambda: Instance(1699, 7, mirrors=[(x, 1700 - x) for x in range(1, 850)],
                                           fixed={**{i + 1: base[i] for i in range(400)}, 537: 6},
                                           forbid={x: {6} for x in range(401, 537)}),
    }
    if not full:
        specs = {k: specs[k] for k in ('shift1697', 'sym1698')}
    for mode, mk in specs.items():
        if time.time() > DEADLINE:
            break
        inst = mk()
        o = solve_bin(inst, min(T_MODE, max(1, DEADLINE - time.time())), seed=rnd.randrange(1 << 30), tag='mode')
        if o['status'] == 'SAT':
            v = violations(o['cols'])
            save(f'sols/{name}_{mode}.json', o['cols'])
            log(event='MODE_SAT', base=name, mode=mode, N=inst.N, violations=len(v), **o)
        else:
            log(event='MODE', base=name, mode=mode, N=inst.N, **o)
        res[mode] = o['status']
    return res

def validate(name, base):
    inst = rowley_modes(1696, base, mirror_S=1697)
    o = solve_bin(inst, T_VALID, seed=rnd.randrange(1 << 30), tag='val')
    v = None
    if o['status'] == 'SAT':
        v = len(violations(o['cols']))
        save(f'sols/{name}_valid1696.json', o['cols'])
    log(event='VALIDATE', base=name, violations=v, **o)
    return o['status'] == 'SAT' and v == 0, o

i = 0
log(event='START', seed=SEED, deadline=DEADLINE)
while time.time() < DEADLINE - 30:
    i += 1
    src_name, src = rnd.choice(sources[-8:]) if rnd.random() < 0.7 else rnd.choice(sources)
    r = rnd.random()
    if r < 0.2:
        o, desc, D, nfree = gen_alone(src); gk = 'alone'
    else:
        kind = rnd.choice(['frac', 'frac', 'window', 'short']); o, desc, D, nfree = gen_joint(src, kind); gk = 'joint'
    if o['status'] != 'SAT':
        log(event='GEN', gen=gk, desc=desc, D=D, nfree=nfree, src=src_name, **o); continue
    base = o['cols'][:536]
    assert not violations(base) and max(base) <= 5
    if tuple(base) in bases:
        log(event='GEN_DUP', gen=gk, desc=desc, src=src_name, dup_of=bases[tuple(base)]); continue
    name = f'b{SEED}_{i:04d}'
    bases[tuple(base)] = name
    save(f'bases/{name}.json', base)
    dmin = min(ham(base, list(b)) for b in bases if bases[b] != name)
    log(event='GEN', gen=gk, desc=desc, D=D, nfree=nfree, src=src_name, base=name, ham_rowley=ham(base, rowley[:536]),
        ham_nearest=dmin, **o)
    ok, vo = validate(name, base)
    if not ok:
        continue
    sources.append((name, vo['cols']))
    npass = sum(1 for _ in sources) - 1
    modes(name, base, full=(npass % 3 == 1) or ham(base, rowley[:536]) >= 120)
log(event='END', bases=len(bases) - 1)
