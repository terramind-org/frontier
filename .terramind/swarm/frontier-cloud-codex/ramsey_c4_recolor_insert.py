#!/usr/bin/env python3
"""Exact local recolour-and-insert experiment around Exoo's g55.42.

For a fixed 42-vertex graph, an admissible 43rd vertex is a satisfying
assignment to one Boolean variable per incident edge.  Every monochromatic
K4 produces one four-literal forbidden pattern.  This script uses exhaustive
unit-propagating DPLL for that small SAT instance.  The two-flip stage first
filters all C(861,2) flips exactly using every K5 of the original graph, then
solves the remaining extension instances until its explicit time budget.
"""
from __future__ import annotations

import argparse, hashlib, itertools, json, time


def load(path):
    rows = [line.strip() for line in open(path, encoding="ascii") if line.strip()]
    assert len(rows) == 42 and all(len(r) == 42 and set(r) <= {"0", "1"} for r in rows)
    a = [[int(x) for x in row] for row in rows]
    assert all(a[i][i] == 0 and a[i][j] == a[j][i] for i in range(42) for j in range(42))
    return a, rows


def setup(a):
    edges = [(i, j) for i in range(42) for j in range(i + 1, 42)]
    index = {e: k for k, e in enumerate(edges)}
    k4 = []
    k5 = []
    for vs in itertools.combinations(range(42), 4):
        es = tuple(index[(i, j)] for i, j in itertools.combinations(vs, 2))
        k4.append((vs, es))
    for vs in itertools.combinations(range(42), 5):
        mask = 0
        for i, j in itertools.combinations(vs, 2): mask |= 1 << index[(i, j)]
        k5.append(mask)
    bits = sum(a[i][j] << index[(i, j)] for i, j in edges)
    return edges, k4, k5, bits


def mono_k4(bits, k4):
    clauses = []
    for vs, es in k4:
        ones = sum((bits >> e) & 1 for e in es)
        if ones == 0 or ones == 6:
            clauses.append((vs, 1 if ones == 6 else 0))
    return clauses


def dpll(clauses, n=42):
    by_v = [[] for _ in range(n)]
    for ci, (vs, _) in enumerate(clauses):
        for v in vs: by_v[v].append(ci)
    order = sorted(range(n), key=lambda v: -len(by_v[v]))
    nodes = 0
    def rec(assign):
        nonlocal nodes
        nodes += 1
        changed = True
        while changed:
            changed = False
            for vs, forbidden in clauses:
                hit = sum(assign[v] == forbidden for v in vs)
                unknown = [v for v in vs if assign[v] < 0]
                if hit == 4: return None
                if hit == 3 and len(unknown) == 1:
                    v = unknown[0]
                    need = 1 - forbidden
                    if assign[v] >= 0 and assign[v] != need: return None
                    if assign[v] < 0:
                        assign[v] = need
                        changed = True
        v = next((v for v in order if assign[v] < 0), None)
        if v is None: return assign
        for value in (0, 1):
            child = assign[:]
            child[v] = value
            got = rec(child)
            if got is not None: return got
        return None
    answer = rec([-1] * n)
    return answer, nodes


def no_mono_k5(bits, k5):
    for mask in k5:
        ones = (bits & mask).bit_count()
        if ones == 0 or ones == 10: return False
    return True


def extend(bits, k4):
    clauses = mono_k4(bits, k4)
    sol, nodes = dpll(clauses)
    return sol, nodes, len(clauses), sum(c == 0 for _, c in clauses), sum(c == 1 for _, c in clauses)


def witness(rows, edges, solution=None):
    out = rows[:]
    if solution is not None:
        out = [r + str(solution[i]) for i, r in enumerate(rows)]
        out.append("".join(str(x) for x in solution) + "0")
    return {"n": len(out), "adjacency": out}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("g55")
    p.add_argument("--seconds", type=float, default=1500)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    started = time.monotonic()
    a, rows = load(args.g55)
    edges, k4, k5, bits = setup(a)
    result = {"sha256": hashlib.sha256(open(args.g55, "rb").read()).hexdigest(), "edges": len(edges)}
    assert no_mono_k5(bits, k5)
    fixed = extend(bits, k4)
    result["fixed_extension"] = {"sat": fixed[0] is not None, "nodes": fixed[1], "clauses": fixed[2], "zero": fixed[3], "one": fixed[4]}
    # Positive control: remove vertex 41 and recover an incident-edge assignment.
    core = [row[:41] for row in a[:41]]
    # Reuse a generic 41-variable constraint calculation for the planted core.
    clauses41 = []
    for vs in itertools.combinations(range(41), 4):
        vals = [core[i][j] for i, j in itertools.combinations(vs, 2)]
        if len(set(vals)) == 1: clauses41.append((vs, vals[0]))
    planted, planted_nodes = dpll(clauses41, 41)
    result["planted_42_recovery"] = {"sat": planted is not None, "nodes": planted_nodes, "clauses": len(clauses41), "matches_exoo_incidence": planted == [a[i][41] for i in range(41)] if planted else False}
    # Exact one-flip pass.
    one = {"total": len(edges), "rejected_k5": 0, "solved_unsat": 0, "solved_sat": 0, "dpll_nodes": 0}
    admissible_one = []
    for e in range(len(edges)):
        changed = bits ^ (1 << e)
        if not no_mono_k5(changed, k5): one["rejected_k5"] += 1; continue
        sol, nodes, clauses, z, o = extend(changed, k4)
        one["dpll_nodes"] += nodes
        if sol is None: one["solved_unsat"] += 1
        else:
            one["solved_sat"] += 1
            admissible_one.append((e, sol))
    result["one_flip"] = one
    # For every two-flip pair, identify K5-invalid partners without checking pairs one by one.
    # A target-colour K5 has all of its original mismatching edges flipped and no matching edge flipped.
    all_edges = (1 << len(edges)) - 1
    forbidden = [0] * len(edges)
    for mask in k5:
        ones = bits & mask
        for mismatch in (ones, mask ^ ones):
            c = mismatch.bit_count()
            if c == 1:
                f = mismatch.bit_length() - 1
                forbidden[f] |= all_edges ^ mask
            elif c == 2:
                lo = mismatch & -mismatch
                hi = mismatch ^ lo
                i, j = lo.bit_length() - 1, hi.bit_length() - 1
                forbidden[i] |= 1 << j; forbidden[j] |= 1 << i
    two = {"total": len(edges) * (len(edges)-1) // 2, "rejected_k5": 0, "completed_unsat": 0, "completed_sat": 0, "timed_out_unstarted": 0, "dpll_nodes": 0}
    candidates = []
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            if ((forbidden[i] >> j) & 1) or ((forbidden[j] >> i) & 1): two["rejected_k5"] += 1
            else: candidates.append((i, j))
    for pos, (i, j) in enumerate(candidates):
        if time.monotonic() - started >= args.seconds:
            two["timed_out_unstarted"] = len(candidates) - pos
            break
        changed = bits ^ (1 << i) ^ (1 << j)
        # A direct check asserts the incremental K5 filter before solving.
        assert no_mono_k5(changed, k5)
        sol, nodes, clauses, z, o = extend(changed, k4)
        two["dpll_nodes"] += nodes
        if sol is None: two["completed_unsat"] += 1
        else:
            two["completed_sat"] += 1
            result["candidate"] = {"flips": [edges[i], edges[j]], "extension": sol}
            break
    result["two_flip"] = two
    result["elapsed_seconds"] = time.monotonic() - started
    with open(args.out, "w", encoding="utf8") as f: json.dump(result, f, indent=2, sort_keys=True); f.write("\n")
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__": main()
