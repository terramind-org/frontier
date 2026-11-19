"""Second n = 5 LKH check: more seeds and longer time limits on the padded lexicographic path (ends fixed)."""
import itertools, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lns_lkh as L
L.N = 5
perms = [''.join(p) for p in itertools.permutations('12345')]
best = None
for seed in range(4, 14):
    new = L.solve_segment(perms, sys.argv[1], sys.argv[2], seed, 60)
    w = L.path_word(new)
    print(f'seed {seed}: length {len(w)} distinct perms {len(set(L.perm_path(w)))}', flush=True)
    if best is None or len(w) < len(best):
        best = w
json.dump({'word': best}, open(os.path.join(sys.argv[2], 'n5_best.json'), 'w'))
print('best', len(best))
