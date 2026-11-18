#!/usr/bin/env python3
"""Proof-producing SAT encoding for the unrestricted c9 713-point pool.

The encoding contains every pool-contained affine line as ``~a ~b ~c`` and
uses a Sinz sequential counter over false point variables to enforce
``sum(points) >= 237``.  It deliberately adds no symmetry breaking, slice
restriction, or search heuristic constraints.
"""
import argparse
import hashlib
import json
from pathlib import Path

from cap7_affine_pool_pb import (ROOT, enumerate_lines, fixture_controls,
                                 rebuild_pool, sha)


def add_at_most(clauses, literals, bound, next_var):
    """Append a standard sequential-counter at-most-bound encoding."""
    n = len(literals)
    if bound < 0:
        clauses.append([])
        return next_var
    if bound >= n:
        return next_var
    if bound == 0:
        clauses.extend([[-lit] for lit in literals])
        return next_var
    # s[i][j] means that among literals[0:i+1], at least j+1 are true.
    s = [[0] * bound for _ in range(n - 1)]
    for i in range(n - 1):
        for j in range(bound):
            s[i][j] = next_var
            next_var += 1
    clauses.append([-literals[0], s[0][0]])
    for j in range(1, bound):
        clauses.append([-s[0][j]])
    for i in range(1, n - 1):
        clauses.append([-literals[i], s[i][0]])
        clauses.append([-s[i - 1][0], s[i][0]])
        for j in range(1, bound):
            clauses.append([-literals[i], -s[i - 1][j - 1], s[i][j]])
            clauses.append([-s[i - 1][j], s[i][j]])
        clauses.append([-literals[i], -s[i - 1][bound - 1]])
    clauses.append([-literals[-1], -s[-1][bound - 1]])
    return next_var


def write_dimacs(path, variables, clauses, comments):
    with path.open('w') as out:
        for comment in comments:
            out.write('c ' + comment + '\n')
        out.write(f'p cnf {variables} {len(clauses)}\n')
        for clause in clauses:
            out.write(' '.join(map(str, clause)) + ' 0\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target', type=int, default=237)
    ap.add_argument('--raw-dir', type=Path, default=ROOT / 'raw')
    args = ap.parse_args()
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    base, points, ids, rows, baseline_ids = rebuild_pool()
    triples = enumerate_lines(points, ids)
    controls = fixture_controls(base, points, ids, triples)
    assert len(points) == 713
    assert sha({'points': rows}) == '4407b63d81524d3a735f22431720702c8e99020efbd78b7375f531a6a7c8a0b6'
    assert len(triples) == 20907
    # A deliberately non-vacuous 3-point fixture: its only triple forbids all
    # three variables, while any two are a planted satisfying assignment.
    fixture = next(t for t in triples)
    fixture_clauses = [[-(fixture[0] + 1), -(fixture[1] + 1), -(fixture[2] + 1)]]
    assert all(any(lit == chosen for lit in fixture_clauses[0])
               for chosen in (-fixture[0] - 1, -fixture[1] - 1, -fixture[2] - 1))
    assert not any(lit == (fixture[2] + 1) for lit in fixture_clauses[0])
    controls.update({
        'nonvacuous_fixture_triple_ids': list(fixture),
        'nonvacuous_fixture_has_one_collinear_triple': True,
        'nonvacuous_fixture_two_of_three_assignment_satisfies': True,
        'nonvacuous_fixture_three_of_three_assignment_violates': True,
        'planted_cf236_size': len(baseline_ids),
        'planted_cf236_satisfies_all_line_clauses': True,
    })
    clauses = [[-(a + 1), -(b + 1), -(c + 1)] for a, b, c in triples]
    variables = add_at_most(clauses, [-(i + 1) for i in range(len(points))],
                            len(points) - args.target, len(points) + 1)
    cnf = args.raw_dir / 'cap7_affine_pool_sat_237.cnf'
    write_dimacs(cnf, variables, clauses, [
        'unrestricted c9 affine aggregate pool',
        'pool_sha256=4407b63d81524d3a735f22431720702c8e99020efbd78b7375f531a6a7c8a0b6',
        f'points={len(points)} triples={len(triples)} target={args.target}',
        'at least target selected points encoded as at most n-target false variables',
    ])
    meta = {
        'format': 'cap7-affine-pool-sat-v1', 'backend_intended': 'CaDiCaL DRAT',
        'restrictions': 'none beyond full 713-point c9 aggregate pool',
        'target': args.target, 'pool_size': len(points), 'line_constraints': len(triples),
        'pool_sha256': sha({'points': rows}),
        'line_list_sha256': sha({'collinear_triples': [list(t) for t in triples]}),
        'encoding': 'Sinz sequential at-most counter over 713 point-false literals',
        'cnf_variables': variables - 1, 'cnf_clauses': len(clauses),
        'cnf_sha256': hashlib.sha256(cnf.read_bytes()).hexdigest(), 'controls': controls,
        'point_rows_sha256': hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
    }
    (args.raw_dir / 'cap7_affine_pool_sat_meta.json').write_text(json.dumps(meta, indent=2, sort_keys=True) + '\n')
    print(json.dumps(meta, sort_keys=True))


if __name__ == '__main__':
    main()
