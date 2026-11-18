#!/usr/bin/env python3
"""Bounded deterministic 11-pair exchange search for the recovered CF-236 cap.

This deliberately does not repeat c4's 10-pair size-10 sweep.  An 11-pair
anchor needs one deletion from every disjoint blocker pair.  A retained core
then has 225 points, so a 237-cap needs the forced anchor plus an independent
set of at least 11 other compatible points.  The decision solver is exact up
to its explicitly logged node cutoff; a cutoff is never reported as a prune.
"""
import argparse, hashlib, itertools, json, platform, sys, time
from pathlib import Path

from cap7_hittingset_search import cap236, blockers, dec, forbidden_by_retained, third, valid

N = 7

def candidate_buckets(base, outside, anchor, pairs, all_blockers):
    """Return candidates for every one-of-each-pair deletion mask at once.

    A candidate q survives exactly when every q blocker has an endpoint in the
    selected deletion set.  A 2048-bit integer represents the masks satisfying
    a clause, so this precomputation replaces 2048 repeated O(225^2) scans.
    """
    width, count = 1 << len(pairs), 1 << len(pairs)
    full = (1 << width) - 1
    choice = {}
    where = {}
    for i, pair in enumerate(pairs):
        for bit, vertex in enumerate(pair):
            where[vertex] = (i, bit)
            choice[i, bit] = sum(1 << mask for mask in range(width) if (mask >> i) & 1 == bit)
    index = {p: i for i, p in enumerate(base)}
    buckets = [[] for _ in range(count)]
    for q in outside:
        if q == anchor:
            continue
        allowed = full
        for edge in all_blockers[q]:
            clause = 0
            for vertex in edge:
                loc = where.get(vertex)
                if loc is not None:
                    clause |= choice[loc]
            allowed &= clause
            if not allowed:
                break
        # A line anchor+q+r additionally requires r's deletion if r is in
        # the base cap.  (If r is not in it, no retained-core constraint.)
        r = index.get(third(anchor, q))
        if allowed and r is not None:
            loc = where.get(r)
            allowed &= choice[loc] if loc is not None else 0
        while allowed:
            low = allowed & -allowed
            mask = low.bit_length() - 1
            buckets[mask].append(q)
            allowed ^= low
    return buckets

def direct_candidates(base, outside, anchor, deleted, all_blockers):
    """Slow reference predicate used only for the bucket control."""
    index = {p: i for i, p in enumerate(base)}
    out = []
    for q in outside:
        if q == anchor:
            continue
        if not all(set(edge) & deleted for edge in all_blockers[q]):
            continue
        r = index.get(third(anchor, q))
        if r is None or r in deleted:
            out.append(q)
    return out

def conflict_graph(forced, candidates, retained):
    forced = set(forced)
    blocked = set(candidates) | forced | set(retained)
    graph = [set() for _ in candidates]
    for i, a in enumerate(candidates):
        for j in range(i + 1, len(candidates)):
            b = candidates[j]
            if third(a, b) in blocked:
                graph[i].add(j); graph[j].add(i)
    return graph

def find_independent(graph, need, node_limit):
    """Exact decision MIS search, bounded solely by node_limit."""
    nodes = 0
    cutoff = False
    answer = None
    def rec(avail, chosen):
        nonlocal nodes, cutoff, answer
        if answer is not None or cutoff:
            return
        nodes += 1
        if nodes > node_limit:
            cutoff = True
            return
        if len(chosen) >= need:
            answer = chosen[:]
            return
        if len(chosen) + len(avail) < need:
            return
        # A high-degree branch gives the same include/exclude exhaustive tree
        # but normally supplies a tighter cardinality bound sooner.
        v = max(avail, key=lambda z: (len(graph[z] & avail), -z))
        rec(avail - {v} - graph[v], chosen + [v])
        rec(avail - {v}, chosen)
    rec(set(range(len(graph))), [])
    return answer, nodes, cutoff

def brute_max(graph):
    """Exhaustive oracle for only the <=12 vertex control instance."""
    best = []
    for mask in range(1 << len(graph)):
        chosen = [i for i in range(len(graph)) if mask >> i & 1]
        if len(chosen) <= len(best):
            continue
        if all(j not in graph[i] for at, i in enumerate(chosen) for j in chosen[at + 1:]):
            best = chosen
    return best

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=1740)
    ap.add_argument('--node-limit', type=int, default=20000)
    ap.add_argument('--out', required=True)
    ap.add_argument('--start-anchor', type=int, default=0)
    ap.add_argument('--start-mask', type=int, default=0)
    a = ap.parse_args()
    began_wall, began_mono = time.time(), time.monotonic()
    deadline = began_mono + a.seconds
    base = cap236()
    canonical = json.dumps({'points': [list(p) for p in base]}, separators=(',', ':'))
    assert valid(base)
    universe = tuple(dec(i) for i in range(3 ** N))
    outside = [p for p in universe if p not in set(base)]
    by_pairs = {}
    for p in outside:
        by_pairs.setdefault(len(blockers(base, p)), []).append(p)
    anchors = by_pairs.get(11, [])
    assert anchors, 'the measured histogram has no 11-pair anchors'

    # Positive control: an actual candidate graph from this construction,
    # checked against all subsets of its first 12 vertices.
    control_forced = ((0,) * N,)
    control_candidates = [(1,0,0,0,0,0,0), (0,1,0,0,0,0,0), (1,1,0,0,0,0,0)]
    assert valid(control_forced + tuple(control_candidates))
    control_graph = conflict_graph(control_forced, control_candidates, ())
    oracle = brute_max(control_graph)
    got, control_nodes, control_cutoff = find_independent(control_graph, len(oracle), 1_000_000)
    impossible, _, impossible_cutoff = find_independent(control_graph, len(oracle) + 1, 1_000_000)
    assert got is not None and not control_cutoff and impossible is None and not impossible_cutoff

    result = {
      'artifact_status': 'new c5 experiment; baseline recovered byte-for-byte from c4 commit 363bcd93',
      'algorithm': 'deterministic 11-pair minimum-deletion exchange; bounded exact 11-extension decision solver',
      'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(began_wall)),
      'seconds_budget': a.seconds, 'node_limit_per_case': a.node_limit,
      'python': sys.version, 'platform': platform.platform(),
      'baseline_size': len(base), 'baseline_sha256_canonical_json': hashlib.sha256(canonical.encode()).hexdigest(),
      'blocker_pair_histogram': {str(k): len(v) for k, v in sorted(by_pairs.items())},
      'anchors_with_11_pairs': len(anchors), 'cases_total': len(anchors) * (1 << 11),
      'cases_started': 0, 'cases_completed': 0, 'cases_pruned': 0, 'cases_cutoff': 0,
      'candidate_checks': 0, 'solver_nodes': 0, 'records': [], 'best_size': 236,
      'control': {'vertices': len(control_graph), 'bruteforce_max': len(oracle),
                  'decision_found': len(got), 'decision_nodes': control_nodes,
                  'impossible_target_rejected': len(oracle) + 1},
      'resume': None, 'timed_out': False,
    }
    stop_anchor, stop_mask = len(anchors), 0
    all_blockers = {q: blockers(base, q) for q in outside}
    # Check the fast 2048-mask bucket construction against a deliberately
    # simple reference for a deterministic prefix of the first anchor.
    bucket_control_pairs = blockers(base, anchors[0])
    bucket_control = candidate_buckets(base, outside, anchors[0], bucket_control_pairs, all_blockers)
    for control_mask in range(32):
        control_deleted = {pair[(control_mask >> i) & 1] for i, pair in enumerate(bucket_control_pairs)}
        assert bucket_control[control_mask] == direct_candidates(base, outside, anchors[0], control_deleted, all_blockers)
    result['bucket_control_masks_checked'] = 32
    for ai in range(a.start_anchor, len(anchors)):
        pairs = blockers(base, anchors[ai])
        assert len(pairs) == 11 and len({v for pair in pairs for v in pair}) == 22
        buckets = candidate_buckets(base, outside, anchors[ai], pairs, all_blockers)
        mask_start = a.start_mask if ai == a.start_anchor else 0
        for mask in range(mask_start, 1 << 11):
            if time.monotonic() >= deadline:
                result['timed_out'] = True; stop_anchor, stop_mask = ai, mask; break
            deleted = {pair[(mask >> i) & 1] for i, pair in enumerate(pairs)}
            cands = buckets[mask]
            result['cases_started'] += 1
            # 225 retained + forced anchor: eleven more points are required.
            if len(cands) < 11:
                result['cases_pruned'] += 1; result['cases_completed'] += 1; continue
            retained = tuple(q for i, q in enumerate(base) if i not in deleted)
            graph = conflict_graph((anchors[ai],), cands, retained)
            chosen, nodes, cutoff = find_independent(graph, 11, a.node_limit)
            result['candidate_checks'] += len(cands); result['solver_nodes'] += nodes
            if cutoff:
                result['cases_cutoff'] += 1
            else:
                result['cases_completed'] += 1
            if chosen is not None:
                trial = retained + (anchors[ai],) + tuple(cands[i] for i in chosen)
                assert valid(trial) and len(trial) >= 237
                result['records'].append({'anchor': list(anchors[ai]), 'mask': mask,
                  'deleted_indices': sorted(deleted), 'candidate_count': len(cands),
                  'extension': [list(cands[i]) for i in chosen], 'size': len(trial)})
                result['best_size'] = max(result['best_size'], len(trial))
                stop_anchor, stop_mask = ai, mask + 1
                result['resume'] = {'anchor_index': stop_anchor, 'next_mask': stop_mask}
                result['elapsed_seconds'] = time.time() - began_wall
                Path(a.out).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
                print(json.dumps({'record_found': True, 'size': len(trial), 'resume': result['resume']}, sort_keys=True))
                return
        if result['timed_out']:
            break
    result['resume'] = {'anchor_index': stop_anchor, 'next_mask': stop_mask}
    result['elapsed_seconds'] = time.time() - began_wall
    Path(a.out).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ('cases_started', 'cases_completed', 'cases_pruned', 'cases_cutoff', 'solver_nodes', 'best_size', 'timed_out', 'resume', 'elapsed_seconds')}, sort_keys=True))

if __name__ == '__main__':
    main()
