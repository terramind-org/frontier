"""C3-symmetric Hensel lift of a GF(2) C3SCHEME file to an integer scheme (cyclic Brent equations, as in
Moosbauer and Poole, arXiv:2502.04514, Section 6).

Unknowns: the three factor matrices of each orbit representative (alpha, beta, gamma). The fixed terms X (x) X (x) X
are constants (entries 0/1), as in the paper. Equations, one per rotation class of (p,q,r) in (n^2)^3:
  sum_orbits alpha_p beta_q gamma_r + beta_p gamma_q alpha_r + gamma_p alpha_q beta_r + sum_fixed X_p X_q X_r = M_pqr
where M is the matrix multiplication tensor in trace form (bit i*n+j of a factor = entry (i,j); M = sum E_ij E_jk E_ki).

Step m -> m+1: x = x_m + 2^m y with J(x0) y = -F(x_m)/2^m (mod 2). Variables are ordered so that entries that are odd
mod 2 come first (they become pivots), entries that are 0 mod 2 come last (they tend to be free and stay 0). Free
variables are 0 except on the first `random_levels` levels of a try, where they are random. After every level x is
taken in the symmetric range (-2^m, 2^m] and tested as an exact integer scheme.

Usage: python3 -I c3lift.py <scheme.c3> <out.json> [tries] [max_level] [random_levels] [seed]
Writes the integer scheme in the verifier's JSON format (c is the transpose of the trace-form third factor) and
prints LIFT_OK / LIFT_FAIL lines.
"""
import json
import sys

import numpy as np


def read_c3(path):
    with open(path) as fh:
        head = fh.readline().split()
        assert head[0] == "C3SCHEME", head
        n, rank, no, nf = map(int, head[1:])
        fixed = [int(fh.readline()) for _ in range(nf)]
        orbits = [tuple(map(int, fh.readline().split())) for _ in range(no)]
    return n, fixed, orbits


def bits(m, nn):
    return np.array([(m >> i) & 1 for i in range(nn)], dtype=np.int64)


def target_tensor(n):
    nn = n * n
    T = np.zeros((nn, nn, nn), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                T[i * n + j, j * n + k, k * n + i] += 1
    return T


def canon_index(nn):
    """indices (flattened) of one representative per rotation class (p,q,r)->(q,r,p)"""
    keep = []
    for p in range(nn):
        for q in range(nn):
            for r in range(nn):
                a = (p * nn + q) * nn + r
                b = (q * nn + r) * nn + p
                c = (r * nn + p) * nn + q
                if a <= b and a <= c:
                    keep.append(a)
    return np.array(keep)


def F_of(X, fixedT, target, mod=None):
    """X: (k,3,nn) int64; returns F as flat (nn^3,) int64 (exact if mod is None, else reduced mod `mod`)."""
    k = X.shape[0]
    nn = X.shape[2]
    tot = fixedT.copy()
    for o in range(k):
        a, b, c = X[o]
        for (u, v, w) in ((a, b, c), (b, c, a), (c, a, b)):
            uv = np.outer(u, v)
            if mod is not None:
                uv %= mod
            t = (uv.reshape(-1, 1) * w.reshape(1, -1))
            if mod is not None:
                t %= mod
            tot = tot + t.reshape(-1)
            if mod is not None:
                tot %= mod
    out = tot - target.reshape(-1)
    if mod is not None:
        out %= mod
    return out


def jacobian_mod2(X0, keep):
    """columns: d F / d X[o, s, e] mod 2, restricted to the canonical equations; returns (len(keep), k*3*nn) uint8"""
    k, _, nn = X0.shape
    cols = np.zeros((len(keep), k * 3 * nn), dtype=np.uint8)
    eye = np.eye(nn, dtype=np.int64)
    for o in range(k):
        a, b, c = X0[o]
        for s in range(3):
            for e in range(nn):
                d = [a, b, c]
                d[s] = eye[e]
                # derivative of the orbit sum w.r.t. factor s, entry e: replace factor s by e_e in each rotation
                da, db, dc = d
                t = (np.einsum("i,j,k->ijk", da, db, dc) + np.einsum("i,j,k->ijk", db, dc, da)
                     + np.einsum("i,j,k->ijk", dc, da, db))
                # each rotation term is linear in each factor, so the derivative is the orbit sum with factor s := e_e
                cols[:, (o * 3 + s) * nn + e] = (t.reshape(-1)[keep] % 2).astype(np.uint8)
    return cols


class GF2System:
    """Row-reduce J once; solve J y = rhs for many rhs."""

    def __init__(self, J, order):
        # J: (R, V) uint8; order: column order (pivot preference)
        self.R, self.V = J.shape
        self.order = np.asarray(order)
        A = J[:, self.order].astype(np.uint8)
        nw = (self.V + 63) // 64
        self.nw = nw
        # pack rows into uint64 words, plus an identity block to record row operations
        self.A = np.packbits(A, axis=1, bitorder="little")
        pad = (-self.A.shape[1]) % 8
        if pad:
            self.A = np.concatenate([self.A, np.zeros((self.R, pad), np.uint8)], axis=1)
        self.A = np.ascontiguousarray(self.A).view(np.uint64).copy()
        E = np.packbits(np.eye(self.R, dtype=np.uint8), axis=1, bitorder="little")
        pad = (-E.shape[1]) % 8
        if pad:
            E = np.concatenate([E, np.zeros((self.R, pad), np.uint8)], axis=1)
        self.E = np.ascontiguousarray(E).view(np.uint64).copy()
        self.pivots = []  # (row, col)
        row = 0
        for col in range(self.V):
            w, b = divmod(col, 64)
            colbits = (self.A[row:, w] >> np.uint64(b)) & np.uint64(1)
            nz = np.nonzero(colbits)[0]
            if len(nz) == 0:
                continue
            pr = row + nz[0]
            if pr != row:
                self.A[[row, pr]] = self.A[[pr, row]]
                self.E[[row, pr]] = self.E[[pr, row]]
            mask = ((self.A[:, w] >> np.uint64(b)) & np.uint64(1)).astype(bool)
            mask[row] = False
            self.A[mask] ^= self.A[row]
            self.E[mask] ^= self.E[row]
            self.pivots.append((row, col))
            row += 1
            if row == self.R:
                break
        self.rank = row
        pivcols = set(c for _, c in self.pivots)
        self.free = [c for c in range(self.V) if c not in pivcols]

    def solve(self, rhs, free_vals):
        """rhs: (R,) 0/1; free_vals: dict col->0/1 in ORDERED column indices. Returns y in ORIGINAL order or None."""
        rb = np.packbits(rhs.astype(np.uint8), bitorder="little")
        pad = (-len(rb)) % 8
        if pad:
            rb = np.concatenate([rb, np.zeros(pad, np.uint8)])
        rw = np.ascontiguousarray(rb).view(np.uint64)
        # transformed rhs: t = E rhs (mod 2)
        t = np.bitwise_xor.reduce(self.E & rw[None, :], axis=1)
        tb = np.array([bin(int(v)).count("1") & 1 for v in t], dtype=np.uint8)
        if tb[self.rank:].any():
            return None
        y = np.zeros(self.V, dtype=np.uint8)
        for c, v in free_vals.items():
            y[c] = v
        yb = np.packbits(y, bitorder="little")
        pad = (-len(yb)) % 8
        if pad:
            yb = np.concatenate([yb, np.zeros(pad, np.uint8)])
        yw = np.ascontiguousarray(yb).view(np.uint64)
        for (r, c) in self.pivots:
            # row r: y_c + sum_{free f} A[r,f] y_f = t_r
            acc = np.bitwise_xor.reduce(self.A[r] & yw)
            par = bin(int(acc)).count("1") & 1  # includes y_c itself, which is 0 so far
            val = (int(tb[r]) ^ par) & 1
            y[c] = val
        out = np.zeros(self.V, dtype=np.uint8)
        out[self.order] = y
        return out


def to_json(n, X, fixed):
    nn = n * n
    terms = []

    def mat(v):
        return [[int(v[i * n + j]) for j in range(n)] for i in range(n)]

    def tmat(v):  # c = transpose of trace-form third factor
        return [[int(v[j * n + i]) for j in range(n)] for i in range(n)]

    for x in fixed:
        b = bits(x, nn)
        terms.append({"a": mat(b), "b": mat(b), "c": tmat(b)})
    for o in range(X.shape[0]):
        a, b, c = X[o]
        for (u, v, w) in ((a, b, c), (b, c, a), (c, a, b)):
            terms.append({"a": mat(u), "b": mat(v), "c": tmat(w)})
    return {"terms": terms}


def main():
    path, outp = sys.argv[1], sys.argv[2]
    tries = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    max_level = int(sys.argv[4]) if len(sys.argv) > 4 else 24
    random_levels = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    n, fixed, orbits = read_c3(path)
    nn = n * n
    k = len(orbits)
    X0 = np.array([[bits(m, nn) for m in o] for o in orbits], dtype=np.int64)
    fixedT = np.zeros(nn ** 3, dtype=np.int64)
    for x in fixed:
        b = bits(x, nn)
        fixedT += np.einsum("i,j,k->ijk", b, b, b).reshape(-1)
    target = target_tensor(n)
    keep = canon_index(nn)
    F0 = F_of(X0, fixedT, target, mod=2)
    if F0.any():
        print("LIFT_FAIL input is not a GF(2) scheme", flush=True)
        sys.exit(3)
    J = jacobian_mod2(X0, keep)
    flat0 = X0.reshape(-1)
    order = list(np.nonzero(flat0)[0]) + list(np.nonzero(flat0 == 0)[0])
    sysm = GF2System(J, order)
    print(f"SYSTEM n={n} orbits={k} fixed={len(fixed)} vars={J.shape[1]} eqs={J.shape[0]} rank={sysm.rank} free={len(sysm.free)}",
          flush=True)
    rng = np.random.default_rng(seed)
    for tr in range(tries):
        X = X0.copy()
        status = "inconsistent"
        for m in range(1, max_level + 1):
            mod = 1 << (m + 1)
            Fm = F_of(X % mod, fixedT, target, mod=mod)
            assert not (Fm % (1 << m)).any()
            rhs = ((Fm >> m) & 1)[keep]  # -v = v mod 2
            fv = {}
            if m <= random_levels and tr > 0:
                for c in sysm.free:
                    fv[c] = int(rng.integers(0, 2))
            y = sysm.solve(rhs.astype(np.uint8), fv)
            if y is None:
                status = f"inconsistent_at_mod_{mod}"
                break
            X = X + (1 << m) * y.reshape(X.shape).astype(np.int64)
            X = ((X + (mod >> 1) - 1) % mod) - ((mod >> 1) - 1)  # symmetric range (-mod/2, mod/2]
            Fz = F_of(X, fixedT, target, mod=None)
            if not Fz.any():
                mx = int(np.abs(X).max())
                print(f"LIFT_OK try={tr} level={m} modulus={mod} max_abs_coef={mx}", flush=True)
                with open(outp, "w") as fh:
                    json.dump(to_json(n, X, fixed), fh)
                return 0
            status = f"no_exact_solution_by_mod_{mod}"
        print(f"LIFT_TRY_FAIL try={tr} status={status}", flush=True)
    print(f"LIFT_FAIL tries={tries}", flush=True)
    return 1


if __name__ == "__main__":
    sys.exit(main())
