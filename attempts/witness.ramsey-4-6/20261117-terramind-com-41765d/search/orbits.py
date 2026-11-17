"""Generate edge orbits for cyclic actions and the groups of order 36, and test SAT."""
import argparse
from itertools import combinations, product
from pathlib import Path
from time import monotonic

from search import edges, solve, log


def cyclic_action(sizes):
    generator = []
    offset = 0
    for size in sizes:
        generator.extend(offset + (i+1) % size for i in range(size))
        offset += size
    return edge_orbits([generator])


def edge_orbits(generators):
    n = len(generators[0])
    vertex_reps = {}
    seen = set()
    for v in range(n):
        if v in seen:
            continue
        seen.add(v)
        queue = [v]
        for a in queue:
            for g in generators:
                b = g[a]
                if b not in seen:
                    seen.add(b)
                    queue.append(b)
        vertex_reps[v] = len(queue)
    mapping = {}
    count = 0
    for edge in edges(n):
        if edge in mapping:
            continue
        count += 1
        mapping[edge] = count
        queue = [edge]
        for a, b in queue:
            for g in generators:
                other = tuple(sorted((g[a], g[b])))
                if other not in mapping:
                    mapping[other] = count
                    queue.append(other)
    return mapping, vertex_reps


I = (1,0,0,1)
NEG = (2,0,0,2)
REFLECTION = (1,0,0,2)
OTHER_REFLECTION = (2,0,0,1)
ROTATION = (0,2,1,0)
ORDER3 = (0,1,1,1)


def matmul(a, b, modulus):
    return tuple(sum(a[2*r+k]*b[2*k+c] for k in range(2)) % modulus for r in range(2) for c in range(2))


def action_group(kernel, quotient, generators):
    """Kernel and quotient are direct products of cyclic groups. Return left translations."""
    elements = list(product(*(range(length) for length in (*kernel, *quotient))))
    index = {element: i for i, element in enumerate(elements)}
    ks = len(kernel)

    def act(q, y):
        for exponent, generator in zip(q, generators):
            for _ in range(exponent):
                if ks == 1:
                    y = ((generator*y[0]) % kernel[0],)
                else:
                    a,b,c,d = generator
                    y = ((a*y[0]+b*y[1]) % kernel[0], (c*y[0]+d*y[1]) % kernel[1])
        return y

    # Check the action relations for these generators before computing translations.
    basis = [tuple(int(i == j) for i in range(ks)) for j in range(ks)]
    for j, length in enumerate(quotient):
        power = tuple(length if i == j else 0 for i in range(len(quotient)))
        assert all(act(power, v) == v for v in basis)
    if ks == len(quotient) == 2:
        assert matmul(*generators, kernel[0]) == matmul(*generators[::-1], kernel[0])

    def translate(g):
        x, q = g[:ks], g[ks:]
        translated = []
        for h in elements:
            y, r = h[:ks], h[ks:]
            z = tuple((a+b)%m for a,b,m in zip(x,act(q,y),kernel))
            s = tuple((a+b)%m for a,b,m in zip(q,r,quotient))
            translated.append(index[z+s])
        assert len(set(translated)) == len(elements)
        return translated

    translations = [translate(g) for g in elements]
    # Check closure against the unique translation sending the identity to the product.
    for g in translations:
        for h in translations:
            k = translations[g[h[0]]]
            assert all(k[i] == g[h[i]] for i in range(len(elements)))
    left_generators = [
        translations[index[tuple(int(i == j) for i in range(len(kernel)+len(quotient)))]]
        for j in range(len(kernel)+len(quotient))
    ]
    mapping, reps = edge_orbits(left_generators)
    assert reps == {0:len(elements)}
    return mapping, reps


def cayley36():
    for tail, quotient in [('c4',(4,)), ('v4',(2,2))]:
        for label, first in [('trivial', 1), ('invert', 8)]:
            # The cyclic trivial product is covered by the Z_36 enumeration.
            if tail == 'c4' and label == 'trivial':
                continue
            yield f'g36-c9-{tail}-{label}', action_group(
                (9,), quotient, (first,) if tail == 'c4' else (first,1))
    for label, matrix in [('trivial',I),('reflect',REFLECTION),('invert',NEG),('rotate',ROTATION)]:
        yield f'g36-v9-c4-{label}', action_group((3,3), (4,), (matrix,))
    for label, matrices in [
        ('trivial',(I,I)), ('trivial-reflect',(REFLECTION,I)), ('trivial-invert',(NEG,I)),
        ('two-chars',(REFLECTION,OTHER_REFLECTION)),
    ]:
        yield f'g36-v9-v4-{label}', action_group((3,3), (2,2), matrices)
    yield 'g36-v4-c9', action_group((2,2), (9,), (ORDER3,))
    yield 'g36-v4-v9', action_group((2,2), (3,3), (ORDER3,I))


def write_map(path, mapping, reps):
    values = [mapping[e]-1 for e in sorted(mapping)]
    vertices = ''.join(f'{v} {size}\n' for v,size in sorted(reps.items()))
    Path(path).write_text(f'{1+max(values)} {len(reps)}\n' + vertices + ' '.join(map(str, values)) + '\n')


def clique_masks(n, sizes, mapping, reps):
    masks_by_color = []
    for size in sizes:
        masks = set()
        for anchor in sorted(reps):
            available = sorted(set(range(n)) - {anchor})
            for others in combinations(available, size-1):
                mask = 0
                vertices = sorted((*others,anchor))
                for edge in combinations(vertices, 2):
                    mask |= 1 << (mapping[edge]-1)
                masks.add(mask)
        masks_by_color.append(masks)
    return masks_by_color


def to_clause(mask, sign):
    clause = []
    while mask:
        bit = mask & -mask
        mask ^= bit
        clause.append(sign*bit.bit_length())
    return clause


def solve_orbits(name, n, sizes, mapping, reps, budget):
    start = monotonic()
    masks = clique_masks(n, sizes, mapping, reps)
    clauses = [to_clause(mask, sign) for group, sign in zip(masks, (1,-1)) for mask in sorted(group)]
    log(case=name, phase='encode', variables=max(mapping.values()), clauses=len(clauses),
        seconds=round(monotonic()-start, 4))
    solve(name+'-sat', n, mapping, clauses, *sizes, budget=budget)


def families():
    for n, cases in [
        (17, {'circle':(17,),'b2':(16,1)}),
        (24, {'circle':(24,), 'b2':(12,12), 'b3':(8,8,8), 'b4':(6,)*4, 'b6':(4,)*6}),
        (36, {'circle':(36,), 'b2':(18,18), 'b3':(12,)*3, 'b4':(9,)*4, 'b6':(6,)*6}),
        (37, {'circle':(37,), 'b2':(36,1), 'b3':(18,18,1), 'b4':(12,12,12,1), 'b6':(8,8,8,8,4,1)}),
    ]:
        for label, orbit_sizes in cases.items():
            yield f'n{n}-{label}', n, cyclic_action(orbit_sizes)
    for label, spec in cayley36():
        yield label, 36, spec


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['maps','sat'])
    parser.add_argument('--names', nargs='*')
    parser.add_argument('--conflicts', type=int, default=300000)
    args = parser.parse_args()
    for label, n, (mapping,reps) in families():
        if args.names and label not in args.names:
            continue
        if args.action == 'maps':
            write_map(label+'.orbits', mapping,reps)
            log(case=label,n=n,variables=max(mapping.values()),vertex_orbits=len(reps))
        else:
            sizes = (4,4) if n==17 else (4,5) if n==24 else (4,6)
            solve_orbits(label,n,sizes,mapping,reps,args.conflicts)
