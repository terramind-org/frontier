"""Find automorphisms by paired colour refinement, and seed symmetry-preserving extensions."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
from math import lcm
from pathlib import Path

from campaign import OUT, launch, result
from orbits import edge_orbits, write_map
from search import as_rows, edges, log, save


def isomorphisms(rows, other):
    n = len(rows)
    assert len(other) == n
    left_neighbors, right_neighbors = [
        [[i for i,edge in enumerate(row) if edge] for row in matrix]
        for matrix in (rows,other)
    ]

    def refine(left,right):
        while True:
            def signatures(colors,neighbors):
                return [
                    (colors[i], tuple(sorted(Counter(colors[j] for j in adjacent).items())))
                    for i,adjacent in enumerate(neighbors)
                ]
            x,y = signatures(left,left_neighbors),signatures(right,right_neighbors)
            if Counter(x)!=Counter(y):
                return None
            labels = {entry:i for i,entry in enumerate(sorted(set(x)))}
            lnext = [labels[entry] for entry in x]
            rnext = [labels[entry] for entry in y]
            if len(labels)==len(set(left)):
                return lnext,rnext
            left,right = lnext,rnext

    def visit(left,right):
        refined = refine(left,right)
        if refined is None:
            return
        left,right = refined
        lpart, rpart = defaultdict(list),defaultdict(list)
        for i in range(n):
            lpart[left[i]].append(i)
            rpart[right[i]].append(i)
        cell = min((c for c in lpart if len(lpart[c])>1),key=lambda c:len(lpart[c]),default=None)
        if cell is None:
            perm = [rpart[color][0] for color in left]
            assert all(rows[i][j]==other[perm[i]][perm[j]] for i,j in edges(n))
            yield perm
        else:
            for target in rpart[cell]:
                lnext,rnext = left[:],right[:]
                lnext[lpart[cell][0]] = rnext[target] = n
                yield from visit(lnext,rnext)

    yield from visit([0]*n,[0]*n)


def automorphisms(rows):
    yield from isomorphisms(rows,rows)


def write_seed(rows, generators, name, source, group_order):
    extended = [perm+[len(rows)] for perm in generators]
    mapping,reps = edge_orbits(extended)
    write_map(name+'.orbits',mapping,reps)
    restricted = [r+[0] for r in rows]+[[0]*(len(rows)+1)]
    save(name+'.json',restricted)
    log(case=name,input=str(source),order_of_aut_group=group_order,
        vertex_orbits=sorted(reps.values()),edge_orbits=max(mapping.values()))


def seed(path,prefix):
    rows = as_rows(path)
    permutations = list(automorphisms(rows))
    for i,perm in enumerate(permutations):
        if perm!=list(range(len(rows))):
            write_seed(rows,[perm],f'{prefix}-{i:02}',path,len(permutations))


def order(perm):
    _, reps = edge_orbits([perm])
    return lcm(*reps.values())


def batch(deadline):
    entries = []
    for input_path in sorted(Path('.').glob('catalogue-input-*.json')):
        rows = as_rows(input_path)
        group = list(automorphisms(rows))
        log(case='catalogue-auto',input=str(input_path),order=len(group))
        if len(group)>1:
            perm = max(group,key=order)
            number = int(input_path.stem.rsplit('-',1)[-1])
            entries.append((-order(perm),number,input_path,rows,perm,len(group)))
    for _,number,path,rows,perm,size in sorted(entries)[:8]:
        name = f'aut-catalogue-{number:02}'
        initial = str(OUT/(name+'-seed'))
        write_seed(rows,[perm],initial,path,size)
        if not launch(deadline,name,[
            './ramsey','anneal','36','4','6',str(4650000+number),'2200000','8',
            '1','0.02',initial+'.json',str(OUT/name),initial+'.orbits','0.8','0.055'
        ],180):
            return
        if result(OUT/(name+'.log'))==0:
            return


def full_group(deadline, number):
    path = Path(f'catalogue-input-{number:02}.json')
    rows = as_rows(path)
    group = list(automorphisms(rows))
    assert len(group)>1
    name = f'aut-full-catalogue-{number:02}'
    initial = str(OUT/(name+'-seed'))
    write_seed(rows,group,initial,path,len(group))
    launch(deadline,name,[
        './ramsey','anneal','36','4','6',str(4651000+number),'3000000','8',
        '1','0.02',initial+'.json',str(OUT/name),initial+'.orbits','0.8','0.055'
    ],180)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deadline',type=datetime.fromisoformat)
    parser.add_argument('--full-group',type=int)
    args = parser.parse_args()
    if args.deadline and args.full_group is not None:
        full_group(args.deadline,args.full_group)
    elif args.deadline:
        batch(args.deadline)
    else:
        seed(Path('baseline.json'),'aut-base')
