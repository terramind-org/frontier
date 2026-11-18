#!/usr/bin/env python3
"""Full c9 affine-pool SAT model using a bitonic sorting-network counter.

This is deliberately independent from the prior Sinz sequential-counter CNF:
every pool-contained line remains a three-negative clause, but cardinality is
expressed by a Batcher bitonic network over the 713 selection bits padded with
311 forced-false bits.  The 237th descending output is asserted true.
"""
import argparse
import hashlib
import json
from pathlib import Path

from cap7_affine_pool_pb import ROOT, enumerate_lines, fixture_controls, rebuild_pool, sha


class Builder:
    def __init__(self, point_count):
        self.next_var = point_count + 1
        self.clauses = []
        self.ops = []

    def fresh(self):
        answer = self.next_var
        self.next_var += 1
        return answer

    def comparator(self, left, right, descending):
        # hi = left OR right; lo = left AND right.  The order of the outputs
        # determines whether this wire segment is ascending or descending.
        hi, lo = self.fresh(), self.fresh()
        self.clauses += [[-left, hi], [-right, hi], [left, right, -hi],
                         [left, -lo], [right, -lo], [-left, -right, lo]]
        self.ops.append((left, right, hi, lo, descending))
        return (hi, lo) if descending else (lo, hi)

    def merge(self, wires, descending):
        if len(wires) == 1:
            return wires
        even = self.merge(wires[::2], descending)
        odd = self.merge(wires[1::2], descending)
        out = []
        for a, b in zip(even, odd):
            out.extend(self.comparator(a, b, descending))
        return out

    def sort(self, wires, descending=True):
        if len(wires) == 1:
            return wires
        half = len(wires) // 2
        return self.merge(self.sort(wires[:half], True) + self.sort(wires[half:], False), descending)


def eval_network(builder, selected, padded_inputs):
    values = {i + 1: (i in selected) for i in range(713)}
    for wire in padded_inputs[713:]:
        values[wire] = False
    for left, right, hi, lo, _ in builder.ops:
        values[hi] = values[left] or values[right]
        values[lo] = values[left] and values[right]
    return values


def satisfied(clauses, values):
    return all(any(values[abs(lit)] == (lit > 0) for lit in clause) for clause in clauses)


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
    ap.add_argument('--raw-dir', type=Path, default=ROOT / 'raw/c17')
    args = ap.parse_args()
    assert 0 < args.target <= 713
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    base, points, ids, rows, baseline_ids = rebuild_pool()
    triples = enumerate_lines(points, ids)
    assert len(points) == 713
    assert sha({'points': rows}) == '4407b63d81524d3a735f22431720702c8e99020efbd78b7375f531a6a7c8a0b6'
    assert len(triples) == 20907
    controls = fixture_controls(base, points, ids, triples)
    b = Builder(len(points))
    padded = list(range(1, 714))
    while len(padded) < 1024:
        wire = b.fresh()
        padded.append(wire)
        b.clauses.append([-wire])
    output = b.sort(padded, True)
    clauses = [[-(a + 1), -(bb + 1), -(c + 1)] for a, bb, c in triples] + b.clauses
    clauses.append([output[args.target - 1]])
    vals236 = eval_network(b, set(baseline_ids), padded)
    # Every auxiliary variable has a simulated value, making this a direct
    # clause-level positive control rather than a claim about the encoding.
    assert satisfied(clauses[:-1], vals236)
    assert vals236[output[235]] is True and vals236[output[236]] is False
    # A non-vacuous direct 3-variable line control, independent of network.
    fixture = next(t for t in triples)
    direct = [[-(fixture[0] + 1), -(fixture[1] + 1), -(fixture[2] + 1)]]
    assert satisfied(direct, {fixture[0] + 1: True, fixture[1] + 1: True, fixture[2] + 1: False})
    assert not satisfied(direct, {fixture[0] + 1: True, fixture[1] + 1: True, fixture[2] + 1: True})
    cnf = args.raw_dir / f'cap7_affine_pool_sorting_{args.target}.cnf'
    write_dimacs(cnf, b.next_var - 1, clauses, [
        'unrestricted c9 affine aggregate pool',
        'pool_sha256=4407b63d81524d3a735f22431720702c8e99020efbd78b7375f531a6a7c8a0b6',
        f'points=713 triples=20907 target={args.target}',
        'Batcher bitonic sorting network, descending; assert target-th output true',
    ])
    meta = {
        'format': 'cap7-affine-pool-sat-v2',
        'restrictions': 'none beyond full 713-point c9 aggregate pool',
        'target': args.target, 'pool_size': len(points), 'line_constraints': len(triples),
        'pool_sha256': sha({'points': rows}),
        'line_list_sha256': sha({'collinear_triples': [list(t) for t in triples]}),
        'encoding': 'Batcher bitonic sorting network over 713 points plus 311 forced-false pads',
        'counter_comparators': len(b.ops), 'cnf_variables': b.next_var - 1,
        'cnf_clauses': len(clauses), 'cnf_sha256': hashlib.sha256(cnf.read_bytes()).hexdigest(),
        'controls': {**controls,
                     'nonvacuous_direct_triple_ids': list(fixture),
                     'nonvacuous_two_of_three_satisfies': True,
                     'nonvacuous_three_of_three_violates': True,
                     'planted_cf236_satisfies_lines_and_network_before_threshold': True,
                     'threshold_236_output_true': True,
                     'threshold_237_output_false': True},
        'point_rows_sha256': hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
    }
    (args.raw_dir / f'cap7_affine_pool_sorting_{args.target}_meta.json').write_text(json.dumps(meta, indent=2, sort_keys=True) + '\n')
    print(json.dumps(meta, sort_keys=True))


if __name__ == '__main__':
    main()
