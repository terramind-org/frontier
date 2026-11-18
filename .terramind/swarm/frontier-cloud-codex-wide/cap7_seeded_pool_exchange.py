#!/usr/bin/env python3
"""Seeded restricted exchanges in the saved unrestricted 713-point pool.

This is deliberately a local search, not a claim about the full pool.  Each
domain freezes CF-236 except the endpoints of the blockers of two pool-only
anchors.  The free incumbent endpoints and every pool point compatible with
the frozen core form the local candidate set.  Exact line checks are used on
every selected set; deterministic greedy restarts explore the restricted
domains.  Anchor pairs are selected by shared CF-236 blocker endpoints and
only use affine-pool points absent from all earlier 10/11-blocker sweeps.
"""
import argparse
import hashlib
import itertools
import json
import platform
import random
import sys
import time
from pathlib import Path

from cap7_affine_pool_pb import ROOT, enumerate_lines, fixture_controls, rebuild_pool, sha
from cap7_hittingset_search import blockers, third, valid


EXPECTED_POOL = '4407b63d81524d3a735f22431720702c8e99020efbd78b7375f531a6a7c8a0b6'


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(',', ':'))


def hash_ids(ids):
    return hashlib.sha256(canonical(sorted(ids)).encode()).hexdigest()


def no_line_with_core(point, core):
    core_set = set(core)
    return all(third(a, b) != point for a, b in itertools.combinations(core, 2))


def add_ok(point, chosen):
    chosen_set = set(chosen)
    return no_line_with_core(point, chosen) and all(third(point, q) not in chosen_set for q in chosen)


def forbidden_pairs(points):
    return {third(a, b) for a, b in itertools.combinations(points, 2)}


def greedy(core, forced, candidates, seed):
    chosen = list(core)
    chosen_set = set(chosen)
    core_forbidden = forbidden_pairs(core)
    def append_if_ok(p):
        if p in core_forbidden:
            return False
        if any(third(p, q) in chosen_set for q in chosen):
            return False
        chosen.append(p)
        chosen_set.add(p)
        return True
    for p in forced:
        if not append_if_ok(p):
            return None
    order = [p for p in candidates if p not in forced]
    random.Random(seed).shuffle(order)
    for p in order:
        if p not in chosen_set:
            append_if_ok(p)
    assert valid(tuple(chosen))
    return tuple(sorted(chosen))


def controls(base, points, ids, triples):
    base_ids = {ids[p] for p in base}
    # Independent cubic enumeration is already checked in fixture_controls.
    independent = fixture_controls(base, points, ids, triples)
    # A non-vacuous local positive-gain toy: retain a deterministic 4-point
    # core, seed it with two compatible pool points, then add a third.  Its
    # selected size is 7 versus the 4-point incumbent seed and direct line
    # enumeration verifies the gain.
    core = tuple(base[:4])
    pool_only = [p for p in points if ids[p] not in base_ids]
    planted = []
    for p in pool_only:
        if add_ok(p, core + tuple(planted)):
            planted.append(p)
            if len(planted) == 3:
                break
    toy = core + tuple(planted)
    assert len(planted) == 3 and valid(toy)
    assert any(tuple((a[j] + b[j] + c[j]) % 3 for j in range(7)) == (0,) * 7
                   for a, b, c in itertools.combinations(core + (planted[0], planted[1],), 3)) is False
    return {
        **independent,
        'positive_gain_toy_incumbent_size': len(core),
        'positive_gain_toy_selected_size': len(toy),
        'positive_gain_toy_gain': len(toy) - len(core),
        'positive_gain_toy_direct_line_free': True,
        'positive_gain_toy_point_ids': [ids[p] for p in toy],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=1500.0)
    ap.add_argument('--domains', type=int, default=256)
    ap.add_argument('--restarts', type=int, default=128)
    ap.add_argument('--raw-dir', type=Path, default=ROOT / 'raw')
    args = ap.parse_args()
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    wall, began = time.time(), time.monotonic()
    deadline = began + args.seconds
    base, points, ids, rows, baseline_ids = rebuild_pool()
    triples = enumerate_lines(points, ids)
    assert len(points) == 713 and len(triples) == 20907
    assert sha({'points': rows}) == EXPECTED_POOL
    controls_out = controls(base, points, ids, triples)
    base_set, pool_set = set(base), set(points)
    # Earlier runs exhaustively addressed single anchors with 10 or 11 blocker
    # pairs.  Excluding those exact outside points makes this new local domain
    # disjoint at the anchor level; only pool-only points with a nonidentity
    # affine provenance are retained.
    # The first hitting-set result preserves the 10-pair coordinates.  The
    # later 11-pair artifact keeps only a count, so regenerate its exact
    # coordinate class from the same baseline rather than pretending it was
    # serialized.  This is a deterministic anchor-level deduplication.
    earlier = {tuple(p) for p in json.loads((ROOT / 'raw' / 'cap7_hittingset_result.json').read_text())['minimum_points']}
    for p in points:
        if p not in base_set and len(blockers(base, p)) == 11:
            earlier.add(p)
    novel = []
    for row in rows:
        p = tuple(row['point'])
        nonidentity = any(not origin.endswith(':id') and 'retained' not in origin for origin in row['origins'])
        if p not in base_set and p not in earlier and nonidentity:
            novel.append(p)
    bpairs = {p: blockers(base, p) for p in novel}
    endpoint_sets = {p: frozenset(i for pair in bpairs[p] for i in pair) for p in novel}
    pair_specs = []
    for a, b in itertools.combinations(novel, 2):
        shared = len(endpoint_sets[a] & endpoint_sets[b])
        if shared:
            pair_specs.append(( -shared, len(endpoint_sets[a] | endpoint_sets[b]), ids[a], ids[b], a, b))
    pair_specs.sort()
    selected = pair_specs[:args.domains]
    result = {
        'format': 'cap7-seeded-restricted-exchange-v1',
        'full_pool_status': 'unresolved: prior unrestricted target >=237 has no witness or full certificate',
        'pool_sha256': EXPECTED_POOL, 'pool_size': len(points), 'line_constraints': len(triples),
        'baseline_size': len(base), 'baseline_valid': valid(base),
        'algorithm': 'freeze CF236 outside joint blocker endpoints; deterministic greedy exact-line search on compatible pool alternatives',
        'restrictions': 'selected local neighborhoods only; not a full-pool proof search',
        'novel_affine_anchor_count': len(novel), 'excluded_prior_anchor_count': len(earlier),
        'candidate_pair_count_with_shared_blockers': len(pair_specs),
        'selected_domains': len(selected), 'domains_budget': args.domains,
        'restarts_per_domain': args.restarts, 'seconds_budget': args.seconds,
        'controls': controls_out, 'domains_completed': 0, 'domains_pruned_by_cardinality': 0,
        'restarts_completed': 0, 'best_verified_size': len(base),
        'best_verified_kind': 'CF-236 control', 'records': [], 'timed_out': False,
        'resume': None, 'domain_summaries': [],
    }
    seen_neighborhoods = set()
    cursor = {'domain_index': len(selected), 'restart': 0, 'state': 'done'}
    for di, spec in enumerate(selected):
        if time.monotonic() >= deadline:
            result['timed_out'] = True; cursor = {'domain_index': di, 'restart': 0, 'state': 'before-domain'}; break
        neg_shared, _, _, _, a, b = spec
        free = endpoint_sets[a] | endpoint_sets[b]
        n_hash = hash_ids(free)
        if n_hash in seen_neighborhoods:
            continue
        seen_neighborhoods.add(n_hash)
        core = tuple(p for i, p in enumerate(base) if i not in free)
        core_forbidden = forbidden_pairs(core)
        compatible = tuple(p for p in points if p not in core and p not in core_forbidden)
        # Both anchors must survive the local preprocessing, otherwise this is
        # not the documented seeded family.
        if a not in compatible or b not in compatible or len(core) + len(compatible) <= 236:
            result['domains_pruned_by_cardinality'] += 1
            result['domain_summaries'].append({'domain_index': di, 'free_endpoint_count': len(free),
                'shared_endpoint_count': -neg_shared, 'compatible_pool_count': len(compatible),
                'neighborhood_sha256': n_hash, 'status': 'pruned'})
            result['domains_completed'] += 1
            continue
        best = 0
        for restart in range(args.restarts):
            if time.monotonic() >= deadline:
                result['timed_out'] = True; cursor = {'domain_index': di, 'restart': restart, 'state': 'greedy'}; break
            # Put both anchors first in alternate order; this is a seeded
            # exchange rather than a generic pool restart.
            seed = (di + 1) * 1000003 + restart
            chosen = greedy(core, (a, b), compatible, seed)
            if chosen is None:
                result['domains_pruned_by_cardinality'] += 1
                break
            result['restarts_completed'] += 1
            best = max(best, len(chosen))
            if len(chosen) > result['best_verified_size']:
                result['best_verified_size'] = len(chosen)
                result['best_verified_kind'] = 'seeded shared-blocker affine-pool exchange'
                result['records'].append({'domain_index': di, 'restart': restart, 'size': len(chosen),
                    'anchor_ids': [ids[a], ids[b]], 'free_endpoint_count': len(free),
                    'neighborhood_sha256': n_hash, 'candidate_ids': [ids[p] for p in chosen],
                    'candidate_direct_line_free': valid(chosen)})
        if result['timed_out']:
            break
        result['domains_completed'] += 1
        result['domain_summaries'].append({'domain_index': di, 'anchor_ids': [ids[a], ids[b]],
            'shared_endpoint_count': -neg_shared, 'free_endpoint_count': len(free),
            'compatible_pool_count': len(compatible), 'neighborhood_sha256': n_hash,
            'best_valid_size': best, 'status': 'completed'})
    result['unique_neighborhoods_examined'] = len(seen_neighborhoods)
    result['resume'] = cursor
    result['elapsed_seconds'] = time.time() - wall
    path = args.raw_dir / 'cap7_seeded_pool_exchange_result.json'
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    (args.raw_dir / 'cap7_seeded_pool_exchange_control.json').write_text(json.dumps(controls_out, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ('pool_size', 'line_constraints', 'novel_affine_anchor_count',
        'candidate_pair_count_with_shared_blockers', 'selected_domains', 'domains_completed',
        'domains_pruned_by_cardinality', 'restarts_completed', 'best_verified_size', 'timed_out',
        'resume', 'elapsed_seconds')}, sort_keys=True))


if __name__ == '__main__':
    main()
