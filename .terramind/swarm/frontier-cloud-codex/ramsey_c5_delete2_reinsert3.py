#!/usr/bin/env python3
"""Exact 40-core / three-new-vertex Ramsey(5,5) neighbourhood search.

For each deletion pair of Exoo's labelled g55.42, retain its induced 40-core
and ask SAT for three unrestricted replacement vertices.  Variables are the
120 new--core and 3 new--new edges.  Every possible K5 meeting the new set
produces two forbidden monochromatic assignments (one per colour).  The
solver is a deterministic, unit-propagating DPLL, deliberately kept here so
the experiment has no unrecorded solver dependency.
"""
from __future__ import annotations

import argparse, hashlib, itertools, json, platform, sys, time, threading
try:
    from pysat.solvers import Glucose4
    import pysat
except ImportError:
    Glucose4 = None
    pysat = None


def read_graph(path):
    rows = [x.strip() for x in open(path, encoding="ascii") if x.strip()]
    assert len(rows) == 42 and all(len(r) == 42 for r in rows)
    a = [[int(x) for x in row] for row in rows]
    assert all(a[i][j] == a[j][i] and (i != j or a[i][j] == 0) for i in range(42) for j in range(42))
    return a, rows


def encode(core, nnew=3):
    """Return clauses as tuples of signed literals, and edge descriptors."""
    nc = len(core)
    # Variable x means colour 1.  First all new-to-core, then pairs of new vertices.
    desc = [("core", q, v) for q in range(nnew) for v in range(nc)] + [("new", q, r) for q in range(nnew) for r in range(q + 1, nnew)]
    vi = {d: i for i, d in enumerate(desc)}
    clauses = []
    # A clause forbids all listed variables taking colour col: (x != col) OR ...
    def forbid(literals, col):
        clauses.append(tuple((v + 1) if col == 0 else -(v + 1) for v in literals))
    # Exactly r new vertices and 5-r core vertices.
    for r in range(1, min(nnew, 4) + 1):
        for new in itertools.combinations(range(nnew), r):
            for old in itertools.combinations(range(nc), 5-r):
                old_edges = [core[i][j] for i, j in itertools.combinations(old, 2)]
                # If old internal edges are nonmonochromatic no K5 colour is possible.
                for col in (0, 1):
                    if old_edges and any(x != col for x in old_edges):
                        continue
                    variables = [vi[("core", q, v)] for q in new for v in old]
                    variables += [vi[("new", q, s)] for q, s in itertools.combinations(new, 2)]
                    forbid(variables, col)
    return clauses, desc


def solve(clauses, nvars, deadline):
    """Deterministic DPLL; returns (assignment|None, nodes, timed_out)."""
    occurrences = [[] for _ in range(nvars)]
    for ci, clause in enumerate(clauses):
        for lit in clause: occurrences[abs(lit)-1].append(ci)
    order = sorted(range(nvars), key=lambda v: -len(occurrences[v]))
    nodes = 0
    timed = False
    def rec(assign):
        nonlocal nodes, timed
        nodes += 1
        if time.monotonic() >= deadline:
            timed = True; return None
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                sat = False; unknown = 0; last = 0
                for lit in clause:
                    val = assign[abs(lit)-1]
                    if val < 0: unknown += 1; last = lit
                    elif bool(val) == (lit > 0): sat = True; break
                if sat: continue
                if unknown == 0: return None
                if unknown == 1:
                    v = abs(last)-1; need = 1 if last > 0 else 0
                    if assign[v] >= 0 and assign[v] != need: return None
                    if assign[v] < 0: assign[v] = need; changed = True
        v = next((x for x in order if assign[x] < 0), None)
        if v is None: return assign
        for value in (0, 1):
            child = assign[:]; child[v] = value
            got = rec(child)
            if got is not None or timed: return got
        return None
    answer = rec([-1] * nvars)
    return answer, nodes, timed


def solve_sat(clauses, nvars, seconds):
    """Glucose4 call with an interrupt timer; None status means timeout."""
    if Glucose4 is None:
        return solve(clauses, nvars, time.monotonic() + seconds)
    with Glucose4(bootstrap_with=clauses) as solver:
        timer = threading.Timer(seconds, solver.interrupt)
        timer.start()
        try:
            status = solver.solve_limited(expect_interrupt=True)
        finally:
            timer.cancel()
        stats = solver.accum_stats()
        nodes = int(stats.get('decisions', 0))
        if status is None: return None, nodes, True
        if not status: return None, nodes, False
        model = set(x for x in solver.get_model() if x > 0)
        return [1 if i + 1 in model else 0 for i in range(nvars)], nodes, False


def graph_from_solution(core_ids, a, deleted, desc, sol):
    rows = [[a[i][j] for j in core_ids] for i in core_ids]
    nnew = max(q for _, q, _ in desc) + 1
    for _ in range(nnew): rows.append([])
    n = len(rows)
    out = [[0] * n for _ in range(n)]
    for i in range(len(core_ids)):
        for j in range(len(core_ids)): out[i][j] = rows[i][j]
    for idx, d in enumerate(desc):
        kind, q, x = d
        if kind == "core":
            u, v = len(core_ids)+q, x
        else:
            u, v = len(core_ids)+q, len(core_ids)+x
        out[u][v] = out[v][u] = sol[idx]
    return ["".join(map(str, row)) for row in out]


def has_mono_k5(rows):
    for vs in itertools.combinations(range(len(rows)), 5):
        vals = {rows[i][j] for i, j in itertools.combinations(vs, 2)}
        if len(vals) == 1: return True
    return False


def exhaustive_encoder_control():
    # 5-core + 3 new = 18 variables. Compare all assignments with a direct K5 scan.
    core = [[0] * 5 for _ in range(5)]
    for i, j in itertools.combinations(range(5), 2):
        core[i][j] = core[j][i] = (3*i + j + 1) & 1
    clauses, desc = encode(core)
    for mask in range(1 << len(desc)):
        sol = [(mask >> i) & 1 for i in range(len(desc))]
        cnf = all(any((sol[abs(l)-1] == 1) == (l > 0) for l in c) for c in clauses)
        rows = graph_from_solution(list(range(5)), core, (), desc, sol)
        if cnf == has_mono_k5(rows):
            return False, mask, len(clauses)
    return True, 1 << len(desc), len(clauses)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('g55'); ap.add_argument('--seconds', type=float, default=1740)
    ap.add_argument('--per-core', type=float, default=20); ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--out', required=True)
    ns = ap.parse_args(); began = time.monotonic()
    a, source_rows = read_graph(ns.g55)
    good, control_count, control_clauses = exhaustive_encoder_control()
    assert good
    result = {"fixture_sha256": hashlib.sha256(open(ns.g55, 'rb').read()).hexdigest(),
              "solver": "PySAT Glucose4" if Glucose4 else "embedded deterministic unit-propagating DPLL", "solver_version": getattr(pysat, '__version__', None), "seed": None,
              "python": sys.version, "platform": platform.platform(),
              "cross_check_5core_3new": {"assignments": control_count, "clauses": control_clauses, "passed": True},
              "scope": "all unordered deleted pairs in lexicographic order after start; 40-core plus 3 new vertices", 
              "total_pairs": 861, "start": ns.start, "exhausted_unsat": 0, "timed_out": 0, "sat": 0,
              "nodes": 0, "completed_pairs": [], "timed_pairs": [], "resume_index": ns.start, "elapsed_seconds": 0}
    # Positive control on the final two vertices, preserving their original incidences.
    deleted = (40, 41); core_ids = [x for x in range(42) if x not in deleted]
    clauses, desc = encode([[a[i][j] for j in core_ids] for i in core_ids], nnew=2)
    planted = []
    for kind, q, old in desc:
        if kind == "core": planted.append(a[deleted[q]][core_ids[old]])
        else: planted.append(a[deleted[q]][deleted[old]])
    reconstructed = graph_from_solution(core_ids, a, deleted, desc, planted)
    result['planted_40_to_42'] = {"clause_count": len(clauses), "satisfies_cnf": all(any((planted[abs(l)-1] == 1) == (l > 0) for l in c) for c in clauses), "is_42_valid": not has_mono_k5(reconstructed), "matches_exoo": reconstructed == source_rows}
    pairs = list(itertools.combinations(range(42), 2))
    end = began + ns.seconds
    for pos in range(ns.start, len(pairs)):
        if time.monotonic() >= end: result['resume_index'] = pos; break
        pair = pairs[pos]; core_ids = [x for x in range(42) if x not in pair]
        core = [[a[i][j] for j in core_ids] for i in core_ids]
        clauses, desc = encode(core)
        sol, nodes, timed = solve_sat(clauses, len(desc), min(end - time.monotonic(), ns.per_core))
        result['nodes'] += nodes
        if timed:
            result['timed_out'] += 1; result['timed_pairs'].append([pos, list(pair)]); result['resume_index'] = pos + 1
        elif sol is None:
            result['exhausted_unsat'] += 1; result['completed_pairs'].append([pos, list(pair), len(clauses)]) ; result['resume_index'] = pos + 1
        else:
            rows = graph_from_solution(core_ids, a, pair, desc, sol)
            assert not has_mono_k5(rows)
            result['sat'] += 1; result['candidate'] = {"pair_index": pos, "deleted": pair, "adjacency": rows}; result['resume_index'] = pos + 1; break
    result['elapsed_seconds'] = time.monotonic() - began
    with open(ns.out, 'w') as f: json.dump(result, f, indent=2, sort_keys=True); f.write('\n')
    print(json.dumps({k: result[k] for k in ('exhausted_unsat','timed_out','sat','resume_index','elapsed_seconds','nodes')}, sort_keys=True))


if __name__ == '__main__': main()
