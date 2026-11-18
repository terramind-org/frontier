#!/usr/bin/env python3
"""Checkpointed exact-Q recovery on retained Perminov low-rank trace rows.

This consumes existing JSONL traces only; it never enumerates subsets.  The
order is a deterministic, stratified round-robin of the stored low-flattening
rows for each recorded rewrite.  A checkpoint is atomically replaced after
every processed row so a later run can resume without retesting it.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import tempfile
import time
from fractions import Fraction
from pathlib import Path


def atomic(path, value):
    path = Path(path)
    # A unique temp name prevents two unrelated atomic writes from sharing a
    # ``.tmp`` file.  The stream lock below prevents two writers for one
    # logical records/cursor pair altogether.
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    with os.fdopen(fd, "w") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    Path(temporary).replace(path)


def acquire_stream_lock(records):
    """Take the non-blocking, OS-held lock for one logical result stream."""
    lock_path = Path(str(records) + ".lock")
    handle = lock_path.open("a+")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise RuntimeError(f"writer already owns stream lock: {lock_path}")
    return handle


def load(path):
    spec = importlib.util.spec_from_file_location("perminov_screen", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def qtext(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def q_rank_one(prior, vector):
    if not prior.rank_one_matrix(vector):
        return None
    matrix = [Fraction(x) for x in vector]
    column = next((j for j in range(9) if any(matrix[9 * i + j] for i in range(9))), None)
    if column is None:
        return None
    left = tuple(matrix[9 * i + column] for i in range(9))
    pivot = next(i for i, x in enumerate(left) if x)
    right = tuple(matrix[9 * pivot + j] / left[pivot] for j in range(9))
    assert tuple(left[i] * right[j] for i in range(9) for j in range(9)) == tuple(matrix)
    return left, right


def rational_factorization(prior, terms, mode):
    factors = [[t[mode] for t in terms], [t[(mode + 1) % 3] for t in terms],
               [t[(mode + 2) % 3] for t in terms]]
    rank, _, _ = prior.rank(factors[0])
    if rank >= len(terms):
        return None
    _, columns, _ = prior.rank(list(zip(*factors[0])))
    basis = [factors[0][i] for i in columns]
    transpose = [list(map(Fraction, row)) for row in zip(*basis)]
    complements = [[Fraction(0) for _ in range(81)] for _ in basis]
    for term_index, factor in enumerate(factors[0]):
        equations = [row + [Fraction(factor[i])] for i, row in enumerate(transpose)]
        pivot_row = 0
        for column in range(len(basis)):
            pivot = next(i for i in range(pivot_row, len(equations)) if equations[i][column])
            equations[pivot_row], equations[pivot] = equations[pivot], equations[pivot_row]
            scale = equations[pivot_row][column]
            equations[pivot_row] = [x / scale for x in equations[pivot_row]]
            for i in range(len(equations)):
                if i != pivot_row and equations[i][column]:
                    scale = equations[i][column]
                    equations[i] = [x - scale * y for x, y in zip(equations[i], equations[pivot_row])]
            pivot_row += 1
        weights = [equations[i][-1] for i in range(len(basis))]
        pair = prior.outer(factors[1][term_index], factors[2][term_index])
        for i, weight in enumerate(weights):
            complements[i] = [x + weight * y for x, y in zip(complements[i], pair)]
    parts = [q_rank_one(prior, vector) for vector in complements]
    if not all(parts):
        return None
    replacement = [(basis[i], parts[i][0], parts[i][1]) for i in range(rank)]
    assert prior.tensor(terms) == prior.tensor(replacement)
    return {"mode": mode, "old_terms": len(terms), "new_terms": rank,
            "replacement": replacement,
            "nonintegral_complement": any(x.denominator != 1 for part in parts for vector in part for x in vector)}


def control(prior):
    zero = (Fraction(0),) * 9
    e0 = (Fraction(1),) + zero[1:]
    e1 = (Fraction(0), Fraction(1)) + zero[2:]
    terms = [(tuple(4 * x for x in e0), e0, e0), (tuple(2 * x for x in e0), e0, e1),
             (tuple(2 * x for x in e0), e1, e0), (e0, e1, e1)]
    assert prior.flatten_factorization(terms, 0) is None
    found = rational_factorization(prior, terms, 0)
    assert found and found["new_terms"] == 1 and found["nonintegral_complement"]
    return {"old_integral_result": None, "new_rational_terms": 1, "identity_verified": True,
            "identity": "4e0⊗e0⊗e0 + 2e0⊗e0⊗e1 + 2e0⊗e1⊗e0 + e0⊗e1⊗e1 = 4e0⊗(e0+e1/2)⊗(e0+e1/2)"}


def ordered_rows(paths):
    buckets, hashes = {}, {}
    for path in paths:
        hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        for line in path.read_text().splitlines():
            row = json.loads(line)
            if row["low_flattening"]:
                key = f"perminov-q-c15-v1:{row['neighbour']}:{row['support_index']}"
                buckets.setdefault(row["neighbour"], []).append((hashlib.sha256(key.encode()).hexdigest(), row))
    for rows in buckets.values():
        rows.sort()
    # Rewrites 1--6 are the recorded strata; each round takes one next row.
    order, round_index = [], 0
    keys = sorted(buckets)
    while True:
        added = False
        for key in keys:
            if round_index < len(buckets[key]):
                order.append(buckets[key][round_index][1])
                added = True
        if not added:
            return order, hashes, {str(k): len(v) for k, v in buckets.items()}
        round_index += 1


def cursor_control(checkpoint, output):
    """Exercise checkpoint semantics without reading or evaluating trace rows."""
    rows = [{"order_index": i, "token": f"synthetic-{i}"} for i in range(12)]

    def run(start, stop, destination):
        seen = []
        for index in range(start, stop):
            seen.append(rows[index])
            atomic(destination, {"completed": seen, "cursor": {"next_order_index": index + 1,
                   "next": None if index + 1 == len(rows) else rows[index + 1]}})
        return seen

    uninterrupted = run(0, len(rows), checkpoint.with_name("cursor-control-uninterrupted.json"))
    first = run(0, 5, checkpoint.with_name("cursor-control-interrupted.json"))
    interrupted_checkpoint = json.loads(checkpoint.with_name("cursor-control-interrupted.json").read_text())
    assert interrupted_checkpoint["cursor"]["next_order_index"] == 5
    assert interrupted_checkpoint["cursor"]["next"] == rows[5]
    second = run(5, len(rows), checkpoint.with_name("cursor-control-resumed.json"))
    assert uninterrupted == first + second
    report = {"synthetic_rows": len(rows), "interrupted_after": 5,
              "interrupted_first_unvisited": rows[5], "uninterrupted_complete": True,
              "resumed_complete": True, "sequence_identical": True}
    atomic(output, report)
    print(json.dumps(report, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--trace", type=Path, action="append", required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-tests", type=int, default=1536)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--records", type=Path)
    parser.add_argument("--expected-start")
    parser.add_argument("--cursor-control", action="store_true")
    args = parser.parse_args()
    if args.cursor_control:
        cursor_control(args.checkpoint, args.output)
        return
    started = time.time()
    prior = load(args.prior)
    seed = prior.decode(args.source)
    neighbours, legal_pairs = prior.neighbours(seed)
    rows, trace_hashes, available = ordered_rows(args.trace)
    if args.expected_start:
        expected = json.loads(args.expected_start)
        actual = rows[args.start_index]
        assert {key: actual[key] for key in ("neighbour", "support_index", "support")} == expected
    # A record is durable before its cursor.  On restart, reconcile the
    # append-only JSONL against the deterministic order and advance from the
    # first absent row; never trust a cursor by itself and never retest a row.
    assert args.records is not None
    # Hold one OS lock from before reading/reconciling the durable stream until
    # after every append/fsync and cursor replacement.  A concurrent start
    # fails before it can append even one production record.
    stream_lock = acquire_stream_lock(args.records)
    recovered = []
    if args.records.exists():
        for line in args.records.read_text().splitlines():
            item = json.loads(line)
            expected_index = args.start_index + len(recovered)
            if item["order_index"] != expected_index:
                raise ValueError("durable records are not a contiguous unique "
                                 f"sequence: expected order {expected_index}, "
                                 f"found {item['order_index']}")
            expected_row = rows[expected_index]
            assert {key: item[key] for key in ("neighbour", "support_index", "support")} == {
                key: expected_row[key] for key in ("neighbour", "support_index", "support")}
            recovered.append(item)
    effective_start = args.start_index + len(recovered)
    end = min(effective_start + args.max_tests, len(rows))
    tested_count, per_rewrite = len(recovered), {}
    old_true_count = new_true_count = 0
    last = None
    candidate = None
    for item in recovered:
        per_rewrite[str(item["neighbour"])] = per_rewrite.get(str(item["neighbour"]), 0) + 1
        old_true_count += int(any(item["old_integral_modes"]))
        new_true_count += int(any(item["new_rational_modes"]))
        last = item
    records = args.records.open("a")
    for index in range(effective_start, end):
        row = rows[index]
        _, terms = neighbours[row["neighbour"]]
        chosen = [terms[i] for i in row["support"]]
        old = [prior.flatten_factorization(chosen, mode) is not None for mode in range(3)]
        new = [rational_factorization(prior, chosen, mode) for mode in range(3)]
        found = next((item for item in new if item), None)
        tested = {"order_index": index, "neighbour": row["neighbour"], "support_index": row["support_index"],
                       "support": list(row["support"]), "old_integral_modes": old,
                       "new_rational_modes": [item is not None for item in new],
                       "new_terms": None if found is None else found["new_terms"]}
        records.write(json.dumps(tested, sort_keys=True) + "\n")
        records.flush()
        os.fsync(records.fileno())
        tested_count += 1
        per_rewrite[str(row["neighbour"])] = per_rewrite.get(str(row["neighbour"]), 0) + 1
        old_true_count += int(any(old))
        new_true_count += int(any(tested["new_rational_modes"]))
        last = tested
        if found and found["new_terms"] <= 6 and candidate is None:
            replacement = []
            for first, second, third in found["replacement"]:
                triplet = [None, None, None]
                mode = found["mode"]
                triplet[mode], triplet[(mode + 1) % 3], triplet[(mode + 2) % 3] = first, second, third
                replacement.append(tuple(triplet))
            candidate = {"neighbour": row["neighbour"], "support": list(row["support"]), "mode": mode,
                         "new_terms": found["new_terms"], "terms": [term for i, term in enumerate(terms) if i not in row["support"]] + replacement}
        next_index = index + 1
        report = {"method": "exact rational complementary-flattening recovery", "old_criterion": "requires integer complementary 9-vectors before rank-one recovery",
                  "sample_rule": "Sort each recorded rewrite by SHA-256(perminov-q-c15-v1:neighbour:support_index), then take rows round-robin across rewrites 1--6.",
                  "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(), "prior_sha256": hashlib.sha256(args.prior.read_bytes()).hexdigest(),
                  "trace_sha256": trace_hashes, "available_low_flattening": available, "legal_shared_factor_pairs": legal_pairs,
                  "synthetic_positive_control": control(prior), "start_order_index": args.start_index,
                  "recovered_record_count": len(recovered), "effective_start_order_index": effective_start,
                  "processed_count": tested_count, "processed_per_rewrite": per_rewrite, "last_processed": last,
                  "records": str(args.records), "old_true_count": old_true_count, "new_true_count": new_true_count,
                  "candidate": None if candidate is None else {k: v for k, v in candidate.items() if k != "terms"},
                  "elapsed_seconds": time.time() - started,
                  "cursor": {"complete": next_index == len(rows), "next_order_index": None if next_index == len(rows) else next_index,
                             "next": None if next_index == len(rows) else {"neighbour": rows[next_index]["neighbour"], "support_index": rows[next_index]["support_index"], "support": list(rows[next_index]["support"])}}}
        atomic(args.checkpoint, report)
    records.close()
    atomic(args.output, report)
    if candidate:
        def matrix(vector): return [[qtext(x) for x in vector[3 * i:3 * i + 3]] for i in range(3)]
        atomic(args.output.with_name("rational-candidate-witness.json"), {"terms": [{"a": matrix(a), "b": matrix(b), "c": matrix(c)} for a, b, c in candidate["terms"]]})
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
