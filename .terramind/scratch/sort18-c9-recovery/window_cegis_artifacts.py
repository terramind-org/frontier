#!/usr/bin/env python3
"""Fixed-prefix/fixed-suffix one-gate-shorter sorting-network window CEGIS.

The candidate window has all 153 legal comparator pairs available at every
position.  SAT sees counterexamples incrementally; every SAT model is checked
against all 2^18 binary inputs before it is accepted.
"""
import hashlib, itertools, json, random, sys, time
import numpy as np
from pysat.solvers import Cadical153

N = 18
PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]

def apply(a, gates):
    a = a.copy()
    for i, j in gates:
        lo = a[:, i] & a[:, j]
        a[:, j] = a[:, i] | a[:, j]
        a[:, i] = lo
    return a

def bad(a): return np.flatnonzero((a[:, :-1] > a[:, 1:]).any(axis=1))

def inputs():
    q = np.arange(1 << N, dtype=np.uint32)
    return ((q[:, None] >> np.arange(N, dtype=np.uint32)) & 1).astype(np.uint8)

def scalar_prefix(v, gates):
    """Independent scalar evaluator used to audit the vectorised state set."""
    v = list(map(int, v))
    for i, j in gates:
        v[i], v[j] = v[i] & v[j], v[i] | v[j]
    return tuple(v)

def state_digest(states):
    return hashlib.sha256(b''.join(sorted(bytes(v) for v in states))).hexdigest()

def main(path, start, width, seconds, seed):
    doc = json.load(open(path)); gates = [tuple(x) for x in doc.get('nw', doc['comparators'])]
    pre, suf, target = gates[:start], gates[start + width:], width - 1
    allx = inputs()
    # Do not trust a capped/sampled CEGIS seed.  Enumerate the reachable
    # prefix image twice, by unrelated scalar and vectorised implementations,
    # and fail closed if they disagree.
    reachable = np.unique(apply(allx, pre), axis=0)
    independent = {scalar_prefix(v, pre) for v in allx}
    vectorised = {tuple(map(int, v)) for v in reachable}
    if vectorised != independent:
        raise RuntimeError('reachable-prefix enumeration mismatch; refusing to encode a partial query')
    baseline_failures = len(bad(apply(allx, gates)))
    print(json.dumps({'event':'baseline', 'gates':len(gates), 'all_inputs':len(allx), 'failures':baseline_failures,
                      'start':start, 'width':width, 'target':target, 'prefix_vectors':len(reachable),
                      'independent_prefix_vectors':len(independent), 'prefix_state_sha256':state_digest(reachable),
                      'seed':seed}), flush=True)
    # The initial query must cover every reachable prefix state.  This makes
    # an UNSAT result a complete fixed-window exclusion, not a CEGIS sample.
    solver, nvar, clauses = Cadical153(with_proof=True), 0, []
    def add(clause):
        clause = list(clause)
        clauses.append(clause)
        solver.add_clause(clause)
    def new():
        nonlocal nvar; nvar += 1; return nvar
    choose = [[new() for _ in PAIRS] for _ in range(target)]
    for row in choose:
        add(row)
        for x, y in itertools.combinations(row, 2): add([-x, -y])
    untouched = [[new() for _ in range(N)] for _ in range(target)]
    for t in range(target):
        for wire in range(N):
            touch = [choose[t][k] for k, (i,j) in enumerate(PAIRS) if wire == i or wire == j]
            add([untouched[t][wire]] + touch)
            for c in touch: add([-untouched[t][wire], -c])
    # Canonicalise only repeated adjacent gates; this excludes no shorter network.
    for t in range(target - 1):
        for k in range(len(PAIRS)): add([-choose[t][k], -choose[t+1][k]])
    seen = set()
    def constrain(v):
        key = v.tobytes()
        if key in seen: return
        seen.add(key); cur = [new() for _ in range(N)]
        for i, bit in enumerate(v): add([cur[i] if bit else -cur[i]])
        for t in range(target):
            nxt = [new() for _ in range(N)]
            for w in range(N):
                add([-untouched[t][w], -cur[w], nxt[w]])
                add([-untouched[t][w], cur[w], -nxt[w]])
            for c, (i,j) in zip(choose[t], PAIRS):
                xi,xj,yi,yj = cur[i],cur[j],nxt[i],nxt[j]
                add([-c,xi,-yi]); add([-c,xj,-yi]); add([-c,-xi,-xj,yi])
                add([-c,-xi,yj]); add([-c,-xj,yj]); add([-c,xi,xj,-yj])
            cur = nxt
        for i,j in suf:
            lo, hi = new(), new(); a,b = cur[i],cur[j]
            add([-lo,a]); add([-lo,b]); add([lo,-a,-b])
            add([-hi,a,b]); add([hi,-a]); add([hi,-b]); cur[i],cur[j] = lo,hi
        for w in range(N-1): add([-cur[w],cur[w+1]])
    rng=random.Random(seed); order=list(range(len(reachable))); rng.shuffle(order)
    for i in order: constrain(reachable[i])
    encoded = {tuple(map(int, np.frombuffer(key, dtype=np.uint8))) for key in seen}
    if encoded != independent:
        raise RuntimeError('encoded state set differs from independently enumerated prefix image')
    print(json.dumps({'event':'state-set-audit', 'encoded_prefix_vectors':len(encoded),
                      'independent_prefix_vectors':len(independent),
                      'encoded_state_sha256':state_digest(encoded),
                      'independent_state_sha256':state_digest(independent), 'status':'equal'}), flush=True)
    cnf = 'query_s%d_w%d_t%d.cnf' % (start, width, target)
    with open(cnf, 'w') as out:
        out.write('p cnf %d %d\n' % (nvar, len(clauses)))
        for clause in clauses: out.write('%s 0\n' % ' '.join(map(str, clause)))
    print(json.dumps({'event':'cnf', 'path':cnf, 'variables':nvar, 'clauses':len(clauses)}), flush=True)
    deadline=time.monotonic()+seconds; rounds=0
    while time.monotonic() < deadline:
        rounds += 1
        if not solver.solve():
            proof = 'query_s%d_w%d_t%d.drat' % (start, width, target)
            with open(proof, 'w') as out: out.write('\n'.join(solver.get_proof()) + '\n')
            print(json.dumps({'event':'result','result':'UNSAT','rounds':rounds,'vectors':len(seen),'variables':nvar,'proof':proof,'seconds':round(seconds-(deadline-time.monotonic()),3)})); return
        pos={x for x in solver.get_model() if x>0}
        middle=[p for row in choose for p,c in zip(PAIRS,row) if c in pos]
        failures=bad(apply(reachable,middle+suf))
        if not len(failures):
            full=pre+middle+suf; out='candidate_s%d_w%d.json'%(start,width)
            json.dump({'comparators':[list(x) for x in full]},open(out,'w'))
            print(json.dumps({'event':'result','result':'SAT','rounds':rounds,'vectors':len(seen),'candidate':out,'gates':len(full)})); return
        picks=list(failures); rng.shuffle(picks)
        for i in picks[:30]: constrain(reachable[i])
        print(json.dumps({'event':'cex','round':rounds,'vectors':len(seen),'all_prefix_failures':len(failures)}),flush=True)
    print(json.dumps({'event':'result','result':'TIMEOUT','rounds':rounds,'vectors':len(seen),'variables':nvar,'seconds':seconds}),flush=True)

if __name__ == '__main__': main(sys.argv[1], *map(int, sys.argv[2:]))
