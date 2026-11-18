#!/usr/bin/env python3
"""Residual 3-edge-matching recolour + one-vertex-insertion search.

PR 60 exhausted old-flip edge sets with a vertex cover of size at most two.
For three flips the remaining sets are exactly three-edge matchings.  For
each matching this program uses a sound certificate filter: a monochromatic
K5 produced by flipping one isolated edge must be disrupted by another
flipped edge lying in that same five-set.  Every survivor is directly checked
for both colours before its exact 43rd-vertex K4 SAT instance is solved.
"""
from __future__ import annotations

import argparse, hashlib, itertools, json, math, time


def read_graph(path):
    rows = [x.strip() for x in open(path, encoding="ascii") if x.strip()]
    assert len(rows) == 42 and all(len(x) == 42 and set(x) <= {"0", "1"} for x in rows)
    a = [[int(x) for x in row] for row in rows]
    assert all(a[i][i] == 0 and a[i][j] == a[j][i] for i in range(42) for j in range(42))
    return a, rows


def make_data(a):
    n = len(a)
    edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    ix = {e: k for k, e in enumerate(edges)}
    bits = sum(a[i][j] << ix[i, j] for i, j in edges)
    k4 = []
    k5 = []
    for vs in itertools.combinations(range(n), 4):
        es = tuple(ix[e] for e in itertools.combinations(vs, 2))
        k4.append((vs, es))
    for vs in itertools.combinations(range(n), 5):
        mask = 0
        for e in itertools.combinations(vs, 2): mask |= 1 << ix[e]
        k5.append((vs, mask))
    return edges, ix, bits, k4, k5


def first_mono(bits, k5):
    for vs, mask in k5:
        c = (bits & mask).bit_count()
        if c == 0 or c == 10: return vs, mask
    return None


def isolated_flip_certificates(bits, k5, m):
    """All K5 certificates for each edge whose isolated flip creates one.

    A flip can create a monochromatic K5 only from a five-set with exactly
    one edge of one colour (or, symmetrically, exactly nine).  Enumerating
    five-sets once is far cheaper than rescanning them for all 861 edges.
    """
    cert = [[] for _ in range(m)]
    for _, mask in k5:
        ones = (bits & mask).bit_count()
        if ones == 1:
            edge = (bits & mask).bit_length() - 1
        elif ones == 9:
            edge = (mask & ~bits).bit_length() - 1
        else:
            continue
        cert[edge].append(mask)
    return cert


def three_flip_clauses(bits, k5, m):
    """Exact residual K5 clauses after the one-minority certificate filter."""
    cert = [[] for _ in range(m)]
    pairs = {}
    triples = set()
    for _, mask in k5:
        minority = bits & mask
        if minority.bit_count() > 5: minority = mask ^ minority
        q = minority.bit_count()
        es = []
        x = minority
        while x:
            low = x & -x; es.append(low.bit_length() - 1); x ^= low
        if q == 1:
            cert[es[0]].append(mask)
        elif q == 2:
            pairs.setdefault(tuple(es), []).append(mask)
        elif q == 3:
            triples.add(tuple(es))
    return cert, pairs, triples


def extension(bits, k4, n):
    """Unit-propagating DPLL for forbidden all-equal K4 incidences."""
    clauses = []
    for vs, es in k4:
        c = sum((bits >> e) & 1 for e in es)
        if c == 0 or c == 6: clauses.append((vs, 1 if c == 6 else 0))
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
                    v = unknown[0]; need = 1 - forbidden
                    if assign[v] >= 0 and assign[v] != need: return None
                    if assign[v] < 0: assign[v] = need; changed = True
        v = next((v for v in order if assign[v] < 0), None)
        if v is None: return assign
        for value in (0, 1):
            got = rec(assign[:v] + [value] + assign[v + 1:])
            if got is not None: return got
        return None
    answer = rec([-1] * n)
    return answer, nodes, len(clauses)


def pairings(six):
    """All 15 perfect matchings of six labelled vertices."""
    a = six[0]
    for q in range(1, 6):
        b = six[q]
        rest = six[1:q] + six[q + 1:]
        c = rest[0]
        for r in range(1, 4):
            d = rest[r]
            last = rest[1:r] + rest[r + 1:]
            yield ((a, b), (c, d), (last[0], last[1]))


def run_small_filter_control():
    """Exhaustively show the certificate filter never rejects a valid triple."""
    # Seek a deterministic K5-free 8-vertex fixture with non-vacuous rejects.
    # Each accepted fixture has all 420 matching triples checked directly.
    for seed in range(1, 10000):
        state = seed
        a = [[0] * 8 for _ in range(8)]
        for i in range(8):
            for j in range(i + 1, 8):
                state = (1103515245 * state + 12345) & 0x7fffffff
                a[i][j] = a[j][i] = (state >> 12) & 1
        edges, ix, bits, _, k5 = make_data(a)
        if first_mono(bits, k5) is not None: continue
        cert = isolated_flip_certificates(bits, k5, len(edges))
        checked = rejected = 0
        for six in itertools.combinations(range(8), 6):
            for ps in pairings(six):
                fs = [ix[tuple(sorted(x))] for x in ps]
                fmask = sum(1 << x for x in fs)
                reject = any(any(not (mask & (fmask ^ (1 << e))) for mask in cert[e]) for e in fs)
                direct_bad = first_mono(bits ^ fmask, k5) is not None
                assert not (reject and not direct_bad)
                checked += 1; rejected += int(reject)
        if rejected:
            return {"fixture_n": 8, "seed": seed, "matching_triples": checked,
                    "filter_rejected": rejected, "false_rejections": 0}
    raise AssertionError("no non-vacuous small fixture found")


def planted_control(a):
    """Recover vertex 41 from its 41-vertex induced subgraph."""
    core = [row[:41] for row in a[:41]]
    edges, _, bits, k4, k5 = make_data(core)
    sol, nodes, clauses = extension(bits, k4, 41)
    return {"sat": sol is not None, "matches_exoo": sol == [a[i][41] for i in range(41)],
            "nodes": nodes, "clauses": clauses, "core_k5_free": first_mono(bits, k5) is None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("g55")
    ap.add_argument("--seconds", type=float, default=1800)
    ap.add_argument("--skip-controls", action="store_true", help="for resumable timed slices")
    ap.add_argument("--start", type=int, default=0, help="global matching cursor")
    ap.add_argument("--count", type=int, default=None, help="maximum matchings in this slice")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    start = time.monotonic()
    a, rows = read_graph(args.g55)
    edges, ix, bits, k4, k5 = make_data(a)
    assert first_mono(bits, k5) is None
    result = {"sha256": hashlib.sha256(open(args.g55, "rb").read()).hexdigest(),
              "edge_count": len(edges), "scope": "all 3-edge matchings of labelled K42",
              "total": 15 * math.comb(42, 6), "start": args.start}
    if not args.skip_controls:
        result["small_filter_control"] = run_small_filter_control()
        result["planted_41_to_42"] = planted_control(a)
        base, base_nodes, base_clauses = extension(bits, k4, 42)
        result["fixed_42_extension"] = {"sat": base is not None, "nodes": base_nodes, "clauses": base_clauses}
    cert, pair_clauses, triple_clauses = three_flip_clauses(bits, k5, len(edges))
    stats = {"enumerated": 0, "certificate_rejected": 0, "direct_rejected": 0,
             "extension_unsat": 0, "extension_sat": 0, "dpll_nodes": 0,
             "pair_clause_rejected": 0, "triple_clause_rejected": 0,
             "timed_out": 0, "resume_six_cursor": None}
    done = False
    global_cursor = 0
    search_started = None
    for six_index, six in enumerate(itertools.combinations(range(42), 6)):
        for ps in pairings(six):
            if global_cursor < args.start:
                global_cursor += 1; continue
            if search_started is None: search_started = time.monotonic()
            if args.count is not None and stats["enumerated"] >= args.count:
                stats["timed_out"] = result["total"] - global_cursor
                stats["resume_six_cursor"] = {"combination_index": six_index, "six_vertices": six}
                done = True; break
            if time.monotonic() - search_started >= args.seconds:
                stats["timed_out"] = result["total"] - global_cursor
                stats["resume_six_cursor"] = {"combination_index": six_index, "six_vertices": six}
                done = True; break
            fs = [ix[tuple(sorted(x))] for x in ps]
            fmask = (1 << fs[0]) | (1 << fs[1]) | (1 << fs[2])
            stats["enumerated"] += 1
            global_cursor += 1
            if any(any(not (mask & (fmask ^ (1 << e))) for mask in cert[e]) for e in fs):
                stats["certificate_rejected"] += 1; continue
            bad_pair = False
            for e, f in itertools.combinations(sorted(fs), 2):
                # The third flip must be outside the five-set for a 2-minority
                # K5 to become monochromatic.
                third = next(x for x in fs if x != e and x != f)
                if any(not (mask & (1 << third)) for mask in pair_clauses.get((e, f), ())):
                    bad_pair = True; break
            if bad_pair:
                stats["pair_clause_rejected"] += 1; continue
            if tuple(sorted(fs)) in triple_clauses:
                stats["triple_clause_rejected"] += 1; continue
            changed = bits ^ fmask
            # The certificate only prunes; this direct two-colour K5 scan is authoritative.
            if first_mono(changed, k5) is not None:
                stats["direct_rejected"] += 1; continue
            sol, nodes, clauses = extension(changed, k4, 42)
            stats["dpll_nodes"] += nodes
            if sol is None:
                stats["extension_unsat"] += 1
            else:
                stats["extension_sat"] += 1
                result["candidate"] = {"flips": [edges[e] for e in fs], "extension": sol}
                done = True; break
        if done: break
    result["search"] = stats
    result["next_cursor"] = args.start + stats["enumerated"]
    result["elapsed_seconds"] = time.monotonic() - start
    with open(args.out, "w", encoding="utf8") as f: json.dump(result, f, indent=2, sort_keys=True); f.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__": main()
