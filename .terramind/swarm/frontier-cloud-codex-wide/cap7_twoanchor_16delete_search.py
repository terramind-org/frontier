#!/usr/bin/env python3
"""Exact 16-deletion exchanges for the 120 CF-236 two-anchor pairs.

The domain is the lexicographic pairs of the 24 ten-blocker outside points
whose union of blocker matchings has exact minimum cover 16.  Every minimum
cover is generated once (after canonical de-duplication).  A candidate point
is first tested against the retained cap and both forced anchors; only cases
with at least 15 further candidates invoke the exact three-uniform extension
search.  The latter checks collinear triples, rather than incorrectly turning
every pair whose third point is merely *available* into a conflict.
"""
import argparse, hashlib, itertools, json, platform, sys, time
from pathlib import Path

from cap7_hittingset_search import N, blockers, cap236, dec, third, valid


def min_cover_degree_two(edges, forced):
    """König's value for a union of two matchings after forced deletions."""
    adj = {}
    for x, y in edges:
        if x in forced or y in forced:
            continue
        adj.setdefault(x, set()).add(y)
        adj.setdefault(y, set()).add(x)
    seen, value = set(), len(forced)
    for root in sorted(adj):
        if root in seen:
            continue
        stack, vertices = [root], 0
        seen.add(root)
        while stack:
            x = stack.pop(); vertices += 1
            for y in adj[x]:
                if y not in seen:
                    seen.add(y); stack.append(y)
        value += vertices // 2
    return value


def exact_covers(edges, forced, target):
    """All target-size covers, in deterministic order, with duplicate paths removed."""
    seen = set()
    def rec(chosen):
        if len(chosen) > target:
            return
        edge = next((e for e in edges if e[0] not in chosen and e[1] not in chosen), None)
        if edge is None:
            if len(chosen) == target:
                seen.add(frozenset(chosen))
            return
        x, y = edge
        rec(chosen | {x})
        rec(chosen | {y})
    rec(frozenset(forced))
    return tuple(sorted(seen, key=lambda c: tuple(sorted(c))))


def additional_candidates(base, outside, anchors, deleted, all_blockers):
    retained = set(base) - set(deleted)
    out = []
    for q in outside:
        if q in anchors:
            continue
        if any(not ({x, y} & deleted) for x, y in all_blockers[q]):
            continue
        if any(third(q, a) in retained for a in anchors):
            continue
        out.append(q)
    return tuple(out), retained


def exact_extension(candidates, fixed, need, node_limit):
    """Find ``need`` additions with no line wholly in fixed plus additions."""
    nodes, cutoff, found = 0, False, None
    fixed = frozenset(fixed)
    def allowed(q, chosen):
        occupied = fixed | frozenset(chosen)
        return all(third(q, r) not in occupied for r in occupied)
    def rec(start, chosen):
        nonlocal nodes, cutoff, found
        if found is not None or cutoff:
            return
        nodes += 1
        if nodes > node_limit:
            cutoff = True; return
        if len(chosen) == need:
            found = tuple(chosen); return
        if len(chosen) + len(candidates) - start < need:
            return
        for i in range(start, len(candidates)):
            if len(chosen) + len(candidates) - i < need:
                return
            q = candidates[i]
            if allowed(q, chosen):
                rec(i + 1, chosen + [q])
                if found is not None or cutoff:
                    return
    rec(0, [])
    return found, nodes, cutoff


def controls():
    # Covers of a path: compare the exact enumerator with all subsets.
    edges, forced, target = ((0, 1), (1, 2), (2, 3), (3, 4)), frozenset({0}), 3
    brute = {frozenset(forced | set(s)) for r in range(6) for s in itertools.combinations(range(5), r)
             if len(forced | set(s)) == target and all(set(e) & (forced | set(s)) for e in edges)}
    got = set(exact_covers(edges, forced, target))
    assert got == brute and min_cover_degree_two(edges, forced) == target
    # Brute force a real F_3^7 mini-instance; third points that are merely
    # candidates must not make a pair illegal unless selected too.
    z = (0,) * N; a = (1, 0, 0, 0, 0, 0, 0)
    qs = ((0, 1, 0, 0, 0, 0, 0), (0, 2, 0, 0, 0, 0, 0),
          (1, 1, 0, 0, 0, 0, 0), (2, 1, 0, 0, 0, 0, 0))
    brute_ok = []
    for s in itertools.combinations(qs, 2):
        if valid((z, a) + s): brute_ok.append(s)
    got_ext, nodes, cutoff = exact_extension(qs, (z, a), 2, 10000)
    assert brute_ok and got_ext in brute_ok and not cutoff
    no, _, no_cut = exact_extension(qs, (z, a), 5, 10000)
    assert no is None and not no_cut
    return {'cover_fixture_covers': len(got), 'extension_bruteforce_witnesses': len(brute_ok),
            'extension_positive_nodes': nodes}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=1740)
    ap.add_argument('--node-limit', type=int, default=500000)
    ap.add_argument('--out', required=True)
    ap.add_argument('--start-pair', type=int, default=0)
    ap.add_argument('--start-cover', type=int, default=0)
    args = ap.parse_args()
    started_wall, started = time.time(), time.monotonic()
    deadline = started + args.seconds
    base = tuple(cap236()); assert valid(base)
    base_set = set(base)
    outside = tuple(dec(i) for i in range(3 ** N) if dec(i) not in base_set)
    all_blockers = {q: tuple(tuple(e) for e in blockers(base, q)) for q in outside}
    eligible = tuple(q for q in outside if len(all_blockers[q]) == 10)
    pairs = []
    all_hist = {}
    for i, a in enumerate(eligible):
        for z in eligible[i + 1:]:
            union = tuple(sorted({tuple(sorted(e)) for e in all_blockers[a]} | {tuple(sorted(e)) for e in all_blockers[z]}))
            pair_line = third(a, z)
            forced = frozenset({pair_line}) if pair_line in base_set else frozenset()
            minimum = min_cover_degree_two(union, forced)
            all_hist[str(minimum)] = all_hist.get(str(minimum), 0) + 1
            if minimum == 16:
                pairs.append((a, z, union, forced))
    canonical = json.dumps({'points': [list(p) for p in base]}, separators=(',', ':'))
    result = {
        'artifact_status': 'new c8 exact 16-deletion two-anchor experiment; CF-236 recovered control',
        'algorithm': 'all exact minimum covers for 16-cover ten-blocker anchor pairs, then exact three-uniform extension',
        'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(started_wall)),
        'seconds_budget': args.seconds, 'node_limit_per_extension': args.node_limit,
        'python': sys.version, 'platform': platform.platform(), 'baseline_size': len(base),
        'baseline_sha256_canonical_json': hashlib.sha256(canonical.encode()).hexdigest(),
        'eligible_anchors': len(eligible), 'all_pair_minimum_histogram': all_hist,
        'selected_pairs': len(pairs), 'selected_pair_minimum': 16,
        'covers_enumerated': 0, 'cases_started': 0, 'cases_completed': 0, 'cases_pruned_cardinality': 0,
        'extension_invocations': 0, 'extension_nodes': 0, 'cases_cutoff': 0, 'records': [],
        'best_size': 236, 'timed_out': False, 'resume': None, 'controls': controls()
    }
    cursor = {'pair_index': len(pairs), 'cover_index': 0, 'state': 'done'}
    for pi, (a, z, union, forced) in enumerate(pairs):
        if pi < args.start_pair:
            continue
        covers = exact_covers(union, forced, 16)
        assert covers and all(len(c) == 16 for c in covers)
        result['covers_enumerated'] += len(covers)
        begin_cover = args.start_cover if pi == args.start_pair else 0
        for ci, deleted in enumerate(covers):
            if ci < begin_cover:
                continue
            if time.monotonic() >= deadline:
                result['timed_out'] = True
                cursor = {'pair_index': pi, 'cover_index': ci, 'state': 'cover'}
                break
            result['cases_started'] += 1
            cands, retained = additional_candidates(base, outside, (a, z), deleted, all_blockers)
            # 236 - 16 + 2 forced anchors needs 15 more to reach 237.
            if len(cands) < 15:
                result['cases_pruned_cardinality'] += 1; result['cases_completed'] += 1
                continue
            result['extension_invocations'] += 1
            ext, nodes, cutoff = exact_extension(cands, retained | {a, z}, 15, args.node_limit)
            result['extension_nodes'] += nodes
            if cutoff:
                result['cases_cutoff'] += 1
            else:
                result['cases_completed'] += 1
            if ext is not None:
                trial = tuple(p for p in base if p not in deleted) + (a, z) + ext
                assert valid(trial) and len(trial) >= 237
                result['best_size'] = max(result['best_size'], len(trial))
                result['records'].append({'pair': [list(a), list(z)], 'cover': list(sorted(deleted)),
                                          'extension': [list(q) for q in ext], 'size': len(trial)})
        if result['timed_out']:
            break
    result['resume'] = cursor
    result['elapsed_seconds'] = time.time() - started_wall
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ('selected_pairs', 'covers_enumerated', 'cases_started',
          'cases_completed', 'cases_pruned_cardinality', 'extension_invocations', 'extension_nodes',
          'cases_cutoff', 'best_size', 'timed_out', 'resume', 'elapsed_seconds')}, sort_keys=True))


if __name__ == '__main__':
    main()
