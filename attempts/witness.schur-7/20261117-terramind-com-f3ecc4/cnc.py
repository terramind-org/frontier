"""Cube-and-conquer line (core 2) of the schur7-r2 search.

For several DIFFERENT valid 1696 colourings (Rowley's, symmetric ones produced by bases.py, and non-symmetric
re-solves of them), fix only the first F colours and ask for a 7-colouring of 1..N (N = 1697 by default,
1696 for the calibration). Cubes: the free integers with the fewest colours left after excluding colours by
pairs of fixed integers (ties: smallest integer) are split on their allowed colours, to depth d chosen so that
the number of cubes is at most CUBES. Each cube is conquered by the CaDiCaL binary with a wall-clock limit;
status, return code and conflicts are logged per cube (logs/cnc.jsonl). Any SAT cube is decoded, checked with
the independent checker and saved.

usage: cnc.py DEADLINE SEED N CUBES TLIM F1,F2 SOURCE.json [SOURCE.json ...]
"""
import glob, itertools, json, os, random, subprocess, sys, time
from schur import *

DEADLINE, SEED, N, CUBES, TLIM = float(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
FS = [int(x) for x in sys.argv[6].split(',')]
CALIB = os.environ.get('CNC_CALIB') == '1'   # put the cube agreeing with the source first
SRCS = sys.argv[7:]

def write_body(inst, path):
    n = 0
    with open(path, 'w') as f:
        for c in inst.clauses():
            f.write(' '.join(map(str, c)) + ' 0\n'); n += 1
    return n

def conquer(inst, body, nbody, units, tlim, seed, tag):
    path = os.path.join(TMP, f'{tag}_{os.getpid()}.cnf')
    with open(path, 'w') as f:
        f.write(f'p cnf {inst.nvars} {nbody + len(units)}\n')
    subprocess.run(f'cat {body} >> {path}', shell=True, check=True)
    with open(path, 'a') as f:
        f.write(''.join(f'{u} 0\n' for u in units))
    t1 = time.time()
    p = subprocess.run([CADICAL, '-t', str(int(max(1, tlim))), f'--seed={seed}', path], capture_output=True, text=True)
    os.remove(path)
    out = dict(rc=p.returncode, seconds=round(time.time() - t1, 2), clauses=nbody + len(units), seed=seed,
               status={10: 'SAT', 20: 'UNSAT', 0: 'TIMEOUT'}.get(p.returncode, 'ERROR'))
    for line in p.stdout.splitlines():
        if line.startswith('c conflicts:'): out['conflicts'] = int(line.split()[2])
        elif line.startswith('c decisions:'): out['decisions'] = int(line.split()[2])
    if out['status'] == 'SAT':
        model = [int(t) for line in p.stdout.splitlines() if line.startswith('v ') for t in line.split()[1:] if t != '0']
        out['cols'] = inst.decode(model)
    return out
rnd = random.Random(SEED)
os.makedirs('sols', exist_ok=True)
LOG = open('logs/cnc.jsonl', 'a')

def log(**kw):
    kw['utc'] = utc(); kw = {k: v for k, v in kw.items() if k != 'cols'}
    LOG.write(json.dumps(kw) + '\n'); LOG.flush(); print(json.dumps(kw), flush=True)

def allowed(fixed, N, K=7):
    al = {}
    for z in range(1, N + 1):
        if z in fixed: continue
        bl = set()
        for x, c in fixed.items():
            if 1 <= z - x and fixed.get(z - x) == c: bl.add(c)
            if z + x <= N and fixed.get(z + x) == c: bl.add(c)
        if 2 * z <= N and fixed.get(2 * z) is not None: bl.add(fixed[2 * z])
        al[z] = [c for c in range(K) if c not in bl]
    return al

def cubes_for(al):
    order = sorted(al, key=lambda z: (len(al[z]), z))
    split, count = [], 1
    for z in order:
        if len(al[z]) <= 1: continue
        if count * len(al[z]) > CUBES: break
        split.append(z); count *= len(al[z])
    cubes = [list(zip(split, cs)) for cs in itertools.product(*[al[z] for z in split])]
    return split, cubes

log(event='START', seed=SEED, N=N, cubes=CUBES, tlim=TLIM, F=FS, sources=SRCS, deadline=DEADLINE)
for src in SRCS:
    cols = load(src)
    for F in FS:
        if time.time() > DEADLINE: break
        fixed = {x: cols[x - 1] for x in range(1, F + 1)}
        al = allowed(fixed, N)
        split, cubes = cubes_for(al)
        inst = Instance(N, 7, fixed=fixed)
        log(event='CUBES', source=src, F=F, split=split, ncubes=len(cubes),
            free_allowed_hist={k: sum(len(v) == k for v in al.values()) for k in range(8)})
        rnd.shuffle(cubes)
        if CALIB:
            cubes.sort(key=lambda cb: 0 if all(cols[z - 1] == c for z, c in cb) else 1)
        os.makedirs(TMP, exist_ok=True)
        body = os.path.join(TMP, f'body_{os.getpid()}.cnf'); t0 = time.time(); nbody = write_body(inst, body)
        log(event='BODY', source=src, F=F, N=N, clauses=nbody, build=round(time.time() - t0, 2))
        tally = {}
        for ci, cube in enumerate(cubes):
            left = DEADLINE - time.time()
            if left < 20: break
            units = [inst.v(z, c) for z, c in cube]
            o = conquer(inst, body, nbody, units, min(TLIM, left - 5), rnd.randrange(1 << 30), 'cnc')
            tally[o['status']] = tally.get(o['status'], 0) + 1
            extra = {}
            if o['status'] == 'SAT':
                v = violations(o['cols']); extra['violations'] = len(v)
                name = f"sols/cnc_{os.path.basename(src)[:-5]}_F{F}_N{N}_{ci}.json"; save(name, o['cols']); extra['saved'] = name
            log(event='CUBE', source=src, F=F, N=N, cube=cube, idx=ci, **o, **extra)
            if CALIB and ci >= int(os.environ.get('CNC_CALIB_N', '2')):
                break
        os.remove(body)
        log(event='CUBES_DONE', source=src, F=F, N=N, tally=tally, ncubes=len(cubes))
log(event='END')
