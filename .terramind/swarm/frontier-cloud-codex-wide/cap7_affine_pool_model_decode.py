#!/usr/bin/env python3
"""Decode and independently validate a CaDiCaL competition-format model.

Only variables 1..713 select affine-pool points.  Auxiliary sorting-network
variables are deliberately ignored after a full DIMACS clause scan has
validated the complete assignment.
"""
import argparse
import hashlib
import json
from pathlib import Path

from cap7_affine_pool_pb import enumerate_lines, rebuild_pool, sha
from cap7_hittingset_search import valid


def parse_dimacs(path):
    clauses = []
    variables = None
    for line in Path(path).read_text().splitlines():
        if not line or line.startswith('c'):
            continue
        if line.startswith('p '):
            _, kind, nvars, _ = line.split()
            assert kind == 'cnf'
            variables = int(nvars)
        else:
            values = [int(x) for x in line.split()]
            assert values[-1] == 0
            clauses.append(values[:-1])
    assert variables is not None
    return variables, clauses


def parse_model(path):
    values = {}
    for line in Path(path).read_text(errors='replace').splitlines():
        if line.startswith('v '):
            for lit in map(int, line.split()[1:]):
                if lit:
                    values[abs(lit)] = lit > 0
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cnf', type=Path, required=True)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    nvars, clauses = parse_dimacs(args.cnf)
    values = parse_model(args.model)
    complete = len(values) == nvars and set(values) == set(range(1, nvars + 1))
    cnf_satisfied = complete and all(any(values[abs(lit)] == (lit > 0) for lit in c) for c in clauses)
    base, points, ids, rows, _ = rebuild_pool()
    triples = enumerate_lines(points, ids)
    selected_ids = [i for i in range(713) if values.get(i + 1, False)]
    selected_points = [points[i] for i in selected_ids]
    result = {
        'cnf_sha256': hashlib.sha256(args.cnf.read_bytes()).hexdigest(),
        'pool_sha256': sha({'points': rows}),
        'cnf_variables': nvars,
        'model_assigned_variables': len(values),
        'model_complete': complete,
        'cnf_satisfied_by_model': cnf_satisfied,
        'selected_count': len(selected_ids),
        'selected_ids': selected_ids,
        'selected_points': [list(p) for p in selected_points],
        'direct_line_scan_valid': all(len(set(t).intersection(selected_ids)) <= 2 for t in triples),
        'geometry_valid': valid(tuple(selected_points)),
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    assert result['model_complete'] and result['cnf_satisfied_by_model']
    assert result['direct_line_scan_valid'] and result['geometry_valid']
    print(json.dumps({k: result[k] for k in ('model_complete', 'cnf_satisfied_by_model', 'selected_count', 'direct_line_scan_valid', 'geometry_valid')}, sort_keys=True))


if __name__ == '__main__':
    main()
