#!/usr/bin/env python3
"""Re-run one previously timed-out labelled triple without advancing a sweep."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import time


def load_encoder(path):
    spec = importlib.util.spec_from_file_location("ramsey_encoder", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("encoder")
    parser.add_argument("g55")
    parser.add_argument("--index", type=int, required=True)
    parser.add_argument("--per-core", type=float, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    began = time.monotonic()
    encoder = load_encoder(args.encoder)
    graph, original = encoder.graph_at(args.g55)
    triples = list(encoder.itertools.combinations(range(42), 3))
    deleted = triples[args.index]
    ids = [v for v in range(42) if v not in deleted]
    clauses, desc = encoder.encode([[graph[i][j] for j in ids] for i in ids], 4)
    bits, decisions, timed_out = encoder.solve(clauses, args.per_core)
    result = {
        "case": {"index": args.index, "triple": list(deleted), "clauses": len(clauses)},
        "encoder_sha256": hashlib.sha256(open(args.encoder, "rb").read()).hexdigest(),
        "fixture_sha256": hashlib.sha256(open(args.g55, "rb").read()).hexdigest(),
        "per_core_seconds": args.per_core,
        "python": sys.version,
        "platform": platform.platform(),
        "solver": "PySAT Glucose4",
        "solver_version": encoder.pysat.__version__,
        "decisions": decisions,
        "elapsed_seconds": time.monotonic() - began,
        "outcome": "timeout" if timed_out else "unsat" if bits is None else "sat",
    }
    if bits is not None:
        rows = encoder.render(ids, graph, desc, bits)
        assert encoder.no_k5(rows)
        result["rows"] = rows
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({key: result[key] for key in ("case", "outcome", "decisions", "elapsed_seconds")}, sort_keys=True))


if __name__ == "__main__":
    main()
