"""One-core three-slice recombination search for the vendored F_3^8 cap.

Split on coordinate 0.  With slices A, B, C in F_3^7, the only lines using
all three slices have a+b+c=0.  This program preserves capness in A and B,
applies a signed coordinate permutation to B, and greedily rebuilds C from
the points not forbidden by A+B.  It is deliberately independent of the
previous single-point exchange walk.
"""
import argparse
import hashlib
import itertools
import json
import os
import random
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np


def digest(points):
    return hashlib.sha256(np.asarray(sorted(points), dtype="<i2").tobytes()).hexdigest()


class Space:
    def __init__(self, n=7):
        self.n = n
        self.m = 3 ** n
        self.v = np.array(list(itertools.product(range(3), repeat=n)), dtype=np.int8)
        self.p = 3 ** np.arange(n - 1, -1, -1, dtype=np.int32)

    def ids(self, rows):
        return np.asarray(rows, dtype=np.int16) @ self.p

    def third(self, a, b):
        return int(((-self.v[a] - self.v[b]) % 3) @ self.p)

    def cap(self, points):
        points = sorted(points)
        inside = np.zeros(self.m, dtype=bool)
        inside[points] = True
        for i, a in enumerate(points):
            for b in points[i + 1:]:
                if inside[self.third(a, b)]:
                    return False
        return True


def transform(space, points, perm, signs):
    rows = space.v[sorted(points)]
    return set(space.ids((rows[:, perm] * signs) % 3))


def rebuild(space, a, b, rng):
    """Randomized greedy cap in the third slice after cross-layer blocking."""
    blocked = np.zeros(space.m, dtype=bool)
    for u in a:
        blocked[space.ids((-space.v[u] - space.v[list(b)]) % 3)] = True
    order = np.flatnonzero(~blocked).tolist()
    rng.shuffle(order)
    c = set()
    unavailable = blocked.copy()
    for u in order:
        if unavailable[u]:
            continue
        for v in c:
            unavailable[space.third(u, v)] = True
        unavailable[u] = True
        c.add(u)
    return c, int((~blocked).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--seconds", type=float, default=1800)
    ap.add_argument("--seed", type=int, default=841196)
    ap.add_argument("--log", required=True)
    ap.add_argument("--best", required=True)
    args = ap.parse_args()
    raw = json.load(open(args.input))["points"]
    sp = Space()
    layers = [set(sp.ids([p[1:] for p in raw if p[0] == z])) for z in range(3)]
    assert [len(x) for x in layers] == [192, 160, 160]
    assert all(sp.cap(x) for x in layers)
    rng = random.Random(args.seed)
    started = time.monotonic()
    best = 0
    trials = 0
    distinct = set()
    with open(args.log, "w", encoding="utf-8") as log:
        def emit(event, **kw):
            row = dict(event=event, elapsed=round(time.monotonic() - started, 3), **kw)
            print(json.dumps(row), flush=True)
            log.write(json.dumps(row) + "\n")
            log.flush()
        emit("start", seed=args.seed, input_sha256=hashlib.sha256(open(args.input, "rb").read()).hexdigest(), layer_sizes=[len(x) for x in layers])
        while time.monotonic() - started < args.seconds:
            trials += 1
            perm = list(range(7)); rng.shuffle(perm)
            signs = np.array([rng.choice((1, 2)) for _ in range(7)], dtype=np.int8)
            b = transform(sp, layers[1], perm, signs)
            c, free = rebuild(sp, layers[0], b, rng)
            size = len(layers[0]) + len(b) + len(c)
            sig = digest(b) + ":" + digest(c)
            distinct.add(sig)
            if size > best:
                best = size
                rows = []
                for z, layer in enumerate((layers[0], b, c)):
                    rows.extend([[z] + list(map(int, sp.v[u])) for u in sorted(layer)])
                assert len(rows) == size
                json.dump({"points": rows}, open(args.best, "w"))
                emit("best", trial=trials, size=size, free=free, perm=perm, signs=signs.tolist(), b_hash=digest(b), c_hash=digest(c))
            if trials % 100 == 0:
                emit("progress", trials=trials, best=best, distinct= len(distinct), last_size=size, last_free=free)
        emit("end", trials=trials, best=best, distinct=len(distinct), seed=args.seed, resume_cursor={"next_trial": trials + 1, "seed": args.seed})


if __name__ == "__main__":
    main()
