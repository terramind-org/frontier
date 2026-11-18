#!/usr/bin/env python3
"""Exact PB feasibility test for the c9 affine 713-point aggregate pool.

The pool is rebuilt from the four documented affine maps on each nonzero
x0-layer of CF-236.  Every collinear triple contained in the aggregate pool
gets the PB inequality x_a + x_b + x_c <= 2, and the sole global condition is
sum x_i >= target.  Thus this is the full saved pool, with no symmetry,
slice, or other restriction beyond the c9 pool provenance itself.
"""
import argparse
import hashlib
import itertools
import json
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_array

from cap7_hittingset_search import N, cap236, third, valid
from cap7_affine_layer_recombine import MAPS1, MAPS2, image


ROOT = Path('.terramind/swarm/frontier-cloud-codex-wide')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def rebuild_pool():
    base = tuple(sorted(cap236()))
    assert len(base) == 236 and valid(base)
    layers = {v: tuple(p for p in base if p[0] == v) for v in range(3)}
    assert [len(layers[v]) for v in range(3)] == [12, 112, 112]
    origins = {}
    for p in layers[0]:
        origins.setdefault(p, []).append('x0=0:retained:CF236')
    for layer_value, specs in ((1, MAPS1), (2, MAPS2)):
        for label, matrix, shift in specs:
            for p in image(layers[layer_value], (label, matrix, shift)):
                origins.setdefault(p, []).append(f'x0={layer_value}:{label}')
    points = tuple(sorted(origins))
    ids = {p: i for i, p in enumerate(points)}
    rows = [
        {'id': i, 'point': list(p), 'origins': sorted(origins[p])}
        for i, p in enumerate(points)
    ]
    baseline_ids = [ids[p] for p in base]
    return base, points, ids, rows, baseline_ids


def enumerate_lines(points, ids):
    point_set = set(points)
    triples = set()
    for a, b in itertools.combinations(points, 2):
        c = third(a, b)
        if c in point_set:
            triples.add(tuple(sorted((ids[a], ids[b], ids[c]))))
    return tuple(sorted(triples))


def brute_triples(points):
    return tuple(sorted(
        tuple(sorted(combo))
        for combo in itertools.combinations(range(len(points)), 3)
        if tuple((points[combo[0]][j] + points[combo[1]][j] + points[combo[2]][j]) % 3
                 for j in range(N)) == (0,) * N
    ))


def fixture_controls(base, points, ids, triples):
    # Independent O(n^3) triple enumeration agrees on a deterministic small
    # fixture.  Baseline membership and every full-pool line check form the
    # positive control for the target encoding.
    sample = points[:12]
    sample_ids = {p: i for i, p in enumerate(sample)}
    fast = enumerate_lines(sample, sample_ids)
    slow = brute_triples(sample)
    assert fast == slow
    base_ids = {ids[p] for p in base}
    assert len(base_ids) == 236
    assert all(len(base_ids.intersection(t)) <= 2 for t in triples)
    assert valid(base)
    return {
        'small_fixture_points': len(sample),
        'small_fixture_line_count': len(slow),
        'small_fixture_fast_equals_bruteforce': True,
        'known_feasible_baseline_size': len(base),
        'known_feasible_baseline_satisfies_every_pool_line_constraint': True,
    }


def matrix_from_triples(n, triples):
    # Triple rows followed by one cardinality row: -sum(x) <= -target.
    indptr = [0]
    indices = []
    data = []
    for triple in triples:
        indices.extend(triple)
        data.extend((1.0, 1.0, 1.0))
        indptr.append(len(indices))
    # CSC construction is column oriented, so build coordinate arrays instead.
    rr = []
    cc = []
    dd = []
    for r, triple in enumerate(triples):
        for c in triple:
            rr.append(r); cc.append(c); dd.append(1.0)
    return rr, cc, dd


def solve(n, triples, target, seconds):
    rr, cc, dd = matrix_from_triples(n, triples)
    card_row = len(triples)
    rr.extend([card_row] * n)
    cc.extend(range(n))
    dd.extend([-1.0] * n)
    a = csc_array((np.array(dd), (np.array(rr), np.array(cc))),
                  shape=(card_row + 1, n))
    lower = np.full(card_row + 1, -np.inf)
    upper = np.ones(card_row + 1) * 2.0
    upper[card_row] = -float(target)
    started = time.monotonic()
    result = milp(
        c=np.zeros(n), integrality=np.ones(n), bounds=Bounds(0, 1),
        constraints=LinearConstraint(a, lower, upper),
        options={'time_limit': seconds, 'mip_rel_gap': 0.0, 'disp': False},
    )
    elapsed = time.monotonic() - started
    chosen = []
    if result.x is not None:
        chosen = [i for i, x in enumerate(result.x) if x > 0.5]
    return result, elapsed, chosen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=1740.0)
    ap.add_argument('--target', type=int, default=237)
    ap.add_argument('--raw-dir', type=Path, default=ROOT / 'raw')
    args = ap.parse_args()
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    base, points, ids, rows, baseline_ids = rebuild_pool()
    triples = enumerate_lines(points, ids)
    controls = fixture_controls(base, points, ids, triples)
    instance = {
        'format': 'cap7-affine-pool-pb-v1',
        'pool_provenance': {
            'source_commit': '3280617b',
            'source_script': 'cap7_affine_layer_recombine.py',
            'split': 'x0=0 retained; x0=1 uses MAPS1; x0=2 uses MAPS2',
            'restrictions': 'none beyond the full c9 713-point aggregate pool',
            'map_names_x0_1': [x[0] for x in MAPS1],
            'map_names_x0_2': [x[0] for x in MAPS2],
        },
        'points': rows,
        'baseline_ids': baseline_ids,
        'collinear_triples': [list(t) for t in triples],
        'canonical_pool_sha256': sha({'points': rows}),
        'canonical_line_list_sha256': sha({'collinear_triples': [list(t) for t in triples]}),
    }
    (args.raw_dir / 'cap7_affine_pool_pb_instance.json').write_text(json.dumps(instance, indent=2) + '\n')
    (args.raw_dir / 'cap7_affine_pool_pb_control.json').write_text(json.dumps(controls, indent=2) + '\n')
    solver, elapsed, chosen = solve(len(points), triples, args.target, args.seconds)
    outcome = {
        0: 'optimal_or_feasible', 1: 'time_or_iteration_limit', 2: 'infeasible',
        3: 'unbounded', 4: 'solver_error',
    }.get(int(solver.status), 'unknown')
    result = {
        'backend': 'scipy.optimize.milp / HiGHS',
        'backend_version': __import__('scipy').__version__,
        'threads': 1,
        'target': args.target,
        'pool_size': len(points),
        'pool_sha256': instance['canonical_pool_sha256'],
        'line_constraints': len(triples),
        'line_list_sha256': instance['canonical_line_list_sha256'],
        'restrictions': 'none beyond full 713-point c9 aggregate pool',
        'controls': controls,
        'seconds_budget': args.seconds,
        'elapsed_seconds': elapsed,
        'solver_status_code': int(solver.status),
        'solver_outcome': outcome,
        'solver_message': str(solver.message),
        'mip_node_count': int(getattr(solver, 'mip_node_count', 0) or 0),
        'mip_dual_bound': (None if getattr(solver, 'mip_dual_bound', None) is None
                           else float(solver.mip_dual_bound)),
        'mip_gap': (None if getattr(solver, 'mip_gap', None) is None else float(solver.mip_gap)),
        'chosen_count': len(chosen),
        'chosen_ids': chosen,
        'candidate_valid_exact': (valid(tuple(points[i] for i in chosen)) if chosen else None),
        'proof_artifact': None,
        'unsat_proof_checked_independently': False,
        'platform': platform.platform(),
        'python': sys.version,
        'env_threads': {k: os.environ.get(k) for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'HIGHS_THREADS')},
    }
    if int(solver.status) == 2:
        result['proof_artifact'] = 'HiGHS reported infeasible; this backend did not emit a standalone independently checkable proof certificate.'
    (args.raw_dir / 'cap7_affine_pool_pb_result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ('pool_size', 'line_constraints', 'pool_sha256',
          'line_list_sha256', 'solver_outcome', 'elapsed_seconds', 'chosen_count',
          'mip_node_count', 'mip_dual_bound', 'mip_gap')}, sort_keys=True))


if __name__ == '__main__':
    main()
