"""Search for 29-mark Golomb rulers shorter than 623.
Phase 1: algebraic constructions (Bose-Chowla, Singer, Ruzsa) over all multipliers,
         all cyclic windows of 29 marks.
Phase 2: simulated annealing on length-L rulers, minimising repeated differences.
Usage: python3 golomb_search.py <phase2_seconds>
"""
import sys, random, time, math, json
from math import gcd

M = 29
BEST_KNOWN = 623


def is_golomb(marks):
    s = set()
    for i in range(len(marks)):
        for j in range(i):
            d = marks[i] - marks[j]
            if d in s:
                return False
            s.add(d)
    return True


def best_window(res, mod, k=M):
    n = len(res)
    best = None
    ext = res + [r + mod for r in res]
    for i in range(n):
        w = ext[i:i + k]
        L = w[-1] - w[0]
        if best is None or L < best[0]:
            best = (L, [x - w[0] for x in w])
    return best


def scan(res, mod, label):
    best = None
    for m in range(1, mod):
        if gcd(m, mod) != 1:
            continue
        r = sorted((m * x) % mod for x in res)
        if len(r) < M:
            continue
        b = best_window(r, mod)
        if best is None or b[0] < best[0]:
            best = b
    print(label, "best length", best[0], flush=True)
    return best


def primes_dividing(order):
    return [p for p in range(2, order + 1)
            if order % p == 0 and all(p % d for d in range(2, int(p ** .5) + 1))]


def bose(q):
    nr = next(a for a in range(2, q) if pow(a, (q - 1) // 2, q) == q - 1)

    def mul(u, v):
        return ((u[0] * v[0] + nr * u[1] * v[1]) % q, (u[0] * v[1] + u[1] * v[0]) % q)

    order = q * q - 1
    fac = primes_dividing(order)

    def powr(u, e):
        r = (1, 0)
        while e:
            if e & 1:
                r = mul(r, u)
            u = mul(u, u)
            e >>= 1
        return r

    th = None
    for a in range(q):
        for b in range(1, q):
            g = (a, b)
            if all(powr(g, order // p) != (1, 0) for p in fac):
                th = g
                break
        if th:
            break
    res = []
    cur = (1, 0)
    for e in range(order):
        if cur[1] == th[1]:  # theta^e - theta in GF(q)
            res.append(e)
        cur = mul(cur, th)
    return sorted(res), order


def singer(q):
    order = q ** 3 - 1
    fac = primes_dividing(order)
    N = q * q + q + 1
    for a in range(q):
        for b in range(1, q):
            def mul(u, w):
                r = [0] * 5
                for i in range(3):
                    for j in range(3):
                        r[i + j] += u[i] * w[j]
                for d in (4, 3):
                    c = r[d]
                    r[d] = 0
                    r[d - 2] += a * c
                    r[d - 3] += b * c
                return tuple(x % q for x in r[:3])

            def powr(u, e):
                r = (1, 0, 0)
                while e:
                    if e & 1:
                        r = mul(r, u)
                    u = mul(u, u)
                    e >>= 1
                return r

            x = (0, 1, 0)
            if powr(x, order) != (1, 0, 0):
                continue
            if any(powr(x, order // p) == (1, 0, 0) for p in fac):
                continue
            res = set()
            cur = (1, 0, 0)
            for e in range(order):
                if cur[2] == 0:
                    res.add(e % N)
                cur = mul(cur, x)
            return sorted(res), N
    raise RuntimeError


def ruzsa(p):
    fac = primes_dividing(p - 1)
    g = next(g for g in range(2, p) if all(pow(g, (p - 1) // f, p) != 1 for f in fac))
    mod = p * (p - 1)
    res = set()
    for i in range(1, p):
        gi = pow(g, i, p)
        for x in range(i % (p - 1), mod, p - 1):
            if x % p == gi:
                res.add(x)
                break
    return sorted(res), mod


def check_sidon(res, mod):
    k = len(res)
    return len({(a - b) % mod for a in res for b in res if a != b}) == k * (k - 1)


def phase1():
    best = (10 ** 9, None)
    cases = []
    for q in (29, 31, 37):
        cases.append((f"Bose q={q}", bose(q)))
    for q in (29, 31):
        cases.append((f"Singer q={q}", singer(q)))
    for p in (31, 37):
        cases.append((f"Ruzsa p={p}", ruzsa(p)))
    for label, (res, mod) in cases:
        print(label, "marks", len(res), "mod", mod, "sidon", check_sidon(res, mod), flush=True)
        b = scan(res, mod, label)
        if b[0] < best[0]:
            best = b
    print("phase1 best:", best[0], flush=True)
    return best


def energy(marks):
    cnt = {}
    e = 0
    for i in range(len(marks)):
        for j in range(i):
            d = abs(marks[i] - marks[j])
            c = cnt.get(d, 0)
            if c:
                e += 1
            cnt[d] = c + 1
    return e


def phase2(L, seconds, seed):
    rnd = random.Random(seed)
    t_end = time.time() + seconds
    best_e = 10 ** 9
    restarts = 0
    while time.time() < t_end:
        restarts += 1
        marks = sorted(rnd.sample(range(1, L), M - 2) + [0, L])
        e = energy(marks)
        T = 1.0
        for it in range(200000):
            if time.time() >= t_end:
                break
            i = rnd.randrange(1, M - 1)
            old = marks[i]
            new = rnd.randrange(1, L)
            if new in marks:
                continue
            marks[i] = new
            e2 = energy(marks)
            if e2 <= e or rnd.random() < math.exp((e - e2) / T):
                e = e2
            else:
                marks[i] = old
            T = max(0.15, T * 0.99997)
            best_e = min(best_e, e)
            if e == 0:
                m = sorted(marks)
                if is_golomb(m):
                    return m, restarts, best_e
    return None, restarts, best_e


if __name__ == "__main__":
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 300
    t0 = time.time()
    b = phase1()
    print("phase1 time %.1fs" % (time.time() - t0), flush=True)
    if b[0] < BEST_KNOWN:
        json.dump({"marks": b[1]}, open("witness_candidate.json", "w"))
        print("IMPROVED?", b[0], b[1])
        sys.exit(0)
    L = BEST_KNOWN - 1
    m, r, be = phase2(L, secs, 1)
    print("phase2 target length", L, "restarts", r, "best energy (repeated diffs)", be, "found", m, flush=True)
    if m:
        json.dump({"marks": m}, open("witness_candidate.json", "w"))
