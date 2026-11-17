"""n = 5 LKH parameter probe: same ATSP encoding as lns_lkh.solve_segment (padded lexicographic path, ends fixed),
with stronger LKH settings, to see whether the known minimum 153 is reachable by this encoding at all."""
import itertools, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lns_lkh as L
L.N = 5
lkh, wd = sys.argv[1], sys.argv[2]
perms = [''.join(p) for p in itertools.permutations('12345')]
L.solve_segment(perms, lkh, wd, 1, 5)           # writes seg.atsp and init.tour for this instance
s, t, inner = perms[0], perms[-1], perms[1:-1]
nodes = ['X'] + inner
settings = {
    'cand20_trials5000_runs5': 'MAX_CANDIDATES = 20\nMAX_TRIALS = 5000\nRUNS = 5\nMOVE_TYPE = 5\n',
    'cand20_no_initial_runs5': 'MAX_CANDIDATES = 20\nMAX_TRIALS = 5000\nRUNS = 5\nMOVE_TYPE = 5\nNOINIT\n',
    'move3_cand10_runs10': 'MAX_CANDIDATES = 10\nMAX_TRIALS = 2000\nRUNS = 10\nMOVE_TYPE = 3\n',
}
for name, extra in settings.items():
    out = os.path.join(wd, f'p_{name}.tour')
    par = os.path.join(wd, f'p_{name}.par')
    init = '' if 'NOINIT' in extra else f'INITIAL_TOUR_FILE = {wd}/init.tour\n'
    extra = extra.replace('NOINIT\n', '')
    open(par, 'w').write(f'PROBLEM_FILE = {wd}/seg.atsp\n{init}OUTPUT_TOUR_FILE = {out}\nTIME_LIMIT = 60\nSEED = 1\nTRACE_LEVEL = 0\n{extra}')
    subprocess.run([lkh, par], stdout=subprocess.DEVNULL, timeout=900)
    tour = []
    sec = False
    for line in open(out):
        line = line.strip()
        if line == 'TOUR_SECTION': sec = True; continue
        if sec:
            if line == '-1': break
            tour.append(int(line) - 1)
    z = tour.index(0); tour = tour[z:] + tour[:z]
    new = [s] + [nodes[i] for i in tour[1:]] + [t]
    w = L.path_word(new)
    print(f'{name}: length {len(w)}, distinct perms {len(set(L.perm_path(w)))}', flush=True)
