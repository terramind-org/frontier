#!/usr/bin/env python3
"""Exact 39-core/four-new-vertex Ramsey(5,5) neighbourhood experiment.

For every labelled triple deleted from Exoo's g55.42, freeze the induced
39-vertex graph and let all 156 new--core and six new--new edges vary.  Each
possible K5 meeting a new vertex gives a pair of CNF clauses forbidding its
two monochromatic colourings.  Output records every distinct triple, so an
interrupted run has an exact resume cursor; a timeout is explicitly separate
from UNSAT.
"""
from __future__ import annotations

import argparse, hashlib, itertools, json, platform, sys, threading, time
try:
    from pysat.solvers import Glucose4
    import pysat
except ImportError:
    Glucose4 = None
    pysat = None


def read_graph(path):
    rows = [line.strip() for line in open(path, encoding="ascii") if line.strip()]
    assert len(rows) == 42 and all(len(row) == 42 for row in rows)
    graph = [[int(bit) for bit in row] for row in rows]
    assert all(graph[i][j] == graph[j][i] and (i != j or graph[i][j] == 0)
               for i in range(42) for j in range(42))
    return graph, rows


def encode(core, nnew):
    """CNF and variable descriptions; x is true exactly for colour 1."""
    nc = len(core)
    desc = [("core", q, v) for q in range(nnew) for v in range(nc)]
    desc += [("new", q, r) for q in range(nnew) for r in range(q + 1, nnew)]
    var = {edge: i for i, edge in enumerate(desc)}
    clauses = []
    for count_new in range(1, min(nnew, 4) + 1):
        for new_set in itertools.combinations(range(nnew), count_new):
            for old_set in itertools.combinations(range(nc), 5 - count_new):
                old_edges = [core[i][j] for i, j in itertools.combinations(old_set, 2)]
                for colour in (0, 1):
                    if any(bit != colour for bit in old_edges):
                        continue
                    edges = [var[("core", q, v)] for q in new_set for v in old_set]
                    edges += [var[("new", q, r)] for q, r in itertools.combinations(new_set, 2)]
                    # At least one edge differs from colour: positive literal for 0.
                    clauses.append(tuple((edge + 1) if colour == 0 else -(edge + 1)
                                         for edge in edges))
    return clauses, desc


def rows_from_solution(core_ids, graph, desc, assignment):
    nc = len(core_ids)
    nnew = max(q for _, q, _ in desc) + 1
    n = nc + nnew
    out = [[0] * n for _ in range(n)]
    for i in range(nc):
        for j in range(nc):
            out[i][j] = graph[core_ids[i]][core_ids[j]]
    for idx, (kind, q, other) in enumerate(desc):
        if kind == "core":
            u, v = nc + q, other
        else:
            u, v = nc + q, nc + other
        out[u][v] = out[v][u] = assignment[idx]
    return ["".join(map(str, row)) for row in out]


def has_mono_k5(rows):
    return any(len({rows[i][j] for i, j in itertools.combinations(vertices, 2)}) == 1
               for vertices in itertools.combinations(range(len(rows)), 5))


def cnf_accepts(clauses, assignment):
    return all(any((assignment[abs(literal) - 1] == 1) == (literal > 0)
                   for literal in clause) for clause in clauses)


def small_exhaustive_control():
    # Three frozen vertices plus four free ones = 18 variables, 262,144 cases.
    core = [[0] * 3 for _ in range(3)]
    core[0][1] = core[1][0] = 1
    core[0][2] = core[2][0] = 0
    core[1][2] = core[2][1] = 1
    clauses, desc = encode(core, 4)
    for mask in range(1 << len(desc)):
        assignment = [(mask >> bit) & 1 for bit in range(len(desc))]
        rows = rows_from_solution(list(range(3)), core, desc, assignment)
        if cnf_accepts(clauses, assignment) == has_mono_k5(rows):
            return False, mask, len(clauses), len(desc)
    return True, 1 << len(desc), len(clauses), len(desc)


def solve_sat(clauses, seconds):
    if Glucose4 is None:
        raise RuntimeError("PySAT Glucose4 is required for bounded 162-variable instances")
    with Glucose4(bootstrap_with=clauses) as solver:
        timer = threading.Timer(seconds, solver.interrupt)
        timer.start()
        try:
            status = solver.solve_limited(expect_interrupt=True)
        finally:
            timer.cancel()
        stats = solver.accum_stats()
        decisions = int(stats.get("decisions", 0))
        if status is None:
            return None, decisions, True
        if not status:
            return None, decisions, False
        model = {literal for literal in solver.get_model() if literal > 0}
        return [1 if index + 1 in model else 0 for index in range(max(abs(x) for c in clauses for x in c))], decisions, False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("g55")
    parser.add_argument("--seconds", type=float, default=1740)
    parser.add_argument("--per-core", type=float, default=8)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    began = time.monotonic()
    graph, source_rows = read_graph(args.g55)
    good, checked, control_clauses, control_vars = small_exhaustive_control()
    assert good
    triples = list(itertools.combinations(range(42), 3))
    result = {
        "experiment": "Exoo g55.42: delete three labelled vertices, freeze 39-core, insert four unrestricted vertices",
        "fixture_sha256": hashlib.sha256(open(args.g55, "rb").read()).hexdigest(),
        "solver": "PySAT Glucose4",
        "solver_version": getattr(pysat, "__version__", None), "seed": None,
        "python": sys.version, "platform": platform.platform(),
        "scope": "lexicographic unordered triples after start; all 162 edges involving four new vertices free",
        "total_triples": len(triples), "start": args.start, "per_core_seconds": args.per_core,
        "cross_check_3core_4new": {"assignments": checked, "variables": control_vars,
                                     "clauses": control_clauses, "passed": True},
        "unsat": [], "timed_out": [], "sat": [], "decisions": 0,
        "resume_index": args.start, "elapsed_seconds": 0,
    }
    # Independent control: the three removed Exoo vertices solve the three-new CNF
    # and reproduce the fixture exactly.  This does not involve a dummy fourth vertex.
    deleted = (39, 40, 41)
    core_ids = [v for v in range(42) if v not in deleted]
    clauses, desc = encode([[graph[i][j] for j in core_ids] for i in core_ids], 3)
    planted = []
    for kind, q, other in desc:
        planted.append(graph[deleted[q]][core_ids[other]] if kind == "core"
                       else graph[deleted[q]][deleted[other]])
    reconstructed = rows_from_solution(core_ids, graph, desc, planted)
    result["planted_39_to_42"] = {"clause_count": len(clauses),
                                   "satisfies_cnf": cnf_accepts(clauses, planted),
                                   "scanner_k5_free": not has_mono_k5(reconstructed),
                                   "matches_exoo": reconstructed == source_rows}
    assert all(result["planted_39_to_42"].values())
    deadline = began + args.seconds
    for index in range(args.start, len(triples)):
        if time.monotonic() >= deadline:
            result["resume_index"] = index
            break
        deleted = triples[index]
        core_ids = [v for v in range(42) if v not in deleted]
        core = [[graph[i][j] for j in core_ids] for i in core_ids]
        clauses, desc = encode(core, 4)
        assignment, decisions, timed_out = solve_sat(clauses, min(args.per_core, deadline - time.monotonic()))
        result["decisions"] += decisions
        result["resume_index"] = index + 1
        if timed_out:
            result["timed_out"].append([index, list(deleted), len(clauses), decisions])
        elif assignment is None:
            result["unsat"].append([index, list(deleted), len(clauses), decisions])
        else:
            rows = rows_from_solution(core_ids, graph, desc, assignment)
            assert not has_mono_k5(rows)
            result["sat"].append([index, list(deleted), len(clauses), decisions, rows])
            break
    result["elapsed_seconds"] = time.monotonic() - began
    result["counts"] = {key: len(result[key]) for key in ("unsat", "timed_out", "sat")}
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"counts": result["counts"], "resume_index": result["resume_index"],
                      "elapsed_seconds": result["elapsed_seconds"], "decisions": result["decisions"]}, sort_keys=True))


if __name__ == "__main__":
    main()
