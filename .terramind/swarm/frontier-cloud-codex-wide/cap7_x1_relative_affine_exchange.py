#!/usr/bin/env python3
"""New x1-layer affine pool and witness-directed cap exchanges.

This deliberately differs from the earlier x0-layer catalog: x1 is held as
the hyperplane label and each remaining six-coordinate tail receives an
independent affine map.  Candidate exchanges retain the CF-236 cap except
for one endpoint from every blocker pair of an added *new* pool point.
All acceptance tests use the exact F_3 line equation.  This is a bounded
heuristic search; exhaustion below is never an exclusion certificate.
"""
import argparse, hashlib, itertools, json, os, random, sys, time
from pathlib import Path
from cap7_hittingset_search import cap236, blockers, third, valid
from cap7_affine_pool_pb import rebuild_pool

I=((1,0,0,0,0,0),(0,1,0,0,0,0),(0,0,1,0,0,0),(0,0,0,1,0,0),(0,0,0,0,1,0),(0,0,0,0,0,1))
# Maps are relative to tail coordinates (x0,x2,x3,x4,x5,x6), and none of the
# nonidentity labels appeared in the prior x0 ledger.
MAPS=(
 ('id',I,(0,0,0,0,0,0)),
 ('shear02_shift5',((1,0,1,0,0,0),(0,1,0,0,0,0),(0,0,1,0,0,0),(0,0,0,1,0,0),(0,0,0,0,1,0),(0,0,0,0,0,1)),(0,0,0,0,0,1)),
 ('swap03_diag4',((0,0,0,1,0,0),(0,1,0,0,0,0),(0,0,1,0,0,0),(1,0,0,0,0,0),(0,0,0,0,2,0),(0,0,0,0,0,1)),(0,1,0,0,0,0)),
 ('shear51_shift2',((1,0,0,0,0,0),(0,1,0,0,0,0),(0,0,1,0,0,0),(0,0,0,1,0,0),(0,1,0,0,1,0),(0,0,0,0,0,1)),(0,0,2,0,0,0)),
)

def tail(p): return (p[0],p[2],p[3],p[4],p[5],p[6])
def untail(x, y): return (y[0],x,y[1],y[2],y[3],y[4],y[5])
def affine(q,m,t): return tuple((sum(m[i][j]*q[j] for j in range(6))+t[i])%3 for i in range(6))
def image(layer,s): return tuple(sorted(untail(p[1],affine(tail(p),s[1],s[2])) for p in layer))
def h(obj): return hashlib.sha256(json.dumps(obj,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def compatible(p,chosen):
    ss=set(chosen); return all(third(p,q) not in ss for q in chosen)

def atomic_json(path, value):
    """Persist only a complete JSON checkpoint, never a torn cursor."""
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    os.replace(tmp,path)

def main():
 p=argparse.ArgumentParser(); p.add_argument('--seconds',type=float,default=1150); p.add_argument('--per-point',type=int,default=64); p.add_argument('--out',required=True); p.add_argument('--start-rank',type=int,default=0); p.add_argument('--start-mask',type=int,default=0); a=p.parse_args()
 start=time.time(); dead=time.monotonic()+a.seconds
 base=tuple(cap236()); bset=set(base); assert valid(base)
 layers={x:tuple(q for q in base if q[1]==x) for x in range(3)}
 imgs={(x,k):image(layers[x],s) for x in range(3) for k,s in enumerate(MAPS)}
 pool=set(base)
 # Different maps on the two nonzero layers; x1=0 remains fixed as an anchor.
 pairs=[(i,j) for i in range(1,len(MAPS)) for j in range(1,len(MAPS)) if i!=j]
 domains=[]
 for i,j in pairs:
   d=set(layers[0])|set(imgs[1,i])|set(imgs[2,j]); new=sorted(d-bset)
   domains.append({'maps':[MAPS[i][0],MAPS[j][0]],'pool':d,'new':new})
   pool |= d
 new=sorted(pool-bset)
 old_base,old_pool,*_ = rebuild_pool()
 old_set=set(old_pool)
 # positive exchange control: deleting then restoring a baseline point works.
 removed=base[0]; assert valid(tuple(q for q in base if q!=removed)+(removed,))
 result={'algorithm':'x1 relative-affine pool with exact blocker-hit exchange and greedy extension',
  'baseline_size':236,'baseline_sha256_canonical_json':h({'points':[list(x) for x in base]}),
  'split_coordinate':1,'slice_sizes':{str(x):len(layers[x]) for x in range(3)},
  'maps':[x[0] for x in MAPS],'pair_maps':[[MAPS[i][0],MAPS[j][0]] for i,j in pairs],
  'aggregate_pool_size':len(pool),'prior_pool_size':len(old_set),
  'intersection_prior_pool':len(pool & old_set),'points_outside_prior_pool':len(pool-old_set),
  'new_points_vs_baseline':len(new),'new_pool_sha256':h({'points':[list(x) for x in sorted(pool)]}),
  'positive_exchange_control':{'removed_then_restored':list(removed),'size':236,'valid':True},
  'baseline_valid':True,'domains':[{'maps':d['maps'],'pool_size':len(d['pool']),'new_points':len(d['new']),'fingerprint':h({'maps':d['maps'],'points':[list(x) for x in sorted(d['pool'])]})} for d in domains],
  'start_cursor':{'new_point_rank':a.start_rank,'mask':a.start_mask},'points_considered':0,'exchange_masks':0,'heuristic_misses':0,'timeouts':0,'proved_exclusions':0,'best_size':236,'records':[],'cursor':None}
 # Global new candidates ranked by fewest necessary blocker pairs then lexicographic.
 ranked=sorted(new,key=lambda x:(len(blockers(base,x)),x))
 for ci,x in enumerate(ranked):
   if ci<a.start_rank: continue
   result['points_considered']+=1
   if time.monotonic()>=dead: result['timeouts']+=1; result['cursor']={'new_point_rank':ci,'state':'before-point'}; break
   ps=blockers(base,x); total=1<<len(ps); limit=min(total,a.per_point)
   # Every examined mask exactly hits each disjoint blocker pair; if total >
   # limit, the remaining masks are explicitly unvisited rather than excluded.
   first_mask=a.start_mask if ci==a.start_rank else 0
   for mask in range(first_mask,limit):
    if time.monotonic()>=dead: result['timeouts']+=1; result['cursor']={'new_point_rank':ci,'mask':mask,'state':'exchange'}; break
    delete={pair[(mask>>z)&1] for z,pair in enumerate(ps)}
    chosen=[q for n,q in enumerate(base) if n not in delete]+[x]
    # New-pool candidates first, deterministically shuffled only within score ties.
    rest=[q for q in ranked if q!=x]
    random.Random(2100001+ci*131+mask).shuffle(rest)
    rest.sort(key=lambda q:len(blockers(tuple(chosen),q)))
    for q in rest:
      if compatible(q,chosen): chosen.append(q)
    assert valid(tuple(chosen)); result['exchange_masks']+=1
    if len(chosen)>result['best_size']:
      result['best_size']=len(chosen); result['records'].append({'point':list(x),'blocker_pairs':len(ps),'mask':mask,'size':len(chosen),'points':[list(q) for q in sorted(chosen)]})
    if len(chosen)<237: result['heuristic_misses']+=1
    # A completed mask is durable before the next one begins.
    result['cursor']={'new_point_rank':ci,'mask':mask+1,'state':'exchange'} if mask+1<limit else {'new_point_rank':ci+1,'state':'before-point'}
    result['elapsed_seconds']=time.time()-start
    atomic_json(Path(a.out),result)
   if result['timeouts']: break
 result['elapsed_seconds']=time.time()-start
 result['cursor']=result['cursor'] or {'new_point_rank':len(ranked),'state':'done'}
 atomic_json(Path(a.out),result)
 print(json.dumps({k:result[k] for k in ('aggregate_pool_size','new_points_vs_baseline','points_considered','exchange_masks','heuristic_misses','timeouts','proved_exclusions','best_size','cursor','elapsed_seconds')},sort_keys=True))
if __name__=='__main__': main()
