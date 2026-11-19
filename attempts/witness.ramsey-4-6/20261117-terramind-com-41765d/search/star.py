"""Export a fixed-core one-vertex formula and minimize violations by branch and bound."""
import argparse
from datetime import datetime
from pathlib import Path
import re

from pysat.examples.rc2 import RC2
from pysat.formula import WCNF

from campaign import OUT, launch
from search import as_rows, counts, extension, log, save


def run(deadline,label,sizes,core,seed,limit,expected=None,compare_rc2=False):
    name = 'star-'+label
    path = OUT/(name+'.clauses')
    n = len(core)+1
    _,clauses = extension(core,1,*sizes)
    path.write_text(''.join(
        f'{sum(1<<(abs(lit)-1) for lit in clause)} {int(clause[0]>0)}\n'
        for clause in clauses
    ))
    destination = OUT/name
    log(case=name,seed_counts=counts(as_rows(seed),*sizes),soft_clauses=len(clauses))
    if not launch(deadline,name,['./ramsey','exact-star',str(n),*map(str,sizes),str(seed),
                                 str(path),str(destination)],limit):
        return
    events = (OUT/(name+'.log')).read_text()
    end = re.search(r'^\S+ end nodes=(\d+) covered=(\d+) optimum=(\d+)$',events,re.MULTILINE)
    best = counts(as_rows(destination.with_suffix('.json')),*sizes)
    if end:
        total = int(end[3])
        assert int(end[2])==1<<(n-1) and total==sum(best)
        if expected is not None:
            assert total==expected
        if compare_rc2:
            wcnf = WCNF()
            wcnf.extend(clauses,weights=[1]*len(clauses))
            with RC2(wcnf,solver='cadical195') as check:
                assert check.compute() and check.cost==total
        log(case=name,status='OPTIMAL',counts=best,nodes=int(end[1]),covered=int(end[2]),
            independent_rc2=compare_rc2)
    else:
        assert expected is None and not compare_rc2
        log(case=name,status='UNKNOWN',counts=best)


def seed_from_core(core,label):
    path = OUT/(label+'-star-seed.json')
    n = len(core)+1
    save(path,[r+[0] for r in core]+[[0]*n])
    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('deadline',type=datetime.fromisoformat)
    args = parser.parse_args()
    for n, sizes, name in [(17,(4,4),'local-control44'),(24,(4,5),'local-control45')]:
        core = [r[:-1] for r in as_rows(name+'.json')[:-1]]
        seed = seed_from_core(core,name)
        assert sum(counts(as_rows(seed),*sizes))>0
        run(args.deadline,f'positive-{n}',sizes,core,seed,45,expected=0)
    core = as_rows('local-control44.json')
    run(args.deadline,'negative-18',(4,4),core,seed_from_core(core,'negative-18'),45,compare_rc2=True)
    run(args.deadline,'published-36',(4,6),as_rows('baseline.json'),Path('best-single-extension.json'),1100)
