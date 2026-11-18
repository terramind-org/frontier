#!/usr/bin/env python3
"""Resume the frozen-core search while atomically saving every finished case."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import sys
import time


def load_encoder(path):
    spec = importlib.util.spec_from_file_location("ramsey_encoder", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_atomic(path, value):
    temporary = f"{path}.tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("encoder")
    parser.add_argument("g55")
    parser.add_argument("--out", required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--per-core", type=float, required=True)
    args = parser.parse_args()
    began = time.monotonic()
    encoder = load_encoder(args.encoder)
    graph, original = encoder.graph_at(args.g55)
    triples = list(encoder.itertools.combinations(range(42), 3))
    result = {
        "experiment": "Exoo g55.42: delete three labelled vertices, freeze 39-core, insert four unrestricted vertices",
        "fixture_sha256": hashlib.sha256(open(args.g55, "rb").read()).hexdigest(),
        "encoder_sha256": hashlib.sha256(open(args.encoder, "rb").read()).hexdigest(),
        "solver": "PySAT Glucose4", "solver_version": encoder.pysat.__version__,
        "python": sys.version, "platform": platform.platform(),
        "scope": "lexicographic unordered triples after start; all 162 edges involving four new vertices free",
        "total_triples": len(triples), "start": args.start, "per_core_seconds": args.per_core,
        "cross_check_3core_4new": encoder.exhaustive_control(), "unsat": [], "timed_out": [], "sat": [],
        "decisions": 0, "resume_index": args.start, "elapsed_seconds": 0,
        "checkpointing": "atomic os.replace after each completed tuple",
    }
    deleted = (39, 40, 41)
    ids = [vertex for vertex in range(42) if vertex not in deleted]
    clauses, desc = encoder.encode([[graph[i][j] for j in ids] for i in ids], 3)
    planted = [graph[deleted[q]][ids[o]] if kind == "core" else graph[deleted[q]][deleted[o]] for kind, q, o in desc]
    rebuilt = encoder.render(ids, graph, desc, planted)
    result["planted_39_to_42"] = {"clause_count": len(clauses), "satisfies_cnf": encoder.accepts(clauses, planted), "scanner_k5_free": encoder.no_k5(rebuilt), "matches_exoo": rebuilt == original}
    assert all(result["planted_39_to_42"].values())
    deadline = began + args.seconds
    for index in range(args.start, len(triples)):
        if time.monotonic() >= deadline:
            break
        deleted = triples[index]
        ids = [vertex for vertex in range(42) if vertex not in deleted]
        clauses, desc = encoder.encode([[graph[i][j] for j in ids] for i in ids], 4)
        bits, decisions, timed_out = encoder.solve(clauses, min(args.per_core, deadline - time.monotonic()))
        result["decisions"] += decisions
        result["resume_index"] = index + 1
        record = [index, list(deleted), len(clauses), decisions]
        if timed_out:
            result["timed_out"].append(record)
        elif bits is None:
            result["unsat"].append(record)
        else:
            rows = encoder.render(ids, graph, desc, bits)
            assert encoder.no_k5(rows)
            result["sat"].append(record + [rows])
        result["elapsed_seconds"] = time.monotonic() - began
        result["counts"] = {key: len(result[key]) for key in ("unsat", "timed_out", "sat")}
        write_atomic(args.out, result)
        if result["sat"]:
            break
    result["elapsed_seconds"] = time.monotonic() - began
    result["counts"] = {key: len(result[key]) for key in ("unsat", "timed_out", "sat")}
    write_atomic(args.out, result)
    print(json.dumps({key: result[key] for key in ("counts", "resume_index", "elapsed_seconds", "decisions")}, sort_keys=True))


if __name__ == "__main__":
    main()
