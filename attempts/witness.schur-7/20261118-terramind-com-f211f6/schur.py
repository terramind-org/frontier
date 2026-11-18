"""Schur-partition SAT encoder and helpers for the schur7-r2 search.

A colouring of 1..N with K colours; variable v(r, c) for representative r of integer x and colour c.
Optional mirror constraints c(x) = c(S - x) for listed x are imposed by giving x and S - x one representative
(union-find), so a mirror is a variable identification, not extra clauses. Clauses:
  - exactly one colour per representative (at-least-one + pairwise at-most-one);
  - for every x <= y with x + y <= N and every colour c: not all of x, y, x + y have colour c (x = y included);
  - fixed colours as unit clauses, forbidden colours as negative units.
Clauses are written over representatives; duplicate literals collapse, so a triple whose members share one
representative becomes shorter (a mirror that forces x + x = 2x monochromatic yields a unit or empty clause).
"""
import json, os, random, threading, time, datetime

def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4] + 'Z'

def violations(cols):
    """Independent checker: list of (x, y, x+y) monochromatic, cols[i] is colour of i+1."""
    n = len(cols); out = []
    for x in range(1, n // 2 + 1):
        cx = cols[x - 1]
        for y in range(x, n - x + 1):
            if cols[y - 1] == cx and cols[x + y - 1] == cx:
                out.append((x, y, x + y))
    return out

def load(path):
    return json.load(open(path))['colors']

def save(path, cols):
    json.dump({'colors': [int(c) for c in cols]}, open(path, 'w'))

class Instance:
    def __init__(self, N, K, mirrors=(), fixed=None, forbid=None):
        """mirrors: iterable of (x, y) pairs meaning c(x) = c(y). fixed: {x: colour}. forbid: {x: set(colours)}."""
        self.N, self.K = N, K
        parent = list(range(N + 1))
        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]; a = parent[a]
            return a
        for x, y in mirrors:
            assert 1 <= x <= N and 1 <= y <= N
            a, b = find(x), find(y)
            if a != b:
                parent[max(a, b)] = min(a, b)
        self.rep = [0] + [find(x) for x in range(1, N + 1)]
        reps = sorted(set(self.rep[1:]))
        self.idx = {r: i for i, r in enumerate(reps)}
        self.nrep = len(reps)
        self.fixed = dict(fixed or {})
        self.forbid = {k: set(v) for k, v in (forbid or {}).items()}

    def v(self, x, c):
        return self.idx[self.rep[x]] * self.K + c + 1

    @property
    def nvars(self):
        return self.nrep * self.K

    def clauses(self):
        K, N = self.K, self.N
        seen = set()
        for r in self.idx:
            lits = [self.v(r, c) for c in range(K)]
            yield lits
            for i in range(K):
                for j in range(i + 1, K):
                    yield [-lits[i], -lits[j]]
        for x in range(1, N // 2 + 1):
            for y in range(x, N - x + 1):
                key = tuple(sorted({self.rep[x], self.rep[y], self.rep[x + y]}))
                if key in seen:
                    continue
                seen.add(key)
                for c in range(K):
                    yield [-(self.idx[r] * K + c + 1) for r in key]
        fixed_rep = {}
        for x, c in self.fixed.items():
            r = self.rep[x]
            if r in fixed_rep and fixed_rep[r] != c:
                yield []  # contradictory fixing through a mirror
            fixed_rep[r] = c
            yield [self.v(x, c)]
        for x, cs in self.forbid.items():
            for c in cs:
                yield [-self.v(x, c)]

    def decode(self, model):
        pos = set(l for l in model if l > 0)
        cols = []
        for x in range(1, self.N + 1):
            cs = [c for c in range(self.K) if self.v(x, c) in pos]
            assert len(cs) == 1, (x, cs)
            cols.append(cs[0])
        return cols

    def to_dimacs(self, path, extra=()):
        cl = list(self.clauses()) + [list(c) for c in extra]
        with open(path, 'w') as f:
            f.write(f'p cnf {self.nvars} {len(cl)}\n')
            for c in cl:
                f.write(' '.join(map(str, c)) + ' 0\n')
        return len(cl)

def solve(inst, timeout, phases=None, extra=(), seed=None, assumptions=()):
    """Solve with PySAT CaDiCaL 1.9.5. Returns dict(status=SAT|UNSAT|TIMEOUT, seconds, conflicts, cols?)."""
    from pysat.solvers import Cadical195
    t0 = time.time()
    s = Cadical195()
    ncl = 0
    empty = False
    for c in inst.clauses():
        if not c:
            empty = True; continue
        s.add_clause(c); ncl += 1
    for c in extra:
        s.add_clause(list(c)); ncl += 1
    if phases:
        s.set_phases(phases)
    build = time.time() - t0
    if empty:
        s.delete()
        return dict(status='UNSAT', seconds=round(time.time() - t0, 2), build=round(build, 2), conflicts=0,
                    clauses=ncl, note='empty clause from fixing/mirror')
    timer = threading.Timer(timeout, s.interrupt)
    timer.start()
    r = s.solve_limited(assumptions=list(assumptions), expect_interrupt=True)
    timer.cancel()
    st = s.accum_stats() or {}
    out = dict(status={True: 'SAT', False: 'UNSAT', None: 'TIMEOUT'}[r], seconds=round(time.time() - t0, 2),
               build=round(build, 2), conflicts=st.get('conflicts'), decisions=st.get('decisions'), clauses=ncl,
               vars=inst.nvars)
    if r:
        out['cols'] = inst.decode(s.get_model())
    s.delete()
    return out

def rowley_modes(N, base, pivot_colour=6, mirror_S=None, mirror_range=None, middle_free=False):
    """Rowley-style instance: base = colours of 1..m (6 colours), m+1 gets the pivot colour,
    colour 6 forbidden on 1..m. mirror_S: c(x) = c(mirror_S - x) for x in mirror_range (default 1..m+1)."""
    m = len(base)
    fixed = {i + 1: c for i, c in enumerate(base)}
    fixed[m + 1] = pivot_colour
    mirrors = []
    if mirror_S is not None:
        rng = mirror_range if mirror_range is not None else range(1, m + 2)
        for x in rng:
            y = mirror_S - x
            if 1 <= y <= N and y != x:
                mirrors.append((x, y))
    return Instance(N, 7, mirrors=mirrors, fixed=fixed)

CADICAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin/cadical-src/build/cadical')
TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')

def solve_bin(inst, timeout, seed=0, extra=(), assumptions_units=(), proof=None, tag='job', keep_cnf=None):
    """Solve with the CaDiCaL 3.1.0 binary. Variables of the instance are renamed by a seeded random permutation
    (a bijection, so the formula is equivalent) and CaDiCaL runs with --seed/--shuffle, which diversifies the
    solutions found. Returns dict(status=SAT|UNSAT|TIMEOUT|ERROR, rc, seconds, conflicts, decisions, clauses, vars)."""
    import subprocess
    os.makedirs(TMP, exist_ok=True)
    rnd = random.Random(seed)
    n = inst.nvars
    perm = list(range(1, n + 1)); rnd.shuffle(perm)
    mp = lambda l: (perm[abs(l) - 1] if abs(l) <= n else abs(l)) * (1 if l > 0 else -1)
    cl = []
    top = n
    t0 = time.time()
    for c in inst.clauses():
        cl.append(' '.join(str(mp(l)) for l in c) + ' 0')
    for c in list(extra) + [[u] for u in assumptions_units]:
        cl.append(' '.join(str(mp(l)) for l in c) + ' 0')
        top = max([top] + [abs(l) for l in c])
    path = keep_cnf or os.path.join(TMP, f'{tag}_{os.getpid()}.cnf')
    with open(path, 'w') as f:
        f.write(f'p cnf {top} {len(cl)}\n'); f.write('\n'.join(cl)); f.write('\n')
    build = time.time() - t0
    ncl = len(cl); del cl
    cmd = [CADICAL, '-t', str(int(max(1, timeout))), f'--seed={seed}', '--shuffle=true', '--shufflerandom=true']
    if proof:
        cmd += ['--lrat', '--binary=false', path, proof]
    else:
        cmd += [path]
    t1 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    secs = time.time() - t1
    if not keep_cnf:
        os.remove(path)
    out = dict(rc=p.returncode, seconds=round(secs, 2), build=round(build, 2), clauses=ncl, vars=top, seed=seed)
    st = {10: 'SAT', 20: 'UNSAT', 0: 'TIMEOUT'}.get(p.returncode, 'ERROR')
    out['status'] = st
    for line in p.stdout.splitlines():
        if line.startswith('c conflicts:'):
            out['conflicts'] = int(line.split()[2])
        elif line.startswith('c decisions:'):
            out['decisions'] = int(line.split()[2])
    if st == 'SAT':
        inv = {perm[i]: i + 1 for i in range(n)}
        model = []
        for line in p.stdout.splitlines():
            if line.startswith('v '):
                for t in line.split()[1:]:
                    l = int(t)
                    if l and abs(l) <= n:
                        model.append(inv[abs(l)] * (1 if l > 0 else -1))
        out['cols'] = inst.decode(model)
    if st == 'ERROR':
        out['stderr'] = p.stderr[-500:]
    return out
