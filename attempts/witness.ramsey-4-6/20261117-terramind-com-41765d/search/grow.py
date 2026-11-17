"""Perturb and repair 35-vertex graphs, then try extending new isomorphism classes."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import random

from automorphisms import isomorphisms
from campaign import OUT, launch, result
from search import as_rows, counts, edges, extension, log, save, solve
from supplemental import check_candidate


def perturb(rows,seed,number,width):
    rng = random.Random(seed)
    n = len(rows)
    graph = [line.copy() for line in rows]
    touched = rng.sample(range(n),width)
    pool = [e for e in edges(n) if any(v in touched for v in e)]
    selected = rng.sample(pool,number)
    for a,b in selected:
        graph[a][b] ^= 1
        graph[b][a] ^= 1
    return graph,selected


def replay(deadline,path,label,sizes,seed,number,p4,restarts,steps):
    rows = as_rows(path)
    graph,selected = perturb(rows,seed,number,3)
    if sum(counts(graph,*sizes))==0:
        log(case=label,event='perturb-valid',path=path,flips=selected,seed=seed)
        save(OUT/(label+'.json'),graph)
        return True
    log(case=label,path=path,flips=selected,seed=seed,p4=p4,steps=steps,restarts=restarts)
    damaged = OUT/(label+'-damaged.json')
    save(damaged,graph)
    if not launch(deadline,label,[
        './ramsey','anneal',str(len(rows)),*map(str,sizes),str(seed),str(steps),str(restarts),
        '1',str(p4),str(damaged),str(OUT/label),'-','0.6','0.055'
    ],60):
        return False
    return result(OUT/(label+'.log'))==0


def signature(rows):
    return tuple(sorted(map(sum,rows)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('deadline',type=datetime.fromisoformat)
    args = parser.parse_args()
    for n,sizes,path in [(17,(4,4),'local-control44.json'),(24,(4,5),'local-control45.json')]:
        assert replay(args.deadline,path,f'growth-control-{n}',sizes,467100+n,6,0.02,8,500000)
    known = {}
    source = sorted(Path('.').glob('catalogue-input-*.json'))
    for path in source:
        rows = as_rows(path)
        known.setdefault(signature(rows),[]).append(rows)
    assert source
    for i,path in enumerate(source*2):
        if datetime.now(timezone.utc)>=args.deadline:
            break
        label = f'grow35-{i:02}'
        p4 = 0.025 if i<len(source) else 0
        seed = 4662000+i
        if not replay(args.deadline,str(path),label,(4,6),seed,5+2*(i%7),p4,5,550000):
            continue
        candidate = OUT/(label+'.json')
        rows = as_rows(candidate)
        assert counts(rows,4,6)==[0,0]
        bucket = known.setdefault(signature(rows),[])
        matched = any(next(isomorphisms(rows,earlier),None) is not None for earlier in bucket)
        log(case=label,status='KNOWN_CLASS' if matched else 'NEW_TO_COLLECTION')
        if matched:
            continue
        bucket.append(rows)
        check_candidate(candidate)
        extension_name = label+'-ext36'
        if solve(extension_name,36,*extension(rows,1,4,6),4,6,rows) is True:
            check_candidate(Path(extension_name+'.json'))
            break
