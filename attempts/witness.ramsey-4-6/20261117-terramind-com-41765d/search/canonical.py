"""Add degree bounds and canonical cross-block rotations to cyclic orbit SAT."""
import argparse
from datetime import datetime
from pathlib import Path
from itertools import accumulate
from collections import defaultdict
from time import monotonic

from pysat.card import CardEnc, EncType

from campaign import OUT, PYTHON, launch
from orbits import clique_masks, cyclic_action, to_clause
from search import log, solve


BLOCK_SIZES = {
    '17-control': (17,), '24-control': (6,)*4,
    '36-b2': (18,18), '36-b3': (12,)*3, '36-b4': (9,)*4, '36-b6': (6,)*6,
    '37-b2': (36,1), '37-b3': (18,18,1), '37-b4': (12,12,12,1), '37-b6': (8,8,8,8,4,1),
}


def lex_leader(first, other, top, clauses):
    """Constrain first <= other as binary words with colour 0 ordered first."""
    prefix = None
    for a,b in zip(first,other):
        if a == b:
            continue
        active = [] if prefix is None else [-prefix]
        clauses.append([*active,-a,b])
        top += 1
        equal = top
        clauses.extend([
            [*active,a,b,equal], [*active,-a,-b,equal], [-equal,-a,b], [-equal,a,-b],
        ])
        if prefix is not None:
            clauses.append([-equal,prefix])
        prefix = equal
    return top


def generate(blocks, sizes, maximums, order_blocks=False):
    n = sum(blocks)
    mapping, reps = cyclic_action(blocks)
    masks = clique_masks(n,sizes,mapping,reps)
    clauses = [to_clause(mask,sign) for group,sign in zip(masks,(1,-1)) for mask in sorted(group)]
    top = max(mapping.values())
    for v in reps:
        incident = [mapping[tuple(sorted((v,u)))] for u in range(n) if u!=v]
        for sign, maximum in zip((-1,1),maximums):
            card = CardEnc.atmost(lits=[sign*x for x in incident],bound=maximum,
                                top_id=top,encoding=EncType.seqcounter)
            clauses.extend(card.clauses)
            top = card.nv
    for start, size in zip(accumulate(blocks),blocks[1:]):
        sequence = list(dict.fromkeys(mapping[0,start+j] for j in range(size)))
        for offset in range(1,len(sequence)):
            top = lex_leader(sequence,sequence[offset:]+sequence[:offset],top,clauses)
    if order_blocks:
        by_size = defaultdict(list)
        for start,size in zip(accumulate((0,*blocks)),blocks):
            word = tuple(mapping[start,start+j] for j in range(1,size//2+1))
            by_size[size].append(word)
        for words in by_size.values():
            for first,other in zip(words,words[1:]):
                top = lex_leader(first,other,top,clauses)
    return mapping,clauses,top


def run(label,conflicts,order_blocks):
    blocks = BLOCK_SIZES[label]
    n = sum(blocks)
    sizes, maxima = ((4,4),(8,8)) if n==17 else ((4,5),(13,17)) if n==24 else ((4,6),(17,24))
    start = monotonic()
    mapping,clauses,cnf_variables = generate(blocks,sizes,maxima,order_blocks)
    log(case=label,phase='encode-canonical',blocks=blocks,fixed_color_max_degrees=maxima,
        variables=max(mapping.values()),cnf_variables=cnf_variables,clauses=len(clauses), ordered_blocks=order_blocks,
        seconds=round(monotonic()-start,4))
    prefix = 'ordered-' if order_blocks else 'canonical-'
    return solve(prefix+label,n,mapping,clauses,*sizes,budget=conflicts)


def batch(deadline, conflicts, order_blocks):
    prefix = 'ordered-' if order_blocks else 'canonical-'
    controls = ('24-control',) if order_blocks else ('17-control','24-control')
    targets = ('36-b6',) if order_blocks else ('36-b3','36-b4','36-b6','37-b4','37-b6')
    mode = ['--ordered'] if order_blocks else []
    for label in controls:
        name = prefix+label
        launch(deadline,name,[PYTHON,'canonical.py',label,'--conflicts','100000',*mode],90)
        if not Path(name+'.json').exists():
            raise RuntimeError(f'{label} canonical SAT failed calibration')
    for label in targets:
        name = prefix+label
        if not launch(deadline,name,[PYTHON,'canonical.py',label,'--conflicts',str(conflicts),*mode],400 if order_blocks else 260):
            return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('label',choices=(*BLOCK_SIZES,'batch'))
    parser.add_argument('--conflicts',type=int,default=500000)
    parser.add_argument('--deadline',type=datetime.fromisoformat)
    parser.add_argument('--ordered',action='store_true')
    args = parser.parse_args()
    if args.label == 'batch':
        if args.deadline is None:
            parser.error('batch requires --deadline')
        OUT.mkdir(exist_ok=True)
        batch(args.deadline,args.conflicts,args.ordered)
    else:
        run(args.label,args.conflicts,args.ordered)
