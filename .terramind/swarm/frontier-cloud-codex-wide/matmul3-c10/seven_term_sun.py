#!/usr/bin/env python3
"""Exact checkpointed seven-term screen on the public Sun rank-23 scheme.

The input is a Frontier-format witness derived from Sun's public 56-addition
certificate. A neighbour is made by the
integer shared-factor identity X⊗Y⊗Z + U⊗V⊗Z =
(X+U)⊗Y⊗Z + U⊗(V-Y)⊗Z (and cyclic variants).  This leaves the full tensor
unchanged but alters the selected supports. For every selected support we
look for a constructive reduction: factor one of its three flattenings over Q
and require every resulting complementary 9-vector to be a decomposable
3-by-3 matrix.  Such a factorization is an explicit replacement by fewer
rank-one terms, not merely a rank lower bound.

The caller chooses one support size. This c6 run uses seven only, so it never
repeats the earlier three- through six-term scans and checkpoints after each
complete neighbour.
"""
from __future__ import annotations

import argparse, hashlib, itertools, json, math, os, time
from fractions import Fraction
from pathlib import Path


def write_json_atomic(path, value):
    """Durably replace a JSON progress artifact without a torn checkpoint."""
    target = Path(path)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, target)


def sparse_program(base, fresh, outputs):
    vectors = [tuple(1 if i == j else 0 for i in range(base)) for j in range(base)]
    def expand(form):
        return tuple(sum(item["value"] * vectors[item["index"]][q] for item in form) for q in range(base))
    for form in fresh:
        vectors.append(expand(form))
    return [expand(form) for form in outputs]


def decode(path):
    data = json.loads(Path(path).read_text())
    assert len(data["terms"]) == 23
    return [tuple(tuple(Fraction(x) for row in term[key] for x in row)
                  for key in ("a", "b", "c")) for term in data["terms"]]


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
    ap.add_argument("--support-size", type=int, required=True,
                    help="single support size to enumerate")
    ap.add_argument("--control-output", help="write the planted exact-control result")
    ap.add_argument("--checkpoint", help="write a durable support-level checkpoint")
    ap.add_argument("--start-neighbour", type=int, default=0,
                    help="first fixed neighbour to visit (zero based)")
    ap.add_argument("--start-support-index", type=int, default=0,
                    help="zero-based lexicographic support index within start neighbour")
    ap.add_argument("--checkpoint-every", type=int, default=1000,
                    help="write a checkpoint after this many tested supports")
    ap.add_argument("--stop-after", type=int,
                    help="test at most this many supports; used for interruption controls")
    ap.add_argument("--max-seconds", type=float,
                    help="gracefully stop after this measured wall-clock budget")
    ap.add_argument("--trace", help="write one deterministic JSON line per tested support")
    args = ap.parse_args()
    source = Path(args.source)
    started = time.time()
    seed = decode(source)
    if not 1 <= args.support_size <= len(seed):
        raise SystemExit("support size must be between 1 and the seed length")
    if args.baseline:
        def matrix(v): return [list(v[3 * row:3 * row + 3]) for row in range(3)]
        write_json_atomic(args.baseline, {"terms": [
            {"a": matrix(a), "b": matrix(b), "c": matrix(c)} for a, b, c in seed
        ]})
    ns, legal_pairs = neighbours(seed)
    # A planted exact control: support-size identical rank-one summands collapse to
    # one. It exercises the corrected 9-by-9 complementary flattening and
    # integer factor recovery used by the actual screen.
    e0 = (1,) + (0,) * 8
    control = [(e0, e0, e0)] * args.support_size
    control_found = flatten_factorization(control, 0)
    if control_found is None or control_found["new_terms"] != 1:
        raise AssertionError("planted control was not reduced exactly")
    if args.control_output:
        write_json_atomic(args.control_output, {
            "support_size": args.support_size, "mode": 0, "old_terms": args.support_size,
            "new_terms": control_found["new_terms"],
            "replacement_terms": len(control_found["replacement"]),
            "status": "passed"
        })
    report = {"source": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "started_unix": started, "support_sizes": [args.support_size],
              "excluded_support_sizes": [3, 4, 5, 6] if args.support_size == 7 else [],
              "planted_control": {"old_terms": args.support_size, "new_terms": 1, "status": "passed"},
              "legal_shared_factor_pairs": legal_pairs, "neighbours": []}
    if not 0 <= args.start_neighbour < len(ns):
        raise SystemExit("start-neighbour is outside the seven fixed neighbours")
    all_supports = list(itertools.combinations(range(23), args.support_size))
    if not 0 <= args.start_support_index < len(all_supports):
        raise SystemExit("start-support-index is outside the support range")
    report["cursor_start"] = {"neighbour": args.start_neighbour,
                              "support_index": args.start_support_index,
                              "support": list(all_supports[args.start_support_index])}
    report["neighbours"] = []
    candidate = None
    tested_total = 0
    next_cursor = None
    trace = Path(args.trace).open("w") if args.trace else None
    for index in range(args.start_neighbour, len(ns)):
        move, terms = ns[index]
        assert tensor(terms) == tensor(seed), ("rewrite changed tensor", move)
        tested = constructive = low_flattening = 0
        min_flat = args.support_size
        examples = []
        support_start = args.start_support_index if index == args.start_neighbour else 0
        for support_index in range(support_start, len(all_supports)):
            support = all_supports[support_index]
            selected = [terms[i] for i in support]
            tested += 1
            tested_total += 1
            ranks = [rank([t[mode] for t in selected])[0] for mode in range(3)]
            min_flat = min(min_flat, max(ranks))
            if max(ranks) >= args.support_size:
                if trace:
                    trace.write(json.dumps({"neighbour": index, "support_index": support_index,
                                            "support": support, "max_factor_rank": max(ranks),
                                            "low_flattening": False, "constructive": False},
                                           sort_keys=True) + "\n")
                next_index = support_index + 1
                next_cursor = ({"complete": False, "next_neighbour": index + 1,
                                "next_support_index": 0,
                                "next_support": list(all_supports[0]) if index + 1 < len(ns) else None}
                               if next_index == len(all_supports) else
                               {"complete": False, "next_neighbour": index,
                                "next_support_index": next_index,
                                "next_support": list(all_supports[next_index])})
                partial = {"index": index, "move": move, "tested": tested,
                           "low_flattening": low_flattening, "constructive_reductions": constructive,
                           "minimum_max_factor_rank": min_flat, "examples": examples,
                           "complete": next_index == len(all_supports)}
                limit_reached = ((args.stop_after is not None and tested_total >= args.stop_after) or
                                 (args.max_seconds is not None and time.time() - started >= args.max_seconds))
                if args.checkpoint and (tested_total % args.checkpoint_every == 0 or limit_reached):
                    checkpoint = dict(report)
                    checkpoint["neighbours"] = report["neighbours"] + [partial]
                    checkpoint["tested_total"] = tested_total
                    checkpoint["elapsed_seconds"] = time.time() - started
                    checkpoint["resume_cursor"] = next_cursor
                    write_json_atomic(args.checkpoint, checkpoint)
                if limit_reached:
                    report["neighbours"].append(partial)
                    report["tested_total"] = tested_total
                    report["elapsed_seconds"] = time.time() - started
                    report["candidate"] = None if candidate is None else {k: v for k, v in candidate.items() if k != "terms"}
                    report["resume_cursor"] = next_cursor
                    write_json_atomic(args.output, report)
                    if trace: trace.close()
                    print(json.dumps(report, sort_keys=True))
                    return
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
            if trace:
                trace.write(json.dumps({"neighbour": index, "support_index": support_index,
                                        "support": support, "max_factor_rank": max(ranks),
                                        "low_flattening": max(ranks) < args.support_size,
                                        "constructive": bool(found) if max(ranks) < args.support_size else False},
                                       sort_keys=True) + "\n")
            next_index = support_index + 1
            if next_index == len(all_supports):
                next_cursor = {"complete": False, "next_neighbour": index + 1,
                               "next_support_index": 0,
                               "next_support": list(all_supports[0]) if index + 1 < len(ns) else None}
            else:
                next_cursor = {"complete": False, "next_neighbour": index,
                               "next_support_index": next_index,
                               "next_support": list(all_supports[next_index])}
            partial = {"index": index, "move": move, "tested": tested,
                       "low_flattening": low_flattening, "constructive_reductions": constructive,
                       "minimum_max_factor_rank": min_flat, "examples": examples,
                       "complete": next_index == len(all_supports)}
            limit_reached = ((args.stop_after is not None and tested_total >= args.stop_after) or
                             (args.max_seconds is not None and time.time() - started >= args.max_seconds))
            if args.checkpoint and (tested_total % args.checkpoint_every == 0 or limit_reached):
                checkpoint = dict(report)
                checkpoint["neighbours"] = report["neighbours"] + [partial]
                checkpoint["tested_total"] = tested_total
                checkpoint["elapsed_seconds"] = time.time() - started
                checkpoint["resume_cursor"] = next_cursor
                write_json_atomic(args.checkpoint, checkpoint)
            if limit_reached:
                report["neighbours"].append(partial)
                report["tested_total"] = tested_total
                report["elapsed_seconds"] = time.time() - started
                report["candidate"] = None if candidate is None else {k: v for k, v in candidate.items() if k != "terms"}
                report["resume_cursor"] = next_cursor
                write_json_atomic(args.output, report)
                if trace: trace.close()
                print(json.dumps(report, sort_keys=True))
                return
        report["neighbours"].append({"index": index, "move": move, "tested": tested,
                                     "low_flattening": low_flattening, "constructive_reductions": constructive,
                                     "minimum_max_factor_rank": min_flat, "examples": examples})
        if args.checkpoint:
            checkpoint = dict(report)
            checkpoint["tested_total"] = tested_total
            checkpoint["elapsed_seconds"] = time.time() - started
            checkpoint["resume_cursor"] = next_cursor
            write_json_atomic(args.checkpoint, checkpoint)
    report["elapsed_seconds"] = time.time() - started
    report["candidate"] = None if candidate is None else {k: v for k, v in candidate.items() if k != "terms"}
    report["resume_cursor"] = {"complete": True, "next_neighbour": None, "next_support": None}
    write_json_atomic(args.output, report)
    if trace: trace.close()
    if args.candidate and candidate:
        def matrix(v): return [list(v[3 * row:3 * row + 3]) for row in range(3)]
        write_json_atomic(args.candidate, {"terms": [
            {"a": matrix(a), "b": matrix(b), "c": matrix(c)} for a, b, c in candidate["terms"]
        ]})
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__": main()
