#!/usr/bin/env python3
"""Deterministic exact minimal-hitting-set exchanges for the CF 236-cap.

For an outside point x, every unordered pair {a,b} in the cap with a+b=-x
is a blocker: one endpoint must be deleted before x can be inserted.  The
pairs are disjoint, so selecting one endpoint per pair enumerates every
minimum-cardinality hitting set exactly once.  After each deletion set this
script computes all points compatible with the retained cap, then performs an
exact branch-and-bound independent-set search on that residual compatibility
graph (with x forced in) to seek a net gain.
"""
import argparse, hashlib, itertools, json, platform, sys, time
from pathlib import Path

N, POW = 7, [3**i for i in range(8)]

def enc(p): return sum(x * POW[N-1-i] for i, x in enumerate(p))
def dec(v):
    out = [0]*N
    for i in range(N-1, -1, -1): out[i], v = v % 3, v // 3
    return tuple(out)
def third(a,b): return tuple((-x-y) % 3 for x,y in zip(a,b))

def cap236():
    # The 2-(6,3,2) design from Bierbrauer--Edel / Holden, with ±1 represented
    # by 1/2.  Ordering is lexicographic after construction to make the source
    # independent of Python set iteration.
    blocks = ((0,1,2),(0,1,3),(0,2,4),(0,3,5),(0,4,5),
              (1,2,5),(1,3,4),(1,4,5),(2,3,4),(2,3,5))
    def hill(use_complements):
        pts = set()
        for block in blocks:
            support = tuple(i for i in range(6) if i not in block) if use_complements else block
            for signs in itertools.product((1,2), repeat=3):
                p=[0]*6
                for i,x in zip(support,signs): p[i]=x
                pts.add(tuple(p))
        for signs in itertools.product((1,2), repeat=6):
            # product is +1 for an even number of -1/2 entries.
            if sum(x == 2 for x in signs) % 2 == 0: pts.add(tuple(signs))
        assert len(pts)==112
        return pts
    h, hp = hill(False), hill(True)
    pts = {(1,)+v for v in h} | {(2,)+v for v in hp}
    for i in range(6):
        for s in (1,2):
            v=[0]*6; v[i]=s; pts.add((0,)+tuple(v))
    assert len(pts)==236
    return tuple(sorted(pts))

def valid(points):
    s=set(points)
    return all(third(a,b) not in s for i,a in enumerate(points) for b in points[i+1:])

def blockers(base, x):
    ids={p:i for i,p in enumerate(base)}
    seen=set(); ans=[]
    for i,a in enumerate(base):
        b=third(x,a) # x+a+b=0
        j=ids.get(b)
        if j is not None and j != i:
            key=(min(i,j),max(i,j))
            if key not in seen: seen.add(key); ans.append(key)
    return tuple(sorted(ans))

def compatible_with_retained(p, retained):
    # A p is admissible iff it completes no pair within retained.
    rs=set(retained)
    for i,a in enumerate(retained):
        for b in retained[i+1:]:
            if third(a,b)==p: return False
    return True

def forbidden_by_retained(retained):
    return {third(a,b) for i,a in enumerate(retained) for b in retained[i+1:]}

def max_extension(forced, candidates, retained, deadline):
    # Exact cap-subset search: candidates already work with retained.  Build
    # conflict graph, including conflicts with forced points, and solve maximum
    # independent set by include/exclude recursion.  Return a witness subset.
    forced=set(forced)
    candidates=[p for p in candidates if all(third(p,q) not in forced for q in forced)]
    candidates=[p for p in candidates if p not in forced]
    candidate_set=set(candidates)
    conflicts=[set() for _ in candidates]
    for i,a in enumerate(candidates):
        for j in range(i+1,len(candidates)):
            b=candidates[j]
            # a,b conflict if third(a,b) is forced or another candidate.
            if third(a,b) in forced or third(a,b) in candidate_set:
                conflicts[i].add(j); conflicts[j].add(i)
    best=[]; timed=False
    def rec(avail, chosen):
        nonlocal best,timed
        if time.monotonic()>deadline: timed=True; return
        if len(chosen)+len(avail)<=len(best): return
        if not avail:
            if len(chosen)>len(best): best=chosen[:]
            return
        v=max(avail,key=lambda z:len(conflicts[z]&avail))
        rec(avail-{v}-conflicts[v],chosen+[v])
        rec(avail-{v},chosen)
    rec(set(range(len(candidates))),[])
    return forced | {candidates[i] for i in best}, timed, len(candidates)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--seconds',type=float,default=1740); ap.add_argument('--out',required=True); ap.add_argument('--baseline-out')
    a=ap.parse_args(); started=time.time(); deadline=time.monotonic()+a.seconds
    base=cap236(); base_json=json.dumps({'points':[list(p) for p in base]},separators=(',',':'))
    base_hash=hashlib.sha256(base_json.encode()).hexdigest()
    assert valid(base)
    if a.baseline_out: Path(a.baseline_out).write_text(base_json+'\n')
    universe=tuple(dec(i) for i in range(3**N)); bset=set(base)
    outside=[p for p in universe if p not in bset]
    groups={}
    for p in outside: groups.setdefault(len(blockers(base,p)),[]).append(p)
    minpairs=min(groups); minima=groups[minpairs]
    result={'algorithm':'exact-minimum-hitting-set exchange, then exact independent-set extension',
      'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(started)), 'seconds_budget':a.seconds,
      'python':sys.version, 'platform':platform.platform(), 'baseline_size':len(base),
      'baseline_sha256_canonical_json':base_hash, 'baseline_valid':True,
      'blocker_pair_histogram':{str(k):len(v) for k,v in sorted(groups.items())},
      'minimum_blocker_pairs':minpairs,'minimum_points':[list(p) for p in minima],
      'cases_total':len(minima)*(2**minpairs),'cases_started':0,'cases_completed':0,
      'timed_out':False,'best_size':236,'best':None,'records':[]}
    for p in minima:
      pairs=blockers(base,p)
      for mask in range(1<<len(pairs)):
        if time.monotonic()>deadline: result['timed_out']=True; break
        deleted={pair[(mask>>i)&1] for i,pair in enumerate(pairs)}
        retained=tuple(q for i,q in enumerate(base) if i not in deleted)
        result['cases_started']+=1
        forbidden=forbidden_by_retained(retained)
        cands=[q for q in outside if q != p and q not in forbidden]
        ext,timed,ncand=max_extension((p,),cands,retained,deadline)
        if timed: result['timed_out']=True; break
        trial=retained+tuple(ext)
        assert valid(trial)
        result['cases_completed']+=1
        if len(trial)>result['best_size']:
            result['best_size']=len(trial); result['best']=[list(q) for q in sorted(trial)]
        if len(trial)>=237:
            result['records'].append({'outside_point':list(p),'mask':mask,'deleted_indices':sorted(deleted),'candidate_count':ncand,'extension':[list(q) for q in sorted(ext)],'size':len(trial)})
      if result['timed_out']: break
    result['elapsed_seconds']=time.time()-started
    result['resume']={'outside_point_index':minima.index(p) if result['timed_out'] else len(minima),'next_mask':mask+1 if result['timed_out'] else 0}
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('baseline_sha256_canonical_json','blocker_pair_histogram','minimum_blocker_pairs','cases_completed','cases_total','timed_out','best_size','elapsed_seconds','resume')},sort_keys=True))
if __name__=='__main__': main()
