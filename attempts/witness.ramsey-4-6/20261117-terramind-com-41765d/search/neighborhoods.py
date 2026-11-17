"""Search fixed-core neighborhoods in the published catalogue and in low-conflict graphs."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import random

from pysat.solvers import Solver

from search import as_rows, clique_iter, counts, edges, extension, log, save, solve, with_deleted


def graph6(record):
    if record.startswith('>>graph6<<'):
        record = record[10:]
    assert record and ord(record[0])-63 == 35
    n = 35
    bits = [((ord(c)-63) >> i) & 1 for c in record[1:] for i in reversed(range(6))]
    assert len(bits) == 600 and all(63 <= ord(c) <= 126 for c in record[1:]) and not any(bits[595:])
    rows = [[0]*n for _ in range(n)]
    for (j,i), value in zip(((j,i) for j in range(n) for i in range(j)),bits):
        rows[i][j] = rows[j][i] = value
    if counts(rows,4,6) != [0,0]:
        rows = [[int(i != j) - b for j,b in enumerate(row)] for i,row in enumerate(rows)]
    assert counts(rows,4,6) == [0,0]
    return rows


def check_drup(clauses, proof):
    # Ignore deletions. Keeping already verified clauses can only aid unit propagation.
    db = [tuple(clause) for clause in clauses]
    additions = 0
    for entry in proof:
        if entry.startswith('d '):
            continue
        numbers = tuple(map(int,entry.split()))
        assert numbers[-1] == 0
        clause = numbers[:-1]
        truth = {-lit for lit in clause}
        conflict = any(-lit in truth for lit in truth)
        changed = True
        while changed and not conflict:
            changed = False
            for existing in db:
                if any(lit in truth for lit in existing):
                    continue
                unresolved = [lit for lit in existing if -lit not in truth]
                if not unresolved:
                    conflict = True
                    break
                if len(unresolved) == 1:
                    truth.add(unresolved[0])
                    changed = True
        assert conflict, ('proof step failed reverse unit propagation', clause)
        additions += 1
        db.append(clause)
        if not clause:
            return additions
    raise ValueError('proof did not derive the empty clause')


def proof_controls(include_four):
    baseline = as_rows('baseline.json')
    cases = [((),1),((0,),2),((0,1),3)]
    if include_four:
        cases = [((0,1,2),4)]
    for cut, added in cases:
        core = with_deleted(baseline,cut)
        _, cnf = extension(core,added,4,6)
        with Solver(name='glucose42',bootstrap_with=cnf,with_proof=True) as solver:
            assert solver.solve() is False
            proof = solver.get_proof()
            assert proof
        steps = check_drup(cnf,proof)
        log(case='proof',cut=cut,added=added, status='UNSAT',rup_additions=steps, clauses=len(cnf))
        Path('extension-proof-'+str(added)+'.drup').write_text('\n'.join(proof)+'\n')


def catalogue(path):
    for index,line in enumerate(Path(path).read_text(encoding='ascii').splitlines()):
        if not line:
            continue
        core = graph6(line)
        name = f'catalogue-input-{index:02}'
        save(f'{name}.json',core)
        solve(f'catalogue-ext1-{index:02}',36,*extension(core,1,4,6),4,6,core)


def delete_more(deadline, label, core, count, limit, seed, conflicts):
    cuts = list(combinations(range(len(core)),count))
    if limit < len(cuts):
        cuts = random.Random(seed).sample(cuts,limit)
    log(method='delete-more',label=label,vertices_removed=count,cases_planned=len(cuts),seed=seed,conflicts=conflicts)
    totals = Counter()
    for cut in cuts:
        if datetime.now(timezone.utc) >= deadline:
            break
        kept = with_deleted(core,cut)
        added = 36-len(kept)
        outcome = solve(f'{label}-ext{added}-'+ '-'.join(map(str,cut)),36,
                        *extension(kept,added,4,6),4,6,kept,budget=conflicts)
        totals[str(outcome)] += 1
        if outcome is True:
            break
    log(method='delete-more',label=label,counts=dict(totals))


def hit_cliques(rows, seed, sample, min_size, max_size):
    randomizer = random.Random(seed)
    n = len(rows)
    dirty = [set(c) for color,size in enumerate((4,6)) for c in clique_iter(rows,size,color)]
    distinct = set()
    for trial in range(sample*10):
        if len(distinct) >= sample:
            break
        target = min_size + trial % (max_size-min_size+1)
        remove = set()
        remaining = dirty[:]
        while remaining and len(remove) < target:
            weights = Counter(v for clique in remaining for v in clique)
            scores = {v: weight*randomizer.uniform(0.3,1.0) for v,weight in weights.items()}
            v = max(scores,key=scores.get)
            remove.add(v)
            remaining = [clique for clique in remaining if v not in clique]
        if remaining:
            continue
        remove.update(randomizer.sample(sorted(set(range(n))-remove),target-len(remove)))
        cut = tuple(sorted(remove))
        if cut in distinct:
            continue
        distinct.add(cut)
        yield cut


def neighborhood_cnf(rows, mutable, sizes):
    """Allow exactly mutable edges to change. Enumerate colour-compatible cliques."""
    n = len(rows)
    variables = {edge:i+1 for i,edge in enumerate(sorted(mutable))}
    clauses = []
    for color,size in enumerate(sizes):
        compatible = [
            sum(1<<j for j in range(i+1,n) if rows[i][j]==color or (i,j) in variables)
            for i in range(n)
        ]
        sign = 1 if color == 0 else -1

        def visit(candidates, need, chosen, clause):
            if not need:
                clauses.append(clause)
                return
            while candidates.bit_count() >= need:
                low = candidates & -candidates
                candidates ^= low
                v = low.bit_length()-1
                new_literals = tuple(sign*variables[u,v] for u in chosen if (u,v) in variables)
                visit(candidates & compatible[v],need-1,(*chosen,v),clause+new_literals)

        visit((1<<n)-1,size,(),())
    return variables,clauses


def repair_controls():
    for n,sizes,path in [(17,(4,4),'local-control44.json'),(24,(4,5),'local-control45.json'),
                         (35,(4,6),'baseline.json')]:
        rows = as_rows(path)
        broken = [r.copy() for r in rows]
        noisy = [e for e in edges(5) if rows[e[0]][e[1]]]
        for i,j in noisy:
            broken[i][j] = broken[j][i] = 0
        assert sum(counts(broken,*sizes)) > 0
        mutable = {(i,j) for i,j in edges(n) if i<3} | set(noisy)
        args = neighborhood_cnf(broken,mutable,sizes)
        assert any(len(c)>1 for c in args[1]) and not any(len(c)==0 for c in args[1])
        assert solve(f'repair-control-{n}',n,*args,*sizes,broken,budget=10000) is True

def repair(deadline, path, label, attempts, seed, conflicts, extra):
    rows = as_rows(path)
    log(method='repair',label=label,input=str(path),counts=counts(rows,4,6),seed=seed,attempts=attempts,conflicts=conflicts,extra=extra)
    totals = Counter()
    for cut in hit_cliques(rows,seed,attempts,4,7):
        if datetime.now(timezone.utc) >= deadline:
            break
        if extra:
            mutable = {(i,j) for i,j in edges(len(rows)) if i in cut or j in cut}
            available = sorted(set(edges(len(rows)))-mutable)
            added_edges = random.Random(str((seed,cut))).sample(available,extra)
            args = neighborhood_cnf(rows,mutable | set(added_edges),(4,6))
            core = rows
        else:
            core = with_deleted(rows,cut)
            args = extension(core,len(cut),4,6)
        outcome = solve(f'{label}-repair-'+ '-'.join(map(str,cut)),36,*args,4,6,core,budget=conflicts)
        totals[str(outcome)] += 1
        if outcome is True:
            break
    log(method='repair',label=label,counts=dict(totals))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest='action',required=True)
    proof = subparsers.add_parser('proof-controls')
    proof.add_argument('--include-four',action='store_true')
    subparsers.add_parser('repair-controls')
    cat = subparsers.add_parser('catalogue')
    cat.add_argument('input')
    for action in ('delete','repair'):
        sub = subparsers.add_parser(action)
        sub.add_argument('deadline',type=datetime.fromisoformat)
        sub.add_argument('input')
        sub.add_argument('label')
        sub.add_argument('--limit',type=int,required=True)
        sub.add_argument('--seed',type=int,required=True)
        sub.add_argument('--conflicts',type=int,default=10000)
        if action == 'delete':
            sub.add_argument('--remove',type=int,required=True)
        else:
            sub.add_argument('--extra',type=int,default=0)
    args = parser.parse_args()
    if args.action == 'proof-controls':
        proof_controls(args.include_four)
    elif args.action == 'repair-controls':
        repair_controls()
    elif args.action == 'catalogue':
        catalogue(args.input)
    elif args.action == 'delete':
        delete_more(args.deadline,args.label,as_rows(args.input),args.remove,args.limit,args.seed,args.conflicts)
    else:
        repair(args.deadline,args.input,args.label,args.limit,args.seed,args.conflicts,args.extra)
