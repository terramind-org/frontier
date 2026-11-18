#!/usr/bin/env python3
"""Exact rational-factor test of a deterministic sample from stored Sun traces.

This deliberately consumes already-recorded low-flattening trace entries.  It
does not enumerate supports: each chosen (neighbour, support_index) is decoded
from an existing trace and checked once.  The predecessor's integer recovery
rejects a nonintegral complementary flattening even when it is rank one over Q;
this file adds the corresponding exact-Q recovery and records both outcomes.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path


def atomic(path: Path, value):
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)


def load_prior(path: Path):
    spec = importlib.util.spec_from_file_location("prior_screen", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def qtext(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def rational_rank_one_factors(prior, v):
    """Return exact Q factors x,y with outer(x,y)=v, or None."""
    if not prior.rank_one_matrix(v):
        return None
    m = [Fraction(x) for x in v]
    col = next((j for j in range(9) if any(m[9 * i + j] for i in range(9))), None)
    if col is None:
        return None
    left = tuple(m[9 * i + col] for i in range(9))
    row = next(i for i, x in enumerate(left) if x)
    right = tuple(m[9 * row + j] / left[row] for j in range(9))
    assert tuple(left[i] * right[j] for i in range(9) for j in range(9)) == tuple(m)
    return left, right


def rational_factorization(prior, terms, mode):
    factors = [[t[mode] for t in terms], [t[(mode + 1) % 3] for t in terms],
               [t[(mode + 2) % 3] for t in terms]]
    r, _, _ = prior.rank(factors[0])
    if r >= len(terms):
        return None
    _, cols, _ = prior.rank(list(zip(*factors[0])))
    basis = [factors[0][i] for i in cols]
    bt = [list(map(Fraction, row)) for row in zip(*basis)]
    complements = [[Fraction(0) for _ in range(81)] for _ in basis]
    for t, f in enumerate(factors[0]):
        eq = [row + [Fraction(f[i])] for i, row in enumerate(bt)]
        prow = 0
        for col in range(len(basis)):
            pivot = next(i for i in range(prow, len(eq)) if eq[i][col])
            eq[prow], eq[pivot] = eq[pivot], eq[prow]
            z = eq[prow][col]
            eq[prow] = [x / z for x in eq[prow]]
            for i in range(len(eq)):
                if i != prow and eq[i][col]:
                    z = eq[i][col]
                    eq[i] = [x - z * y for x, y in zip(eq[i], eq[prow])]
            prow += 1
        weights = [eq[i][-1] for i in range(len(basis))]
        pair = prior.outer(factors[1][t], factors[2][t])
        for i, w in enumerate(weights):
            complements[i] = [x + w * y for x, y in zip(complements[i], pair)]
    parts = [rational_rank_one_factors(prior, x) for x in complements]
    if not all(parts):
        return None
    replacement = [(basis[i], parts[i][0], parts[i][1]) for i in range(r)]
    # This verifies the exact selected-subtensor identity, independent of any
    # serialization or later Frontier checker.
    assert prior.tensor(terms) == prior.tensor(replacement)
    return {"mode": mode, "old_terms": len(terms), "new_terms": r,
            "replacement": replacement,
            "nonintegral_complement": any(x.denominator != 1 for p in parts for v in p for x in v)}


def synthetic_control(prior):
    z = (Fraction(0),) * 9
    e0 = (Fraction(1),) + z[1:]
    e1 = (Fraction(0), Fraction(1)) + z[2:]
    # Four different b/c products combine to
    # (e0 + e1/2) ⊗ (e0 + e1/2), while the a-factors make the
    # complementary coefficients 1, 1/2, 1/2, 1/4.  It is therefore not a
    # per-summand projective rescaling.
    terms = [
        (tuple(4 * x for x in e0), e0, e0),
        (tuple(2 * x for x in e0), e0, e1),
        (tuple(2 * x for x in e0), e1, e0),
        (e0, e1, e1),
    ]
    old = prior.flatten_factorization(terms, 0)
    new = rational_factorization(prior, terms, 0)
    assert old is None
    assert new is not None and new["new_terms"] == 1 and new["nonintegral_complement"]
    return {"old_integral_result": None, "new_rational_terms": new["new_terms"],
            "identity_verified": True,
            "identity": "4e0⊗e0⊗e0 + 2e0⊗e0⊗e1 + 2e0⊗e1⊗e0 + e0⊗e1⊗e1 = 4e0⊗(e0+e1/2)⊗(e0+e1/2)",
            "replacement": [[qtext(x) for x in v] for v in new["replacement"][0]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prior", required=True, type=Path)
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--trace", action="append", type=Path, required=True)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--sample-per-neighbour", type=int, default=32)
    args = ap.parse_args()
    prior = load_prior(args.prior)
    seed = prior.decode(args.source)
    ns, _ = prior.neighbours(seed)
    control = synthetic_control(prior)
    buckets = {i: [] for i in range(len(ns))}
    trace_hashes = {}
    for path in args.trace:
        trace_hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        for line in path.read_text().splitlines():
            row = json.loads(line)
            if row["low_flattening"]:
                key = f"sun-q-c14-v1:{row['neighbour']}:{row['support_index']}"
                buckets[row["neighbour"]].append((hashlib.sha256(key.encode()).hexdigest(), row))
    selected = []
    for neighbour, rows in buckets.items():
        selected.extend(row for _, row in sorted(rows)[:args.sample_per_neighbour])
    selected.sort(key=lambda row: (row["neighbour"], row["support_index"]))
    tested = []
    candidate = None
    for row in selected:
        _, terms = ns[row["neighbour"]]
        support = tuple(row["support"])
        chosen = [terms[i] for i in support]
        old = [prior.flatten_factorization(chosen, mode) is not None for mode in range(3)]
        new = [rational_factorization(prior, chosen, mode) for mode in range(3)]
        found = next((x for x in new if x), None)
        tested.append({"neighbour": row["neighbour"], "support_index": row["support_index"],
                       "support": list(support), "old_integral_modes": old,
                       "new_rational_modes": [x is not None for x in new],
                       "new_terms": None if found is None else found["new_terms"]})
        if found and found["new_terms"] <= 6 and candidate is None:
            mode = found["mode"]
            replacement = []
            for first, second, third in found["replacement"]:
                triplet = [None, None, None]
                triplet[mode] = first
                triplet[(mode + 1) % 3] = second
                triplet[(mode + 2) % 3] = third
                replacement.append(tuple(triplet))
            candidate = {"neighbour": row["neighbour"], "support": list(support), "mode": mode,
                         "new_terms": found["new_terms"], "terms": [t for i, t in enumerate(terms) if i not in support] + replacement}
    report = {"method": "exact rational complementary-flattening recovery",
              "old_criterion": "requires integer complementary 9-vectors before rank-one recovery",
              "sample_rule": "For each neighbour, sort stored low-flattening trace rows by SHA-256(sun-q-c14-v1:neighbour:support_index) and retain the first N.",
              "sample_per_neighbour": args.sample_per_neighbour, "trace_sha256": trace_hashes,
              "sample_counts": {str(i): sum(1 for row in selected if row["neighbour"] == i) for i in range(len(ns))},
              "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
              "prior_sha256": hashlib.sha256(args.prior.read_bytes()).hexdigest(),
              "synthetic_positive_control": control, "tested_count": len(tested),
              "tested": tested,
              "candidate": None if candidate is None else {k: v for k, v in candidate.items() if k != "terms"},
              "cursor": {"complete": True, "next": None}}
    atomic(args.output, report)
    if candidate:
        def matrix(v): return [[qtext(x) for x in v[3*i:3*i+3]] for i in range(3)]
        atomic(args.output.with_name("rational-candidate-witness.json"), {"terms": [
            {"a": matrix(a), "b": matrix(b), "c": matrix(c)} for a, b, c in candidate["terms"]]})
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
