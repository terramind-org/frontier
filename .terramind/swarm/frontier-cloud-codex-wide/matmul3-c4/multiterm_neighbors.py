#!/usr/bin/env python3
"""Exact five-term reduction screen on seven rank-23 Perminov neighbours.

The input is the pinned cr58_cn122 certificate.  A neighbour is made by the
integer shared-factor identity X⊗Y⊗Z + U⊗V⊗Z =
(X+U)⊗Y⊗Z + U⊗(V-Y)⊗Z (and cyclic variants).  This leaves the full tensor
unchanged but alters the five-term supports.  For every five-term support we
look for a constructive reduction: factor one of its three flattenings over Q
and require every resulting complementary 9-vector to be a decomposable
3-by-3 matrix.  Such a factorization is an explicit replacement by fewer
rank-one terms, not merely a rank lower bound.

This deliberately never visits supports of size three or four.
"""
from __future__ import annotations

import argparse, hashlib, itertools, json, math, time
from fractions import Fraction
from pathlib import Path


def sparse_program(base, fresh, outputs):
    vectors = [tuple(1 if i == j else 0 for i in range(base)) for j in range(base)]
    def expand(form):
        return tuple(sum(item["value"] * vectors[item["index"]][q] for item in form) for q in range(base))
    for form in fresh:
        vectors.append(expand(form))
    return [expand(form) for form in outputs]


def decode(path):
    data = json.loads(Path(path).read_text())
    assert data["n"] == [3, 3, 3] and data["m"] == 23 and data["z2"] is False
    a = sparse_program(9, data["u_fresh"], data["u"])
    b = sparse_program(9, data["v_fresh"], data["v"])
    raw = sparse_program(23, data["w_fresh"], data["w"])
    c = [tuple(raw[3 * col + row][term] for row in range(3) for col in range(3)) for term in range(23)]
    return [(a[i], b[i], c[i]) for i in range(23)]


def normalize(v):
    first = next(x for x in v if x)
    return tuple(Fraction(x, first) for x in v)


def add(x, y): return tuple(a + b for a, b in zip(x, y))
def sub(x, y): return tuple(a - b for a, b in zip(x, y))
def outer(x, y): return tuple(a * b for a in x for b in y)


def rank(rows):
    rows = [list(map(Fraction, row)) for row in rows]
    pivot_row = 0
    pivots = []
    for col in range(len(rows[0]) if rows else 0):
        pivot = next((r for r in range(pivot_row, len(rows)) if rows[r][col]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][col]
        rows[pivot_row] = [x / scale for x in rows[pivot_row]]
        for r in range(len(rows)):
            if r != pivot_row and rows[r][col]:
                k = rows[r][col]
                rows[r] = [x - k * y for x, y in zip(rows[r], rows[pivot_row])]
        pivots.append(col)
        pivot_row += 1
        if pivot_row == len(rows): break
    return pivot_row, pivots, rows


def rank_one_matrix(v):
    """Whether a 9-by-9 flattening is a single b⊗c vector."""
    matrix = [v[9 * i:9 * i + 9] for i in range(9)]
    r, _, _ = rank(matrix)
    return r <= 1


def integer_rank_one_factors(v):
    """Return integer 9-vectors x,y with outer(x,y)=v, or None."""
    if any(x.denominator != 1 for x in v) or not rank_one_matrix(v): return None
    m = [int(x) for x in v]
    col = next((j for j in range(9) if any(m[9*i+j] for i in range(9))), None)
    if col is None: return None
    values = [m[9*i+col] for i in range(9)]
    g = math.gcd(*(abs(x) for x in values))
    left = tuple(x // g for x in values)
    row = next(i for i, x in enumerate(left) if x)
    right = tuple(m[9*row+j] // left[row] for j in range(9))
    return left, right


def tensor(terms):
    answer = [Fraction(0) for _ in range(9 * 9 * 9)]
    for a, b, c in terms:
        for i, x in enumerate(a):
            if not x: continue
            for j, y in enumerate(b):
                if not y: continue
                for k, z in enumerate(c):
                    if z: answer[(i * 9 + j) * 9 + k] += x * y * z
    return answer


def flatten_factorization(terms, mode):
    """Return explicit smaller CP count if pivot-factor rows give rank-one complements."""
    factors = [[t[mode] for t in terms], [t[(mode + 1) % 3] for t in terms], [t[(mode + 2) % 3] for t in terms]]
    # For mode c, preserve the other order; decomposability is invariant.
    r, _, rref = rank(factors[0])
    if r >= len(terms): return None
    pivots = []
    # Pivot columns of transpose identify independent original factor vectors.
    _, cols, _ = rank(list(zip(*factors[0])))
    basis = [factors[0][i] for i in cols]
    # Solve coordinate weights using the RREF of B^T augmented by each vector.
    bt = [list(map(Fraction, row)) for row in zip(*basis)]
    complements = [[Fraction(0) for _ in range(81)] for _ in basis]
    for t, f in enumerate(factors[0]):
        aug = [row + [Fraction(f[i])] for i, row in enumerate(bt)]
        _, _, rr = rank(aug)
        # In RREF, pivot columns of coefficient matrix give coordinate rows; solve directly.
        # Re-run a compact Gauss-Jordan solve for the r unknowns.
        eq = [row[:] for row in aug]
        prow = 0
        for col in range(len(basis)):
            p = next(i for i in range(prow, len(eq)) if eq[i][col])
            eq[prow], eq[p] = eq[p], eq[prow]
            z = eq[prow][col]; eq[prow] = [x / z for x in eq[prow]]
            for i in range(len(eq)):
                if i != prow and eq[i][col]:
                    z = eq[i][col]; eq[i] = [x - z*y for x, y in zip(eq[i], eq[prow])]
            prow += 1
        weights = [eq[i][-1] for i in range(len(basis))]
        pair = outer(factors[1][t], factors[2][t])
        for i, w in enumerate(weights):
            complements[i] = [x + w*y for x, y in zip(complements[i], pair)]
    parts = [integer_rank_one_factors(x) for x in complements]
    if all(parts):
        return {"mode": mode, "old_terms": len(terms), "new_terms": r,
                "replacement": [(tuple(map(int, basis[i])), parts[i][0], parts[i][1]) for i in range(r)]}
    return None


def neighbours(seed):
    pairs = []
    for mode in range(3):
        for i, j in itertools.combinations(range(len(seed)), 2):
            if normalize(seed[i][mode]) == normalize(seed[j][mode]):
                pairs.append((mode, i, j))
    # Fixed cursor: the first seven lexicographic legal shared-factor rewrites.
    output = []
    for mode, i, j in pairs[:7]:
        ts = [list(t) for t in seed]
        # The common factor is `mode`; use the other two factors in the
        # two-term identity (A+U)⊗B + U⊗(V-B) = A⊗B + U⊗V.
        x, y = (mode + 1) % 3, (mode + 2) % 3
        # Scale j so that its common factor equals i's exactly; compensate in
        # x, which preserves the rank-one tensor term over Q.
        scale = next(Fraction(seed[i][mode][q], seed[j][mode][q]) for q in range(9) if seed[j][mode][q])
        jj = list(seed[j]); jj[x] = tuple(scale * e for e in jj[x]); jj[mode] = seed[i][mode]
        ti, tj = list(seed[i]), jj
        ti[x] = add(ti[x], tj[x])
        tj[y] = sub(tj[y], ti[y])
        ts[i], ts[j] = ti, tj
        output.append(((mode, i, j), [tuple(t) for t in ts]))
    assert len(output) == 7, len(output)
    return output, pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("output")
    ap.add_argument("--baseline", help="write the decoded rank-23 Frontier witness")
    ap.add_argument("--candidate", help="write the first integer rank-22 candidate, if found")
    args = ap.parse_args()
    source = Path(args.source)
    started = time.time()
    seed = decode(source)
    if args.baseline:
        def matrix(v): return [list(v[3 * row:3 * row + 3]) for row in range(3)]
        Path(args.baseline).write_text(json.dumps({"terms": [
            {"a": matrix(a), "b": matrix(b), "c": matrix(c)} for a, b, c in seed
        ]}, indent=2) + "\n")
    ns, legal_pairs = neighbours(seed)
    report = {"source": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "started_unix": started, "support_sizes": [5], "excluded_support_sizes": [3, 4],
              "legal_shared_factor_pairs": legal_pairs, "neighbours": []}
    candidate = None
    for index, (move, terms) in enumerate(ns):
        assert tensor(terms) == tensor(seed), ("rewrite changed tensor", move)
        tested = constructive = low_flattening = 0
        min_flat = 5
        examples = []
        for support in itertools.combinations(range(23), 5):
            selected = [terms[i] for i in support]
            tested += 1
            ranks = [rank([t[mode] for t in selected])[0] for mode in range(3)]
            min_flat = min(min_flat, max(ranks))
            if max(ranks) >= 5:
                continue
            low_flattening += 1
            for mode in range(3):
                found = flatten_factorization(selected, mode)
                if found:
                    constructive += 1
                    examples.append({"support": support, **{k: v for k, v in found.items() if k != "replacement"}})
                    if candidate is None:
                        replacement = []
                        for first, second, third in found["replacement"]:
                            triplet = [None, None, None]
                            triplet[mode] = first
                            triplet[(mode + 1) % 3] = second
                            triplet[(mode + 2) % 3] = third
                            replacement.append(tuple(triplet))
                        candidate = {"neighbour": index, "move": move, "support": support,
                                     "mode": mode, "terms": [t for q, t in enumerate(terms) if q not in support] + replacement}
                    break
        report["neighbours"].append({"index": index, "move": move, "tested": tested,
                                     "low_flattening": low_flattening, "constructive_reductions": constructive,
                                     "minimum_max_factor_rank": min_flat, "examples": examples})
    report["elapsed_seconds"] = time.time() - started
    report["candidate"] = None if candidate is None else {k: v for k, v in candidate.items() if k != "terms"}
    report["resume_cursor"] = {"complete": True, "next_neighbour": None, "next_support": None}
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if args.candidate and candidate:
        def matrix(v): return [list(v[3 * row:3 * row + 3]) for row in range(3)]
        Path(args.candidate).write_text(json.dumps({"terms": [
            {"a": matrix(a), "b": matrix(b), "c": matrix(c)} for a, b, c in candidate["terms"]
        ]}, indent=2) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__": main()
