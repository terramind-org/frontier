"""Exact fixed-core Ramsey extensions and unrestricted SAT controls."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
import json
from pathlib import Path
from time import monotonic

from pysat.card import CardEnc, EncType
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
from pysat.solvers import Solver


def log(**fields):
    print(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(), **fields)), flush=True)


def save(path, rows):
    Path(path).write_text(json.dumps(dict(n=len(rows), adjacency=[''.join(map(str, row)) for row in rows])) + '\n')


def as_rows(path):
    return [list(map(int, row)) for row in json.loads(Path(path).read_text())['adjacency']]


def from_exoo(path):
    rows = Path(path).read_text().split()
    assert len(rows) == 35 and all(len(row) == 35 and set(row) <= {'0','1'} for row in rows)
    assert all(row[i] == '0' and all(row[j] == rows[j][i] for j in range(35))
               for i,row in enumerate(rows))
    return [[int(i != j and v == '1') for j, v in enumerate(row)] for i, row in enumerate(rows)]


def clique_iter(rows, size, color):
    if size == 0:
        yield ()
        return
    n = len(rows)
    neighbors = [sum(1 << j for j in range(i + 1, n) if rows[i][j] == color) for i in range(n)]

    def visit(candidates, need, chosen):
        if need == 0:
            yield chosen
        while need and candidates.bit_count() >= need:
            low = candidates & -candidates
            candidates ^= low
            v = low.bit_length() - 1
            yield from visit(candidates & neighbors[v], need - 1, (*chosen, v))

    yield from visit((1 << n) - 1, size, ())


def counts(rows, zero, one):
    return [sum(1 for _ in clique_iter(rows, size, color)) for color, size in enumerate((zero, one))]


def edges(n):
    return list(combinations(range(n), 2))


def extension(core, added, zero, one):
    m = len(core)
    n = m + added
    variables = {e: i + 1 for i, e in enumerate(e for e in edges(n) if e[1] >= m)}
    clauses = []
    for color, size in enumerate((zero, one)):
        sign = 1 if color == 0 else -1
        assert not any(clique_iter(core, size, color))
        for new in range(1, min(added, size) + 1):
            for old_vertices in clique_iter(core, size - new, color):
                for new_vertices in combinations(range(m, n), new):
                    clauses.append(tuple(sign * variables[e] for e in combinations(old_vertices + new_vertices, 2) if e[1] >= m))
    return variables, clauses


def model_rows(n, variables, model, core=()):
    values = {literal for literal in model if literal > 0}
    rows = [[0] * n for _ in range(n)]
    for i, j in edges(n):
        value = int(variables[i, j] in values) if (i, j) in variables else core[i][j]
        rows[i][j] = rows[j][i] = value
    return rows


def solve(label, n, variables, clauses, zero, one, core=(), budget=None):
    start = monotonic()
    with Solver(name='cadical195', bootstrap_with=clauses) as solver:
        if budget is None:
            result = solver.solve()
        else:
            solver.conf_budget(budget)
            result = solver.solve_limited()
        stats = solver.accum_stats()
        rows = model_rows(n, variables, solver.get_model(), core) if result is True else None
    if rows is not None:
        assert counts(rows, zero, one) == [0, 0]
        save(f'{label}.json', rows)
    log(case=label, status={True:'SAT', False:'UNSAT', None:'UNKNOWN'}[result],
        variables=max(variables.values()), clauses=len(clauses), seconds=round(monotonic()-start, 4), **stats)
    return result


def with_deleted(rows, deleted):
    keep = [i for i in range(len(rows)) if i not in deleted]
    return [[rows[i][j] for j in keep] for i in keep]


def unrestricted(n, zero, one, redundant_bounds=None):
    variables = dict(zip(edges(n), range(1, n*(n-1)//2+1)))
    clauses = [
        tuple(sign * variables[e] for e in combinations(vertices, 2))
        for size, sign in ((zero, 1), (one, -1))
        for vertices in combinations(range(n), size)
    ]
    if redundant_bounds is not None:
        top = len(variables)
        for v in range(n):
            incident = [variables[tuple(sorted((v, w)))] for w in range(n) if v != w]
            for sign, max_degree in zip((-1, 1), redundant_bounds):
                card = CardEnc.atmost(lits=[sign*x for x in incident], bound=max_degree,
                                    top_id=top, encoding=EncType.seqcounter)
                clauses.extend(card.clauses)
                top = card.nv
    return variables, clauses


def run_controls():
    for n, zero, one, bounds in [(14, 3, 5, (8,4)), (18, 4, 4, (8,8))]:
        args = unrestricted(n, zero, one, bounds)
        assert solve(f'control-{zero}{one}-{n}', n, *args, zero, one) is False
    for n, zero, one in [(13,3,5),(17,3,6),(17,4,4),(24,4,5)]:
        args = unrestricted(n, zero, one)
        solve(f'control-{zero}{one}-{n}', n, *args, zero, one, budget=500000)


def raw_negative_controls():
    # Vertex zero must have at least five colour-0 neighbours or nine colour-1
    # neighbours in K14. In K18, one of its colour-degrees is at least nine.
    # Relabel the neighbours, and use colour symmetry for the diagonal case.
    cases = [(14,3,5,0,5),(14,3,5,1,9),(18,4,4,1,9)]
    for n, zero, one, color, degree in cases:
        variables, clauses = unrestricted(n,zero,one)
        sign = 1 if color else -1
        clauses.extend((sign*variables[0,j],) for j in range(1,degree+1))
        label = f'raw-control-{zero}{one}-{n}-star{color}'
        assert solve(label,n,variables,clauses,zero,one,budget=500000) is False


def run_extensions(three):
    base = as_rows('baseline.json')
    cases = [((), 1)] + [((i,), 2) for i in range(35)]
    if three:
        cases += [(d, 3) for d in combinations(range(35), 2)]
    core = with_deleted(base, (34,))
    assert solve('recover35', 35, *extension(core, 1, 4, 6), 4, 6, core) is True
    for removed, added in cases:
        core = with_deleted(base, removed)
        name = f'ext{added}-' + ('-'.join(map(str, removed)) or 'original')
        variables, clauses = extension(core, added, 4, 6)
        solve(name, 36, variables, clauses, 4, 6, core)


def minimize_extension():
    core = as_rows('baseline.json')
    variables, clauses = extension(core, 1, 4, 6)
    start = monotonic()
    formula = WCNF()
    formula.extend(clauses, weights=[1]*len(clauses))
    with RC2(formula, solver='cadical195') as optimizer:
        model = optimizer.compute()
        rows = model_rows(36, variables, model, core)
        violation_counts = counts(rows, 4, 6)
        assert sum(violation_counts) == optimizer.cost
        literals = set(model)
        assert sum(violation_counts) == sum(
            not any(lit in literals for lit in clause) for clause in clauses
        )
        save('best-single-extension-exact.json', rows)
        log(case='best-single-extension-exact', status='OPTIMAL', counts=violation_counts, cost=optimizer.cost,
            seconds=round(monotonic()-start, 4), clauses_by_length=dict(Counter(map(len, clauses))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['baseline', 'controls', 'raw-negative-controls', 'extend', 'extend-three', 'minimize-extension'])
    parser.add_argument('--input', default='input/r4.6.35')
    args = parser.parse_args()
    if args.action == 'baseline':
        rows = from_exoo(args.input)
        assert counts(rows, 4, 6) == [0, 0]
        save('baseline.json', rows)
        broken = [row.copy() for row in rows]
        for i, j in edges(4):
            broken[i][j] = broken[j][i] = 0
        assert sum(counts(broken, 4, 6)) > 0
        save('broken.json', broken)
        for name, matrix in [('baseline', rows), ('broken', broken)]:
            log(case=name, counts=counts(matrix, 4, 6))
    elif args.action == 'controls':
        run_controls()
    elif args.action == 'raw-negative-controls':
        raw_negative_controls()
    elif args.action == 'minimize-extension':
        minimize_extension()
    else:
        run_extensions(args.action == 'extend-three')
