#!/usr/bin/env python3
"""Exact 11-deletion exchanges at the 10-pair CF-236 anchors.

The completed c4 run covered the 10-deletion (one endpoint per pair) masks.
This script covers exactly the disjoint new 11-deletion masks: (A) one endpoint
from every pair plus one vertex outside those pairs, and (B) both endpoints of
one pair plus one endpoint from each other pair.  It never emits a 10-deletion
mask.  A case is only called pruned when fewer than eleven individually
compatible extra points remain; node limits are logged as cutoffs.
"""
import argparse, hashlib, json, platform, sys, time
from pathlib import Path

from cap7_hittingset_search import cap236, blockers, dec, third, valid

N = 7

def choose_masks(pair_count):
    width = 1 << pair_count
    return [[sum(1 << m for m in range(width) if ((m >> i) & 1) == bit)
             for bit in (0, 1)] for i in range(pair_count)]

def and_all(values, full):
    out = full
    for v in values:
        out &= v
    return out

def bit_indices(bits):
    while bits:
        low = bits & -bits
        yield low.bit_length() - 1
        bits ^= low

def graph_and_decide(forced, candidate_bits, outside, retained, need, limit):
    candidates = [outside[i] for i in bit_indices(candidate_bits)]
    blocked = set(forced) | set(candidates) | set(retained)
    graph = [set() for _ in candidates]
    for i, x in enumerate(candidates):
        for j in range(i + 1, len(candidates)):
            if third(x, candidates[j]) in blocked:
                graph[i].add(j); graph[j].add(i)
    nodes, cutoff, answer = 0, False, None
    def rec(avail, chosen):
        nonlocal nodes, cutoff, answer
        if answer is not None or cutoff: return
        nodes += 1
        if nodes > limit:
            cutoff = True; return
        if len(chosen) >= need:
            answer = chosen[:]; return
        if len(chosen) + len(avail) < need: return
        v = max(avail, key=lambda z: (len(graph[z] & avail), -z))
        rec(avail - {v} - graph[v], chosen + [v])
        rec(avail - {v}, chosen)
    rec(set(range(len(candidates))), [])
    return ([candidates[i] for i in answer] if answer is not None else None), nodes, cutoff

def direct_candidates(base, outside, anchor, deleted, all_blockers):
    index = {p:i for i,p in enumerate(base)}
    ans = []
    for q in outside:
        if q == anchor: continue
        if not all(set(edge) & deleted for edge in all_blockers[q]): continue
        r = index.get(third(anchor, q))
        if r is None or r in deleted: ans.append(q)
    return ans

def add_to(bucket, allowed, qbit):
    for m in bit_indices(allowed): bucket[m] |= qbit

def case_a_buckets(base, outside, anchor, pairs, all_blockers):
    """Candidate bitsets for one-per-pair plus extra vertex d.

    Return base[m] (works for every d) and needs[m][d] (works only if d is
    deleted).  The representation is exact because blocker pairs are disjoint:
    after the pair choices, at most one remaining blocker may be hit by d.
    """
    width, full = 1 << len(pairs), (1 << (1 << len(pairs))) - 1
    loc = {v:(i,b) for i,pair in enumerate(pairs) for b,v in enumerate(pair)}
    choice = choose_masks(len(pairs))
    extras = tuple(i for i in range(len(base)) if i not in loc)
    extra_set = set(extras)
    index = {p:i for i,p in enumerate(base)}
    base_bucket = [0] * width
    need_bucket = [dict() for _ in range(width)]
    def add_need(d, allowed, qbit):
        if d not in extra_set: return
        for m in bit_indices(allowed):
            need_bucket[m][d] = need_bucket[m].get(d, 0) | qbit
    for qi, q in enumerate(outside):
        if q == anchor: continue
        qbit = 1 << qi
        edges = all_blockers[q]
        hits = []
        for edge in edges:
            hm = 0
            for v in edge:
                if v in loc:
                    i,b = loc[v]; hm |= choice[i][b]
            hits.append(hm)
        r = index.get(third(anchor, q))
        line_required = None
        line_mask = full
        if r is not None:
            if r in loc:
                i,b = loc[r]; line_mask = choice[i][b]
            elif r in extra_set:
                line_required = r
            else:
                continue
        # No blocker left for the extra deletion.
        allowed = and_all(hits, full) & line_mask
        if allowed:
            if line_required is None: add_to(base_bucket, allowed, qbit)
            else: add_need(line_required, allowed, qbit)
        # Exactly edge k remains; d must be one of its vertices.
        for k, edge in enumerate(edges):
            allowed = line_mask & (full ^ hits[k])
            for j, hm in enumerate(hits):
                if j != k: allowed &= hm
            if not allowed: continue
            for d in edge:
                if line_required is None or line_required == d:
                    add_need(d, allowed, qbit)
    return extras, base_bucket, need_bucket

def case_b_buckets(base, outside, anchor, pairs, all_blockers):
    """Candidate bitsets for each doubled pair j and ten-bit choice mask."""
    width, full = 1 << len(pairs), (1 << (1 << len(pairs))) - 1
    loc = {v:(i,b) for i,pair in enumerate(pairs) for b,v in enumerate(pair)}
    choice = choose_masks(len(pairs)); index = {p:i for i,p in enumerate(base)}
    out = [[0] * width for _ in pairs]
    for qi, q in enumerate(outside):
        if q == anchor: continue
        qbit = 1 << qi
        edge_hits = []
        for edge in all_blockers[q]:
            hm, touch = 0, set()
            for v in edge:
                if v in loc:
                    i,b = loc[v]; hm |= choice[i][b]; touch.add(i)
            edge_hits.append((hm, touch))
        r = index.get(third(anchor, q))
        for j in range(len(pairs)):
            allowed = full
            for hm, touch in edge_hits:
                allowed &= full if j in touch else hm
            if r is not None:
                if r not in loc: allowed = 0
                else:
                    i,b = loc[r]
                    allowed &= full if i == j else choice[i][b]
            # one representative choice for doubled j prevents duplicates
            allowed &= choice[j][0]
            if allowed: add_to(out[j], allowed, qbit)
    return out

def run_control(base, outside, anchor, pairs, all_blockers):
    extras, aa, an = case_a_buckets(base, outside, anchor, pairs, all_blockers)
    bb = case_b_buckets(base, outside, anchor, pairs, all_blockers)
    checked_a = checked_b = 0
    for m in range(4):
        chosen = {pair[(m >> i) & 1] for i,pair in enumerate(pairs)}
        for d in extras[:4]:
            got = {outside[i] for i in bit_indices(aa[m] | an[m].get(d, 0))}
            assert got == set(direct_candidates(base, outside, anchor, chosen | {d}, all_blockers))
            checked_a += 1
    for j in range(2):
        for raw in range(4):
            m = raw & ~(1 << j)
            deleted = {v for i,pair in enumerate(pairs) for v in (pair if i == j else (pair[(m >> i) & 1],))}
            got = {outside[i] for i in bit_indices(bb[j][m])}
            assert got == set(direct_candidates(base, outside, anchor, deleted, all_blockers))
            checked_b += 1
    # Positive and negative exhaustive control for the decision solver.
    pts = ((0,)*N, (1,0,0,0,0,0,0), (0,1,0,0,0,0,0), (1,1,0,0,0,0,0))
    extension, nodes, cutoff = graph_and_decide((pts[0],), (1 << 3)-1, list(pts[1:]), (), 3, 10000)
    impossible, _, bad_cutoff = graph_and_decide((pts[0],), (1 << 3)-1, list(pts[1:]), (), 4, 10000)
    assert extension is not None and len(extension) == 3 and not cutoff and impossible is None and not bad_cutoff
    return {'a_direct_cases':checked_a, 'b_direct_cases':checked_b, 'solver_positive_nodes':nodes}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=1740)
    ap.add_argument('--node-limit', type=int, default=20000)
    ap.add_argument('--out', required=True)
    ap.add_argument('--start-anchor', type=int, default=0)
    ap.add_argument('--start-kind', choices=('a','b'), default='a')
    ap.add_argument('--start-mask', type=int, default=0)
    ap.add_argument('--start-extra', type=int, default=0)
    ap.add_argument('--start-double', type=int, default=0)
    a = ap.parse_args(); wall, began = time.time(), time.monotonic(); deadline = began + a.seconds
    base = cap236(); assert valid(base)
    canonical = json.dumps({'points':[list(p) for p in base]}, separators=(',',':'))
    universe = tuple(dec(i) for i in range(3**N)); outside = [p for p in universe if p not in set(base)]
    all_blockers = {q:blockers(base,q) for q in outside}
    anchors = [q for q in outside if len(all_blockers[q]) == 10]
    assert len(anchors) == 24
    # A has 2^10 * 216 and B has 10 * 2^9 cases per anchor.
    cases_a, cases_b = (1 << 10) * (len(base)-20), 10 * (1 << 9)
    result = {'artifact_status':'new c6 experiment; baseline recovered from c5/PR 69',
      'algorithm':'exact 10-pair anchors with exactly 11 deletions: A pair-choice plus outside vertex; B one doubled pair',
      'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(wall)), 'seconds_budget':a.seconds,
      'node_limit_per_case':a.node_limit, 'python':sys.version, 'platform':platform.platform(),
      'baseline_size':len(base), 'baseline_sha256_canonical_json':hashlib.sha256(canonical.encode()).hexdigest(),
      'anchors_with_10_pairs':len(anchors), 'cases_a_per_anchor':cases_a, 'cases_b_per_anchor':cases_b,
      'cases_total':len(anchors)*(cases_a+cases_b), 'cases_started':0, 'cases_completed':0,
      'cases_pruned':0, 'cases_cutoff':0, 'candidate_checks':0, 'solver_nodes':0,
      'best_size':236, 'records':[], 'timed_out':False, 'resume':None}
    control = run_control(base, outside, anchors[0], all_blockers[anchors[0]], all_blockers)
    result['control'] = control
    stop = {'anchor_index':len(anchors), 'kind':'done', 'mask':0, 'extra_index':0, 'double_pair':0}
    for ai in range(a.start_anchor, len(anchors)):
        anchor = anchors[ai]; pairs = all_blockers[anchor]
        extras, ab, an = case_a_buckets(base, outside, anchor, pairs, all_blockers)
        bb = case_b_buckets(base, outside, anchor, pairs, all_blockers)
        kind_start = a.start_kind if ai == a.start_anchor else 'a'
        if kind_start == 'a':
            ms = a.start_mask if ai == a.start_anchor else 0
            for m in range(ms, 1 << 10):
                es = a.start_extra if ai == a.start_anchor and m == ms else 0
                selected = {pair[(m >> i) & 1] for i,pair in enumerate(pairs)}
                for ei in range(es, len(extras)):
                    if time.monotonic() >= deadline:
                        result['timed_out']=True; stop={'anchor_index':ai,'kind':'a','mask':m,'extra_index':ei,'double_pair':0}; break
                    d=extras[ei]; bits=ab[m] | an[m].get(d,0); result['cases_started'] += 1
                    if bits.bit_count() < 11:
                        result['cases_pruned'] += 1; result['cases_completed'] += 1; continue
                    deleted = selected | {d}
                    retained=tuple(p for i,p in enumerate(base) if i not in deleted)
                    ext,nodes,cutoff=graph_and_decide((anchor,),bits,outside,retained,11,a.node_limit)
                    result['candidate_checks'] += bits.bit_count(); result['solver_nodes'] += nodes
                    if cutoff: result['cases_cutoff'] += 1
                    else: result['cases_completed'] += 1
                    if ext is not None:
                        trial=retained+(anchor,)+tuple(ext); assert valid(trial) and len(trial)>=237
                        result['records'].append({'anchor':list(anchor),'kind':'a','mask':m,'extra_index':d,'extension':[list(x) for x in ext],'size':len(trial)})
                        result['best_size']=max(result['best_size'],len(trial))
                if result['timed_out']: break
        if result['timed_out']: break
        # B begins only once all A masks are exhaustive for this anchor.
        js = a.start_double if ai == a.start_anchor and a.start_kind == 'b' else 0
        for j in range(js, 10):
            for m in range(1 << 10):
                if m >> j & 1: continue
                if time.monotonic() >= deadline:
                    result['timed_out']=True; stop={'anchor_index':ai,'kind':'b','mask':m,'extra_index':0,'double_pair':j}; break
                deleted={v for i,pair in enumerate(pairs) for v in (pair if i==j else (pair[(m>>i)&1],))}
                bits=bb[j][m]; result['cases_started'] += 1
                if bits.bit_count() < 11:
                    result['cases_pruned'] += 1; result['cases_completed'] += 1; continue
                retained=tuple(p for i,p in enumerate(base) if i not in deleted)
                ext,nodes,cutoff=graph_and_decide((anchor,),bits,outside,retained,11,a.node_limit)
                result['candidate_checks'] += bits.bit_count(); result['solver_nodes'] += nodes
                if cutoff: result['cases_cutoff'] += 1
                else: result['cases_completed'] += 1
                if ext is not None:
                    trial=retained+(anchor,)+tuple(ext); assert valid(trial) and len(trial)>=237
                    result['records'].append({'anchor':list(anchor),'kind':'b','mask':m,'double_pair':j,'extension':[list(x) for x in ext],'size':len(trial)})
                    result['best_size']=max(result['best_size'],len(trial))
            if result['timed_out']: break
        if result['timed_out']: break
    result['resume']=stop; result['elapsed_seconds']=time.time()-wall
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('cases_started','cases_completed','cases_pruned','cases_cutoff','candidate_checks','solver_nodes','best_size','timed_out','resume','elapsed_seconds')},sort_keys=True))

if __name__ == '__main__': main()
