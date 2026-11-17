"""Self-tests for the search code (run from the scratch directory; source dir on sys.path).

1. The inner-loop validity check used by lns_lkh.py (perm_path: every window with 7 distinct digits; a valid word has
   all 5040 distinct) accepts the 5905 baseline and rejects two broken copies (one character changed, one deleted).
2. path_word(perm_path(w)) rebuilds the baseline exactly (the LNS writes words this way).
3. solve_segment (the LKH segment re-solve) on n = 5: start from the 5 symbols' permutations in lexicographic order
   (a padded path, ends 12345 and 54321 fixed) and re-solve the whole path; the known minimum is 153 characters.
4. solve_segment on n = 7: corrupt the baseline path by reversing a 40-permutation stretch inside a 300-permutation
   window (which adds weight), then re-solve that window; it should return to the original window cost or less.

Usage: python3 -I src/selftest.py <baseline.json> <lkh-binary> <workdir>
"""
import itertools, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import lns_lkh as L

def valid(word, n):
    L.N = n
    p = L.perm_path(word)
    import math
    return len(set(p)) == math.factorial(n)

def main():
    base, lkh, wd = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(wd, exist_ok=True)
    w = json.load(open(base))['word']
    print('1. baseline', len(w), 'accepted:', valid(w, 7))
    k = 3000
    broken1 = w[:k] + ('1' if w[k] != '1' else '2') + w[k + 1:]
    broken2 = w[:k] + w[k + 1:]
    print('   one character changed at 3000, accepted:', valid(broken1, 7))
    print('   one character deleted at 3000, accepted:', valid(broken2, 7))
    json.dump({'word': broken1}, open(os.path.join(wd, 'broken_changed.json'), 'w'))
    json.dump({'word': broken2}, open(os.path.join(wd, 'broken_deleted.json'), 'w'))
    L.N = 7
    print('2. path_word(perm_path(baseline)) == baseline:', L.path_word(L.perm_path(w)) == w)
    # 3. n = 5
    L.N = 5
    perms = [''.join(p) for p in itertools.permutations('12345')]
    padded = L.path_word(perms)
    print('3. n=5 padded lexicographic path: length', len(padded), 'valid', valid(padded, 5))
    L.N = 5
    best = None
    for seed in (1, 2, 3):
        new = L.solve_segment(perms, lkh, wd, seed, 20)
        word = L.path_word(new)
        ok = valid(word, 5)
        print(f'   LKH re-solve seed {seed}: length {len(word)}, valid {ok}, same ends {new[0]==perms[0] and new[-1]==perms[-1]}')
        if ok and (best is None or len(word) < len(best)):
            best = word
    json.dump({'word': best}, open(os.path.join(wd, 'n5_resolved.json'), 'w'))
    print('   best', len(best), '(known minimum 153)')
    # 4. n = 7 corrupted window
    L.N = 7
    path = L.perm_path(w)
    i, j = 2000, 2300
    seg = path[i:j + 1]
    orig = L.seg_cost(seg)
    bad = seg[:100] + seg[100:140][::-1] + seg[140:]
    bc = L.seg_cost(bad)
    new = L.solve_segment(bad, lkh, wd, 7, 60)
    nc = L.seg_cost(new)
    full = L.path_word(path[:i] + new + path[j + 1:])
    print(f'4. n=7 window [{i},{j}]: original cost {orig}, corrupted {bc}, LKH re-solved {nc}, '
          f'rebuilt word length {len(full)} valid {valid(full, 7)}')

if __name__ == '__main__':
    main()
