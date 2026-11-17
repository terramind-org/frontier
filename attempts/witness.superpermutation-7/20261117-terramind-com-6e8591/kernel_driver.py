"""Kernel line: generate Houston kernels of score >= 20 (which would give length 5904) by re-completing the tail of the
5905 kernel (or of its reversal) with kernelwalk, then hand each new kernel to Egan's PermutationChains (no symmetry
options, as in the 5905 find). Kernels that PermutationChains finds viable (it reaches the tree search) join a pool of
bases, in both orientations, so later tails are cut from them too; a share of batches targets score 15 to grow the
pool. Every kernel tried is logged with the last line of PermutationChains' output. Any solution file is converted to a witness JSON and checked by the repo verifier.

Usage: python3 -I kernel_driver.py <bin-dir> <workdir> <seconds> <seed> <repo-root> [targets, default 20,20,20,25] [file of earlier 'viable kernel searched:' lines to seed the pool]
"""
import glob, json, os, random, shutil, subprocess, sys, time

K5905 = '4666446666-6666466636666-666646646666-666646646666-6666366646666-6666446664'

def main():
    bindir, wd, seconds, seed, repo = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    targets = [int(x) for x in (sys.argv[6] if len(sys.argv) > 6 else '20,20,20,25').split(',')]
    bindir, wd = os.path.abspath(bindir), os.path.abspath(wd)
    os.makedirs(wd, exist_ok=True)
    rng = random.Random(seed)
    kw, pc = os.path.join(bindir, 'kernelwalk'), os.path.join(bindir, 'PermutationChains')
    seen = set()
    stats = {'kernels': 0, 'unviable': 0, 'searched': 0, 'timeout': 0, 'solutions': 0}
    bases = [K5905, K5905[::-1]]
    log = open(os.path.join(wd, 'kernels.log'), 'a')
    if len(sys.argv) > 7:
        for line in open(sys.argv[7]):
            if line.startswith('viable kernel searched: '):
                k = line.split(': ', 1)[1].strip()
                seen.add(k)
                for b in (k, k[::-1]):
                    if b not in bases:
                        bases.append(b)
    t0 = time.time(); batch = 0
    while time.time() - t0 < seconds:
        batch += 1
        base = rng.choice(bases)
        cut = rng.randint(15, len(base))
        while cut > 0 and base[cut - 1] == '-':
            cut -= 1
        prefix = base[:cut]
        target = 15 if rng.random() < 0.15 else rng.choice(targets)
        maxlen = len(base) + rng.randint(5, 35)
        try:
            r = subprocess.run([kw, '7', str(target), str(maxlen), str(rng.choice([20000, 200000, 2000000])), '5',
                                str(rng.randint(1, 10**9)), '0', prefix], capture_output=True, text=True, timeout=120)
            ks = [k for k in r.stdout.split() if k and k[0].isdigit()]
        except subprocess.TimeoutExpired:
            ks = []
        new = [k for k in dict.fromkeys(ks) if k not in seen]
        rng.shuffle(new)
        for k in new[:300]:
            if time.time() - t0 >= seconds:
                break
            seen.add(k); stats['kernels'] += 1
            for f in glob.glob(os.path.join(wd, '7_*.txt')):
                os.remove(f)
            try:
                p = subprocess.run([pc, '7', 'nsk' + k], cwd=wd, capture_output=True, text=True, timeout=60)
                out = p.stdout
            except subprocess.TimeoutExpired as e:
                out = (e.stdout or b'').decode() if isinstance(e.stdout, bytes) else (e.stdout or '')
                stats['timeout'] += 1
            if 'unviable' in out:
                stats['unviable'] += 1
            elif 'Searching for solutions' in out:
                stats['searched'] += 1
                print(f'viable kernel searched: {k}', flush=True)
                for b in (k, k[::-1]):
                    if b not in bases:
                        bases.append(b)
            last = out.strip().splitlines()[-1] if out.strip() else ''
            log.write(f'{k}\t{last}\n'); log.flush()
            if 'Found SOLUTION' in out:
                stats['solutions'] += 1
                for f in glob.glob(os.path.join(wd, '7_*.txt')):
                    if 'twoCycles' in f:
                        continue
                    keep = os.path.join(wd, 'found_' + os.path.basename(f)[:60] + f'_{stats["solutions"]}.txt')
                    shutil.copy(f, keep)
                    for li, line in enumerate(open(f)):
                        w = ''.join(c for c in line if c in '1234567')
                        if not w:
                            continue
                        js = os.path.join(wd, f'cand_{len(w)}_{stats["solutions"]}_{li}.json')
                        json.dump({'word': w}, open(js, 'w'))
                        d = subprocess.run(['bun', 'frontier', 'diagnose', os.path.abspath(js), '--problem',
                                            'witness.superpermutation-7'], cwd=repo, capture_output=True, text=True)
                        print(f'SOLUTION kernel {k} length {len(w)} -> {js}\n{d.stdout}', flush=True)
        print(f'batch {batch} t {time.time()-t0:.0f}s prefix {cut}/{len(base)} target {target} maxlen {maxlen} '
              f'new {len(new)} pool {len(bases)} stats {stats}', flush=True)
    print(f'end {stats}', flush=True)

if __name__ == '__main__':
    main()
