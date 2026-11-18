#!/usr/bin/env python3
"""R(4,6) replacement search: delete four vertices, insert five jointly.

The base is Exoo's 35-vertex r4.6.35 graph.  A labelled four-vertex deletion
leaves a fixed 31-core; all 165 edges touching five new vertices are SAT
variables.  The CNF forbids colour-0 K4s and colour-1 K6s separately.
Results are append-free JSON with a precise lexicographic resume cursor.
"""
from __future__ import annotations

import argparse, hashlib, itertools, json, os, platform, sys, threading, time
from pysat.solvers import Glucose4
import pysat


def read_graph(path):
    rows = [line.strip() for line in open(path, encoding="ascii") if line.strip()]
    assert len(rows) == 35 and all(len(row) == 35 and set(row) <= {"0", "1"} for row in rows)
    a = [[int(bit) for bit in row] for row in rows]
    assert all(a[i][i] == 0 and a[i][j] == a[j][i] for i in range(35) for j in range(35))
    return a, rows


def has_forbidden(rows):
    n = len(rows)
    z4 = sum(all(rows[i][j] == "0" for i, j in itertools.combinations(vs, 2))
             for vs in itertools.combinations(range(n), 4))
    o6 = sum(all(rows[i][j] == "1" for i, j in itertools.combinations(vs, 2))
             for vs in itertools.combinations(range(n), 6))
    return z4, o6


def encode(core, nnew):
    """Return clauses and edge descriptors; variable true means colour 1."""
    nc = len(core)
    desc = [("cross", q, v) for q in range(nnew) for v in range(nc)]
    desc += [("new", q, r) for q in range(nnew) for r in range(q + 1, nnew)]
    var = {edge: i + 1 for i, edge in enumerate(desc)}
    clauses = []
    for size, colour in ((4, 0), (6, 1)):
        for count_new in range(1, min(size, nnew) + 1):
            for new_set in itertools.combinations(range(nnew), count_new):
                for old_set in itertools.combinations(range(nc), size - count_new):
                    if any(core[i][j] != colour for i, j in itertools.combinations(old_set, 2)):
                        continue
                    free = [var[("cross", q, v)] for q in new_set for v in old_set]
                    free += [var[("new", q, r)] for q, r in itertools.combinations(new_set, 2)]
                    # A 0-clique needs a 1; a 1-clique needs a 0.
                    clauses.append(tuple(edge if colour == 0 else -edge for edge in free))
    return clauses, desc


def cnf_accepts(clauses, assignment):
    return all(any((assignment[abs(lit) - 1] == 1) == (lit > 0) for lit in clause)
               for clause in clauses)


def rows_from_assignment(core_ids, original, desc, assignment):
    nc, nnew = len(core_ids), max(q for _, q, _ in desc) + 1
    out = [[0] * (nc + nnew) for _ in range(nc + nnew)]
    for i in range(nc):
        for j in range(nc): out[i][j] = original[core_ids[i]][core_ids[j]]
    for bit, (kind, q, other) in zip(assignment, desc):
        u, v = (nc + q, other) if kind == "cross" else (nc + q, nc + other)
        out[u][v] = out[v][u] = bit
    return ["".join(map(str, row)) for row in out]


def exhaustive_encoder_control():
    # 2-core + 4 new = 6 vertices, 14 variables: all 16,384 assignments.
    core = [[0, 1], [1, 0]]
    clauses, desc = encode(core, 4)
    for mask in range(1 << len(desc)):
        assignment = [(mask >> i) & 1 for i in range(len(desc))]
        rows = rows_from_assignment([0, 1], core, desc, assignment)
        actual = has_forbidden(rows) == (0, 0)
        assert cnf_accepts(clauses, assignment) == actual
    return {"vertices": 6, "variables": len(desc), "assignments": 1 << len(desc),
            "clauses": len(clauses), "passed": True}


def planted_control(a, rows):
    deleted = (31, 32, 33, 34)
    core_ids = [v for v in range(35) if v not in deleted]
    core = [[a[i][j] for j in core_ids] for i in core_ids]
    clauses, desc = encode(core, 4)
    assignment = []
    for kind, q, other in desc:
        assignment.append(a[deleted[q]][core_ids[other]] if kind == "cross" else a[deleted[q]][deleted[other]])
    rebuilt = rows_from_assignment(core_ids, a, desc, assignment)
    return {"deleted": list(deleted), "clauses": len(clauses),
            "satisfies_cnf": cnf_accepts(clauses, assignment), "matches_fixture": rebuilt == rows,
            "forbidden": list(has_forbidden(rebuilt))}


def solve(clauses, seconds):
    with Glucose4(bootstrap_with=clauses) as solver:
        timer = None
        if seconds > 0:
            timer = threading.Timer(seconds, solver.interrupt)
            timer.start()
        limited = solver.solve_limited(expect_interrupt=True)
        if timer is not None:
            timer.cancel()
        solver.clear_interrupt()
        stats = solver.accum_stats()
        if limited is None: return "UNKNOWN", None, int(stats.get("decisions", 0))
        if not limited: return "UNSAT", None, int(stats.get("decisions", 0))
        model = {x for x in solver.get_model() if x > 0}
        return "SAT", model, int(stats.get("decisions", 0))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("fixture")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--count", type=int, default=64)
    p.add_argument("--case-timeout", type=float, default=1.0,
                   help="seconds permitted for each formula; timeout is recorded as UNKNOWN")
    p.add_argument("--wall-seconds", type=float, default=0.0,
                   help="stop before starting a case once this run budget is spent (0 means no budget)")
    p.add_argument("--out", required=True)
    p.add_argument("--baseline-witness", help="write the validated input as Frontier JSON")
    args = p.parse_args()
    # The output path identifies one deterministic cursor range.  Refuse a
    # second writer rather than letting two controllers collide on .tmp.
    lock_path = args.out + ".lock"
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise SystemExit(f"refusing a second writer; lock exists: {lock_path}")
    with os.fdopen(lock_fd, "w", encoding="ascii") as lock_file:
        lock_file.write(f"pid={os.getpid()}\\n")
    began = time.monotonic(); a, rows = read_graph(args.fixture)
    assert has_forbidden(rows) == (0, 0)
    if args.baseline_witness:
        with open(args.baseline_witness, "w", encoding="utf8") as f:
            json.dump({"n": 35, "adjacency": rows}, f, indent=2)
            f.write("\n")
    cases = list(itertools.combinations(range(35), 4))
    result = {"experiment": "R(4,6): delete four labelled vertices from Exoo r4.6.35; insert five unrestricted vertices",
              "fixture_sha256": hashlib.sha256(open(args.fixture, "rb").read()).hexdigest(),
              "source_n": 35, "target_n": 36, "core_n": 31, "new_vertices": 5,
              "variables": 165, "total_cases": len(cases), "start": args.start, "requested_count": args.count,
              "case_timeout_seconds": args.case_timeout, "wall_seconds": args.wall_seconds,
              "python": sys.version, "platform": platform.platform(), "pysat": pysat.__version__,
              "baseline_forbidden": list(has_forbidden(rows)), "encoder_control": exhaustive_encoder_control(),
              "planted_control": planted_control(a, rows), "cases": [], "next_cursor": args.start}
    assert all(result["planted_control"][x] for x in ("satisfies_cnf", "matches_fixture"))
    assert result["planted_control"]["forbidden"] == [0, 0]
    def checkpoint():
        result["elapsed_seconds"] = time.monotonic() - began
        temporary = args.out + ".tmp"
        with open(temporary, "w", encoding="utf8") as f:
            json.dump(result, f, indent=2, sort_keys=True); f.write("\n")
        os.replace(temporary, args.out)

    try:
        for index in range(args.start, min(args.start + args.count, len(cases))):
            if args.wall_seconds and time.monotonic() - began >= args.wall_seconds:
                break
            deleted = cases[index]; ids = [v for v in range(35) if v not in deleted]
            core = [[a[i][j] for j in ids] for i in ids]
            clauses, desc = encode(core, 5)
            status, model, decisions = solve(clauses, args.case_timeout)
            item = {"index": index, "deleted": list(deleted), "clauses": len(clauses), "status": status, "decisions": decisions}
            if status == "SAT":
                assignment = [int(i + 1 in model) for i in range(len(desc))]
                candidate = rows_from_assignment(ids, a, desc, assignment)
                item["forbidden"] = list(has_forbidden(candidate)); item["witness"] = candidate
                assert item["forbidden"] == [0, 0]
                result["cases"].append(item); result["next_cursor"] = index + 1; checkpoint(); break
            result["cases"].append(item); result["next_cursor"] = index + 1
            checkpoint()
        result["elapsed_seconds"] = time.monotonic() - began
        result["counts"] = {s: sum(x["status"] == s for x in result["cases"]) for s in ("SAT", "UNSAT", "UNKNOWN")}
        checkpoint()
        print(json.dumps({"counts": result["counts"], "next_cursor": result["next_cursor"], "elapsed_seconds": result["elapsed_seconds"]}, sort_keys=True))
    finally:
        os.unlink(lock_path)


if __name__ == "__main__": main()
