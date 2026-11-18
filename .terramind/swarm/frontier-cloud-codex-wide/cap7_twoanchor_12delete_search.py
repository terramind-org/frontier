#!/usr/bin/env python3
"""Joint two-anchor, twelve-deletion exchanges around recovered CF-236.

The selected domain is every lexicographically ordered pair of the 24
outside points having the smallest observed individual blocker count (10).
For each pair the union of blockers is formed, the line through both anchors
is forced deleted if it is a retained base point, and exact size-12 hitting
sets are enumerated if the resulting minimum cover is at most 12.  A final
exact extension search asks for eleven additions beyond the two anchors.
"""
import argparse, hashlib, itertools, json, platform, sys, time
from pathlib import Path

from cap7_hittingset_search import cap236, blockers, dec, third, valid

N = 7

def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low

def cover_minimum(edges, forced, cap=12):
    """All minimum vertex covers up to cap, using a deterministic branch-and-bound.

    The union of two blocker matchings has degree at most two, but this generic
    routine is deliberately small and independently fixture-tested below.
    """
    remaining = tuple(e for e in edges if not (set(e) & forced))
    best = cap + 1; solutions = []
    def rec(todo, chosen):
        nonlocal best, solutions
        if len(chosen) > best or len(chosen) > cap: return
        uncovered = next((e for e in todo if not (set(e) & chosen)), None)
        if uncovered is None:
            size = len(chosen)
            if size < best: best, solutions = size, [frozenset(chosen)]
            elif size == best: solutions.append(frozenset(chosen))
            return
        x, y = uncovered
        rec(todo, chosen | {x})
        rec(todo, chosen | {y})
    rec(remaining, set(forced))
    return best, tuple(sorted(set(solutions), key=lambda s: tuple(sorted(s))))

def degree_two_cover_lower_bound(edges, forced):
    """Exact minimum cover size for a max-degree-two graph, by components."""
    adj = {}
    for x, y in edges:
        if x in forced or y in forced: continue
        adj.setdefault(x, set()).add(y); adj.setdefault(y, set()).add(x)
    seen, answer = set(), len(forced)
    for root in adj:
        if root in seen: continue
        stack=[root]; seen.add(root); vertices=0
        while stack:
            x=stack.pop(); vertices += 1
            for y in adj[x]:
                if y not in seen: seen.add(y); stack.append(y)
        # Every component is an alternating path or even cycle (union of two
        # matchings); its maximum matching, hence minimum cover, is floor(v/2).
        answer += vertices // 2
    return answer

def compatible(base, outside, a, z, deleted, all_blockers):
    answer = []
    for q in outside:
        if q == a or q == z: continue
        if any(not (set(edge) & deleted) for edge in all_blockers[q]): continue
        # All three pair-lines with forced anchors must avoid retained base.
        if any(third(q, w) in base and third(q, w) not in deleted for w in (a, z)):
            continue
        answer.append(q)
    return answer

def extend(base, outside, forced, candidates, retained, need, limit):
    occupied = set(forced) | set(candidates) | set(retained)
    graph = {q:set() for q in candidates}
    for i, q in enumerate(candidates):
        for r in candidates[i + 1:]:
            if third(q, r) in occupied:
                graph[q].add(r); graph[r].add(q)
    nodes, cutoff, found = 0, False, None
    def rec(avail, chosen):
        nonlocal nodes, cutoff, found
        if found is not None or cutoff: return
        nodes += 1
        if nodes > limit: cutoff = True; return
        if len(chosen) == need: found = tuple(chosen); return
        if len(chosen) + len(avail) < need: return
        q = max(avail, key=lambda x: (len(graph[x] & avail), x))
        rec(avail - {q} - graph[q], chosen + [q])
        rec(avail - {q}, chosen)
    rec(set(candidates), [])
    return found, nodes, cutoff

def controls():
    # Brute-force all covers of a four-edge path plus forced endpoint.
    edges = ((0,1),(1,2),(2,3),(3,4)); forced = {0}
    got, covers = cover_minimum(edges, forced, 4)
    brute = [frozenset(forced | set(s)) for r in range(5) for s in itertools.combinations(range(5), r)
             if all(set(e) & (forced | set(s)) for e in edges)]
    want = min(map(len, brute)); assert got == want and set(covers) == {x for x in brute if len(x) == want}
    assert degree_two_cover_lower_bound(edges, forced) == got
    # A planted three-vertex extension and impossible four-vertex request.
    base = (); outside = [(0,)*N, (1,0,0,0,0,0,0), (0,1,0,0,0,0,0), (1,1,0,0,0,0,0)]
    yes, nodes, cut = extend(base, outside, (outside[0],), outside[1:], (), 3, 10000)
    no, _, cut2 = extend(base, outside, (outside[0],), outside[1:], (), 4, 10000)
    assert yes is not None and len(yes) == 3 and no is None and not cut and not cut2
    return {'cover_fixture_minimum':got, 'cover_fixture_solutions':len(covers), 'extension_positive_nodes':nodes}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--seconds', type=float, default=1740)
    ap.add_argument('--node-limit', type=int, default=20000); ap.add_argument('--out', required=True)
    ap.add_argument('--start-pair', type=int, default=0); args = ap.parse_args()
    began_wall, began = time.time(), time.monotonic(); deadline = began + args.seconds
    base = tuple(cap236()); assert valid(base); base_set=set(base); index={x:i for i,x in enumerate(base)}
    outside = tuple(dec(i) for i in range(3**N) if dec(i) not in base_set)
    all_blockers = {q:tuple(tuple(e) for e in blockers(base,q)) for q in outside}
    eligible = tuple(q for q in outside if len(all_blockers[q]) == 10)
    selected=[]; hist={}; filter_count=0
    for ai,a in enumerate(eligible):
        for z in eligible[ai+1:]:
            union=tuple(sorted({tuple(sorted(e)) for e in all_blockers[a]} | {tuple(sorted(e)) for e in all_blockers[z]}))
            t=third(a,z); forced=frozenset({t}) if t in base_set else frozenset()
            minimum = degree_two_cover_lower_bound(union, forced)
            hist[str(minimum)] = hist.get(str(minimum),0)+1
            if minimum <= 12:
                checked, covers = cover_minimum(union, forced, 12)
                assert checked == minimum
                # Add arbitrary non-cover vertices only when a smaller cover
                # exists; this is intentionally bounded to this case because
                # it is the exact size-12 family, not just its minima.
                if minimum < 12:
                    pool=tuple(x for x in base if x not in covers[0])
                    expanded=[]
                    for cover in covers:
                        expanded.extend(frozenset(cover | set(extra)) for extra in itertools.combinations(tuple(x for x in base if x not in cover),12-minimum))
                    covers=tuple(sorted(set(expanded),key=lambda s:tuple(sorted(s))))
                selected.append((a,z,union,forced,covers))
            else: filter_count += 1
    canonical=json.dumps({'points':[list(p) for p in base]},separators=(',',':'))
    result={'artifact_status':'new c7 experiment; CF-236 recovered from c6/PR 71',
      'algorithm':'all 10-blocker anchor pairs; exact size-12 covers of their union after forced anchor line',
      'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(began_wall)), 'seconds_budget':args.seconds,
      'node_limit_per_case':args.node_limit,'python':sys.version,'platform':platform.platform(),
      'baseline_size':236,'baseline_sha256_canonical_json':hashlib.sha256(canonical.encode()).hexdigest(),
      'outside_points':len(outside),'eligible_anchors':len(eligible),'pair_filter_histogram':hist,
      'pairs_filtered_not_minimum_12':filter_count,'selected_pairs':len(selected),
      'selected_cover_count':sum(len(x[4]) for x in selected),'cases_started':0,'cases_completed':0,'cases_pruned':0,
      'cases_cutoff':0,'candidate_checks':0,'solver_nodes':0,'best_size':236,'records':[],'timed_out':False,'resume':None,
      'controls':controls()}
    stop={'pair_index':len(selected),'cover_index':0,'state':'done'}
    for pi,(a,z,union,forced,covers) in enumerate(selected[args.start_pair:],args.start_pair):
        for ci, deleted in enumerate(covers):
            if time.monotonic() >= deadline:
                result['timed_out']=True; stop={'pair_index':pi,'cover_index':ci,'state':'cover'}; break
            result['cases_started']+=1
            cand=compatible(base_set,outside,a,z,deleted,all_blockers)
            # 224 retained + two anchors requires 11 other additions for 237.
            if len(cand)<11:
                result['cases_pruned']+=1;result['cases_completed']+=1;continue
            retained=tuple(p for p in base if p not in deleted)
            ext,nodes,cut=extend(base,outside,(a,z),cand,retained,11,args.node_limit)
            result['candidate_checks']+=len(cand);result['solver_nodes']+=nodes
            if cut: result['cases_cutoff']+=1
            else: result['cases_completed']+=1
            if ext is not None:
                trial=retained+(a,z)+ext
                assert valid(trial) and len(trial)>=237
                result['records'].append({'pair':[list(a),list(z)],'cover':[list(x) for x in sorted(deleted)],'extension':[list(x) for x in ext],'size':len(trial)})
                result['best_size']=max(result['best_size'],len(trial))
        if result['timed_out']: break
    result['resume']=stop;result['elapsed_seconds']=time.time()-began_wall
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('selected_pairs','selected_cover_count','cases_started','cases_completed','cases_pruned','cases_cutoff','candidate_checks','solver_nodes','best_size','timed_out','resume','elapsed_seconds')},sort_keys=True))
if __name__ == '__main__': main()
