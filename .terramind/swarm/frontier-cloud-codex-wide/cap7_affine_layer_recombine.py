#!/usr/bin/env python3
"""Deterministic nonlocal affine-layer recombination around CF-236.

Split F_3^7 by the first coordinate.  The x_0=0 layer is retained while
independent affine automorphisms of F_3^6 are applied to the two 112-point
layers.  The aggregate pool contains several images of each nonzero layer,
so it has room above 236; every accepted point is nevertheless checked
against all previously selected points by the exact F_3 line equation.

This is an exploratory construction search, not an optimality proof.  The
identity/identity image is retained solely as the positive baseline control;
all reported nonlocal constructions use different maps on the two layers.
"""
import argparse, hashlib, itertools, json, platform, random, sys, time
from pathlib import Path

from cap7_hittingset_search import N, cap236, third, valid


I = ((1,0,0,0,0,0),(0,1,0,0,0,0),(0,0,1,0,0,0),
     (0,0,0,1,0,0),(0,0,0,0,1,0),(0,0,0,0,0,1))

# All matrices are invertible elementary maps.  Each nonidentity entry differs
# across the two layers, preventing the pair from being a common relabeling of
# the baseline construction.
MAPS1 = (
    ('id', I, (0,0,0,0,0,0)),
    ('s01+t2', ((1,1,0,0,0,0),(0,1,0,0,0,0),(0,0,1,0,0,0),
                (0,0,0,1,0,0),(0,0,0,0,1,0),(0,0,0,0,0,1)), (0,0,1,0,0,0)),
    ('d0+s23', ((2,0,0,0,0,0),(0,1,0,0,0,0),(0,0,1,1,0,0),
                (0,0,0,1,0,0),(0,0,0,0,1,0),(0,0,0,0,0,1)), (0,1,0,0,0,0)),
    ('swap45+t0', ((1,0,0,0,0,0),(0,1,0,0,0,0),(0,0,1,0,0,0),
                   (0,0,0,1,0,0),(0,0,0,0,0,1),(0,0,0,0,1,0)), (1,0,0,0,0,0)),
)
MAPS2 = (
    ('id', I, (0,0,0,0,0,0)),
    ('s12+t4', ((1,0,0,0,0,0),(0,1,1,0,0,0),(0,0,1,0,0,0),
                (0,0,0,1,0,0),(0,0,0,0,1,0),(0,0,0,0,0,1)), (0,0,0,0,1,0)),
    ('d3+s50', ((1,0,0,0,0,0),(0,1,0,0,0,0),(0,0,1,0,0,0),
                (0,0,0,2,0,0),(0,0,0,0,1,0),(1,0,0,0,0,1)), (0,0,0,1,0,0)),
    ('swap14+t5', ((1,0,0,0,0,0),(0,0,0,0,1,0),(0,0,1,0,0,0),
                   (0,0,0,1,0,0),(0,1,0,0,0,0),(0,0,0,0,0,1)), (0,0,0,0,0,2)),
)


def affine(p, matrix, shift):
    q = [sum(matrix[i][j] * p[j] for j in range(6)) % 3 for i in range(6)]
    return tuple((q[i] + shift[i]) % 3 for i in range(6))


def image(layer, spec):
    _, matrix, shift = spec
    return tuple(sorted((layer[0][0],) + affine(p[1:], matrix, shift) for p in layer))


def compatible(p, chosen):
    selected = set(chosen)
    return all(third(p, q) not in selected for q in chosen)


def greedy(pool, seed, fixed=()):
    """Exact incremental line filtering, with a reproducible shuffled order."""
    chosen = list(fixed)
    rest = [p for p in pool if p not in set(chosen)]
    random.Random(seed).shuffle(rest)
    for p in rest:
        if compatible(p, chosen):
            chosen.append(p)
    assert valid(tuple(chosen))
    return tuple(sorted(chosen))


def brute_valid(points):
    return not any(tuple((a[i] + b[i] + c[i]) % 3 for i in range(N)) == (0,) * N
                   for a, b, c in itertools.combinations(points, 3))


def controls(base, layers):
    # The identity construction is a required positive control.  On small
    # subsets, direct triple enumeration agrees with the incremental filter.
    assert valid(base) and greedy(base, 0, base) == tuple(sorted(base))
    sample = tuple(sorted(base))[:9]
    assert valid(sample) == brute_valid(sample)
    prefix = sample[:5]
    for p in sample[5:]:
        assert compatible(p, prefix) == valid(prefix + (p,))
    # An image of a cap layer is itself cap-free under the affine map.
    assert valid(image(layers[1], MAPS1[1])) and valid(image(layers[2], MAPS2[1]))
    return {'identity_positive_control_size': len(base), 'small_bruteforce_points': len(sample),
            'small_bruteforce_agrees': True, 'image_internal_cap_checks': 2}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=1740)
    ap.add_argument('--restarts', type=int, default=512)
    ap.add_argument('--out', required=True)
    ap.add_argument('--start-construction', type=int, default=0)
    ap.add_argument('--start-restart', type=int, default=0)
    args = ap.parse_args()
    started_wall, started = time.time(), time.monotonic()
    deadline = started + args.seconds
    base = tuple(cap236()); assert valid(base)
    layers = {v: tuple(p for p in base if p[0] == v) for v in range(3)}
    assert [len(layers[v]) for v in range(3)] == [12,112,112]
    imgs1 = [image(layers[1], s) for s in MAPS1]
    imgs2 = [image(layers[2], s) for s in MAPS2]
    aggregate = tuple(sorted(set(layers[0]).union(*map(set, imgs1), *map(set, imgs2))))
    canonical = json.dumps({'points': [list(p) for p in base]}, separators=(',', ':'))
    constructions = [(i, j) for i in range(len(MAPS1)) for j in range(len(MAPS2))
                     if not (i == 0 and j == 0)]
    result = {
        'artifact_status': 'new c9 affine-layer recombination; CF-236 recovered control',
        'algorithm': 'independent F_3^6 affine images by x0 layer plus exact incremental line filtering',
        'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(started_wall)),
        'seconds_budget': args.seconds, 'restarts_per_construction': args.restarts,
        'python': sys.version, 'platform': platform.platform(),
        'baseline_size': len(base), 'baseline_sha256_canonical_json': hashlib.sha256(canonical.encode()).hexdigest(),
        'slice_coordinate': 0, 'slice_sizes': {str(v): len(layers[v]) for v in range(3)},
        'documented_split': 'retain x0=0; independently map x0=1 and x0=2 tails by listed affine F3^6 maps',
        'layer1_maps': [s[0] for s in MAPS1], 'layer2_maps': [s[0] for s in MAPS2],
        'aggregate_pool_size_upper_bound': len(aggregate),
        'pair_pool_size_upper_bound': 236, 'nonlocal_constructions_total': len(constructions),
        'domains_completed': 0, 'restarts_completed': 0, 'unresolved': 0,
        'best_valid_size': len(base), 'best_kind': 'identity/identity positive control',
        'best_witness_sha256': hashlib.sha256(canonical.encode()).hexdigest(),
        'records': [], 'timed_out': False, 'resume': None, 'controls': controls(base, layers),
    }
    cursor = {'construction_index': len(constructions), 'restart': 0, 'state': 'done'}
    # The full augmented pool supplies off-baseline points and has a size upper
    # bound above 236.  Search it first, then every distinct two-layer pair.
    domains = [('aggregate', aggregate, -1, -1)] + [
        (f'{MAPS1[i][0]} / {MAPS2[j][0]}', tuple(sorted(set(layers[0]) | set(imgs1[i]) | set(imgs2[j]))), i, j)
        for i, j in constructions]
    for di, (label, pool, i, j) in enumerate(domains):
        if di < args.start_construction:
            continue
        initial = args.start_restart if di == args.start_construction else 0
        domain_best = 0
        for r in range(initial, args.restarts):
            if time.monotonic() >= deadline:
                result['timed_out'] = True; result['unresolved'] += 1
                cursor = {'construction_index': di, 'restart': r, 'state': 'greedy'}; break
            witness = greedy(pool, (di + 1) * 1000003 + r)
            result['restarts_completed'] += 1
            domain_best = max(domain_best, len(witness))
            if len(witness) > result['best_valid_size']:
                payload = json.dumps({'points': [list(p) for p in witness]}, separators=(',', ':'))
                result['best_valid_size'] = len(witness); result['best_kind'] = label
                result['best_witness_sha256'] = hashlib.sha256(payload.encode()).hexdigest()
                result['records'].append({'construction': label, 'domain_pool_size': len(pool),
                    'restart': r, 'size': len(witness), 'witness_sha256': result['best_witness_sha256'],
                    'points': [list(p) for p in witness]})
        if result['timed_out']:
            break
        result['domains_completed'] += 1
        result.setdefault('construction_summaries', []).append({'construction': label,
            'pool_size_upper_bound': len(pool), 'best_valid_size': domain_best, 'restarts': args.restarts})
    result['resume'] = cursor
    result['elapsed_seconds'] = time.time() - started_wall
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ('aggregate_pool_size_upper_bound', 'nonlocal_constructions_total',
        'domains_completed', 'restarts_completed', 'unresolved', 'best_valid_size', 'timed_out',
        'resume', 'elapsed_seconds')}, sort_keys=True))


if __name__ == '__main__':
    main()
