#!/usr/bin/env python3
"""Exact Exoo g55.42 39-core/four-new-vertex Ramsey(5,5) search.

Enumerates labelled deleted triples in itertools.combinations(42, 3) order.
Each finished case is recorded as SAT, UNSAT, or timeout; the resume cursor is
therefore not an assertion about cases that were never visited.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, platform, sys, threading, time
import pysat
from pysat.solvers import Glucose4

def graph_at(path):
    rows = [x.strip() for x in open(path, encoding="ascii") if x.strip()]
    assert len(rows) == 42 and all(len(x) == 42 for x in rows)
    g = [[int(b) for b in row] for row in rows]
    assert all(g[i][j] == g[j][i] and (i != j or not g[i][j])
               for i in range(42) for j in range(42))
    return g, rows

def encode(core, nnew):
    nc = len(core)
    desc = [("core", q, v) for q in range(nnew) for v in range(nc)]
    desc += [("new", q, r) for q in range(nnew) for r in range(q + 1, nnew)]
    var = {x: i for i, x in enumerate(desc)}
    cs = []
    for k in range(1, min(4, nnew) + 1):
        for ns in itertools.combinations(range(nnew), k):
            for os in itertools.combinations(range(nc), 5 - k):
                old = [core[i][j] for i, j in itertools.combinations(os, 2)]
                for colour in (0, 1):
                    if any(x != colour for x in old):
                        continue
                    vs = [var[("core", q, v)] for q in ns for v in os]
                    vs += [var[("new", q, r)] for q, r in itertools.combinations(ns, 2)]
                    cs.append(tuple((v + 1) if colour == 0 else -(v + 1) for v in vs))
    return cs, desc

def render(ids, source, desc, bits):
    nc, n = len(ids), len(ids) + max(q for _, q, _ in desc) + 1
    out = [[0] * n for _ in range(n)]
    for i in range(nc):
        for j in range(nc): out[i][j] = source[ids[i]][ids[j]]
    for i, (kind, q, other) in enumerate(desc):
        u, v = (nc + q, other) if kind == "core" else (nc + q, nc + other)
        out[u][v] = out[v][u] = bits[i]
    return ["".join(map(str, r)) for r in out]

def no_k5(rows):
    return not any(len({rows[i][j] for i, j in itertools.combinations(s, 2)}) == 1
                   for s in itertools.combinations(range(len(rows)), 5))

def accepts(cs, bits):
    return all(any((bits[abs(x)-1] == 1) == (x > 0) for x in c) for c in cs)

def exhaustive_control():
    core = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    cs, desc = encode(core, 4)
    for mask in range(1 << len(desc)):
        bits = [(mask >> i) & 1 for i in range(len(desc))]
        assert accepts(cs, bits) == no_k5(render(list(range(3)), core, desc, bits))
    return {"assignments": 1 << len(desc), "variables": len(desc),
            "clauses": len(cs), "passed": True}

def solve(cs, seconds):
    with Glucose4(bootstrap_with=cs) as s:
        t = threading.Timer(seconds, s.interrupt); t.start()
        try: status = s.solve_limited(expect_interrupt=True)
        finally: t.cancel()
        decisions = int(s.accum_stats().get("decisions", 0))
        if status is None: return None, decisions, True
        if not status: return None, decisions, False
        model = {x for x in s.get_model() if x > 0}
        return [int(i + 1 in model) for i in range(max(abs(x) for c in cs for x in c))], decisions, False

def main():
    p = argparse.ArgumentParser(); p.add_argument("g55"); p.add_argument("--out", required=True)
    p.add_argument("--start", type=int, default=0); p.add_argument("--seconds", type=float, default=1740)
    p.add_argument("--per-core", type=float, default=8); a = p.parse_args()
    began = time.monotonic(); g, original = graph_at(a.g55); triples = list(itertools.combinations(range(42), 3))
    result = {"experiment": "Exoo g55.42: delete three labelled vertices, freeze 39-core, insert four unrestricted vertices",
      "fixture_sha256": hashlib.sha256(open(a.g55, "rb").read()).hexdigest(), "solver": "PySAT Glucose4",
      "solver_version": pysat.__version__, "seed": None, "python": sys.version, "platform": platform.platform(),
      "scope": "lexicographic unordered triples after start; all 162 edges involving four new vertices free",
      "total_triples": len(triples), "start": a.start, "per_core_seconds": a.per_core,
      "cross_check_3core_4new": exhaustive_control(), "unsat": [], "timed_out": [], "sat": [],
      "decisions": 0, "resume_index": a.start, "elapsed_seconds": 0}
    deleted = (39, 40, 41); ids = [v for v in range(42) if v not in deleted]; cs, desc = encode([[g[i][j] for j in ids] for i in ids], 3)
    planted = [g[deleted[q]][ids[o]] if kind == "core" else g[deleted[q]][deleted[o]] for kind, q, o in desc]
    rebuilt = render(ids, g, desc, planted)
    result["planted_39_to_42"] = {"clause_count": len(cs), "satisfies_cnf": accepts(cs, planted), "scanner_k5_free": no_k5(rebuilt), "matches_exoo": rebuilt == original}
    assert all(result["planted_39_to_42"].values())
    deadline = began + a.seconds
    for index in range(a.start, len(triples)):
        if time.monotonic() >= deadline: result["resume_index"] = index; break
        deleted = triples[index]; ids = [v for v in range(42) if v not in deleted]
        cs, desc = encode([[g[i][j] for j in ids] for i in ids], 4)
        bits, dec, timeout = solve(cs, min(a.per_core, deadline - time.monotonic())); result["decisions"] += dec; result["resume_index"] = index + 1
        if timeout: result["timed_out"].append([index, list(deleted), len(cs), dec])
        elif bits is None: result["unsat"].append([index, list(deleted), len(cs), dec])
        else:
            rows = render(ids, g, desc, bits); assert no_k5(rows)
            result["sat"].append([index, list(deleted), len(cs), dec, rows]); break
    result["elapsed_seconds"] = time.monotonic() - began; result["counts"] = {x: len(result[x]) for x in ("unsat", "timed_out", "sat")}
    with open(a.out, "w", encoding="utf-8") as f: json.dump(result, f, indent=2, sort_keys=True); f.write("\n")
    print(json.dumps({"counts": result["counts"], "resume_index": result["resume_index"], "elapsed_seconds": result["elapsed_seconds"], "decisions": result["decisions"]}, sort_keys=True))
if __name__ == "__main__": main()
