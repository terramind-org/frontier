"""Witness-directed, restricted neighborhoods for the audited mixed F_3^8 pool.

The 264 fixed points and the 813 optional points are reconstructed from the
mixed-pool screen.  Each case starts from the 248 selected baseline optionals,
chooses outside anchors deterministically, deletes a greedy cover of their
baseline blocker pairs, and freezes every other incumbent assignment.  Only
the freed endpoints and related outside alternatives remain variable.

This is deliberately a *neighborhood* experiment: UNSAT says nothing about
the full 813-variable pool.  The JSON ledger fingerprints frozen assignments
so reruns cannot silently repeat a neighborhood.
"""
import argparse, hashlib, itertools, json, os, time
from pathlib import Path
os.environ.update({"OMP_NUM_THREADS":"1","OPENBLAS_NUM_THREADS":"1","MKL_NUM_THREADS":"1"})
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix

P=[3**k for k in range(7,-1,-1)]
def vec(q): return tuple((q//p)%3 for p in P)
def ident(v): return sum(x*p for x,p in zip(v,P))
def third(a,b): return ident(tuple((-x-y)%3 for x,y in zip(vec(a),vec(b))))
def digest(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def direct(s): return all(third(a,b) not in s for a,b in itertools.combinations(sorted(s),2))

def line_constraints(fixed, variables):
 pos={q:i for i,q in enumerate(variables)}; universe=sorted(fixed|set(variables)); seen=set(); out=[]
 for i,x in enumerate(universe):
  for y in universe[i+1:]:
   L=tuple(sorted((x,y,third(x,y))))
   if len(set(L))<3 or L in seen: continue
   seen.add(L); f=sum(q in fixed for q in L); vs=tuple(sorted(pos[q] for q in L if q in pos))
   if vs:
    assert f<=2, (L,f)
    out.append((vs,2-f))
 return sorted(set(out))

def solve(variables, clauses, target, seconds):
 if len(variables)<target: return "UNSAT",[],0.0,"cardinality"
 A=np.zeros((len(clauses)+1,len(variables))); upper=[]
 for r,(vs,k) in enumerate(clauses): A[r,list(vs)]=1; upper.append(k)
 A[-1,:]=-1; upper.append(-target)
 started=time.monotonic()
 r=milp(c=np.zeros(len(variables)),integrality=np.ones(len(variables)),bounds=Bounds(np.zeros(len(variables)),np.ones(len(variables))),constraints=LinearConstraint(csr_matrix(A),-np.inf*np.ones(len(upper)),np.array(upper)),options={"time_limit":seconds,"presolve":True,"mip_rel_gap":0})
 elapsed=time.monotonic()-started
 status={0:"SAT",1:"TIMEOUT",2:"UNSAT"}.get(int(r.status),"OTHER")
 chosen=[] if r.x is None else [variables[i] for i,x in enumerate(r.x) if x>.5]
 return status,chosen,elapsed,"scipy.optimize.milp/HiGHS"

def main(a):
 out=Path(a.output); out.mkdir(parents=True,exist_ok=True)
 fixture=json.load(open(a.input)); screen=json.load(open(a.screen)); rows=fixture['points']
 by=[set() for _ in range(3)]
 for r in rows: by[r[0]].add(ident(r))
 base=set().union(*by); deleted={x['point'] for x in screen['cover_steps']}; fixed=base-deleted
 selected=set(deleted); outside=set(screen['insert_b']+screen['insert_c']); assert len(base)==512 and [len(x) for x in by]==[192,160,160]
 assert len(fixed)==264 and len(selected)==248 and len(outside)==565 and not(deleted&by[0])
 assert direct(base)
 # Complete baseline blocker map.  Each outside point is safe against two
 # fixed points by construction, but may have fixed/selected or selected/selected blockers.
 pairs={}
 for i,x in enumerate(sorted(base)):
  for y in sorted(base)[i+1:]: pairs.setdefault(third(x,y),[]).append((x,y))
 anchors=sorted(outside,key=lambda q:(len(pairs.get(q,[])),-sum(p in selected for xy in pairs.get(q,[]) for p in xy),q))
 # Deterministic anchor groups.  The two rules trade low burden for endpoint overlap.
 groups=[]
 # Score each deterministic seed by the alternatives exposed per deleted
 # incumbent.  The score deliberately uses the completed restricted boundary,
 # rather than just raw anchor blocker counts, so larger groups are selected
 # for useful shared covers rather than for a superficially small cover.
 for seed in range(a.seed_start,a.seed_start+a.seed_count):
  ranked=sorted(anchors,key=lambda q:(len(pairs.get(q,[]))-sum((seed+p)%11==0 for xy in pairs.get(q,[]) for p in xy), (q*1103515245+seed)%3**8))
  # Force a different deterministic starting anchor for each seed before
  # rewarding common endpoints; otherwise all seeds collapse to the same
  # high-overlap cover and the ledger has nothing new to test.
  group=[ranked[(seed*17)%min(128,len(ranked))]]; frequency={}
  for xy in pairs.get(group[0],[]):
   for p in xy:
    if p in selected: frequency[p]=frequency.get(p,0)+1
  while len(group)<a.anchors:
   q=max((z for z in ranked if z not in group),key=lambda z:(sum(frequency.get(p,0) for xy in pairs.get(z,[]) for p in xy if p in selected),-len(pairs.get(z,[])),-((z*1664525+seed*1013904223)%(3**8))))
   group.append(q)
   for xy in pairs.get(q,[]):
    for p in xy:
     if p in selected: frequency[p]=frequency.get(p,0)+1
  groups.append((seed,group))
 # Earlier versions iterated their fixed seed list in order.  Reorder this
 # run's deterministic candidates by the actual boundary yield, with seed as
 # a stable tie breaker.  We still execute every generated case unless a
 # frozen assignment is a duplicate.
 def boundary_yield(group):
  uncovered={(q,x,y) for q in group for x,y in pairs.get(q,[]) if x in selected or y in selected}
  delete=set()
  while uncovered:
   score={}
   for _,x,y in uncovered:
    for p in (x,y):
     if p in selected: score[p]=score.get(p,0)+1
   if not score: return (-1,0,0)
   p=max(score,key=lambda z:(score[z],-z)); delete.add(p)
   uncovered={t for t in uncovered if p not in t[1:]}
  frozen=base-delete; eligible=[]
  for q in outside:
   blockers=pairs.get(q,[])
   if not any(x in frozen and y in frozen for x,y in blockers) and (q in group or any(x in delete or y in delete for x,y in blockers)):
    eligible.append(q)
  return (len(eligible)/max(1,len(delete)),len(eligible),len(delete))
 # Computing a completed boundary scans the full blocker relation.  Cache it
 # before sorting so screening a seed is not accidentally repeated three
 # times, which would make the resume cursor needlessly expensive.
 group_yields={seed:boundary_yield(group) for seed,group in groups}
 groups=sorted(groups,key=lambda sg:(-group_yields[sg[0]][0],-group_yields[sg[0]][1],group_yields[sg[0]][2],sg[0]))
 ledger=[]; seen=set(); best=512
 prior=set()
 for prior_path in a.prior_ledger:
  prior.update(x.get('fingerprint') for x in json.load(open(prior_path)).get('cases',[]) if x.get('fingerprint'))
 for case,(seed,anchor_group) in enumerate(groups):
  uncovered={(q,x,y) for q in anchor_group for x,y in pairs.get(q,[]) if x in selected or y in selected}
  delete=set()
  while uncovered:
   score={}
   for _,x,y in uncovered:
    for p in (x,y):
     if p in selected: score[p]=score.get(p,0)+1
   assert score, "anchor blocked by immutable pair"
   p=max(score,key=lambda z:(score[z],-z)); delete.add(p)
   uncovered={t for t in uncovered if p not in t[1:]}
  frozen=base-delete
  # An alternative is eligible if it has no all-frozen blocker and shares a
  # released endpoint with the anchor cover.  Anchors are retained explicitly.
  eligible=[]
  for q in sorted(outside):
   blockers=pairs.get(q,[])
   if any(x in frozen and y in frozen for x,y in blockers): continue
   if q in anchor_group or any(x in delete or y in delete for x,y in blockers): eligible.append(q)
  # The continuation is deliberately selective: expanding a larger anchor
  # group is worthwhile only when its completed boundary has a strictly
  # better alternative/deletion ratio than the recorded 60/125 benchmark.
  # Keep screened-but-rejected groups in the ledger, rather than silently
  # dropping them, so the cursor and search coverage remain reproducible.
  yield_num, yield_den = len(eligible), len(delete)
  yield_passes = yield_num * a.min_yield_den > a.min_yield_num * yield_den
  if not yield_passes:
   ledger.append({"case":case,"seed":seed,"anchors":anchor_group,"anchor_count":len(anchor_group),"delete_count":len(delete),"eligible_alternatives":len(eligible),"yield_numerator":yield_num,"yield_denominator":yield_den,"yield_benchmark":{"numerator":a.min_yield_num,"denominator":a.min_yield_den},"classification":"YIELD_PRUNED","reason":"eligible/deletion does not strictly exceed benchmark"})
   continue
  variables=sorted(delete)+sorted(set(eligible)); clauses=line_constraints(frozen,variables); target=len(delete)+1
  fingerprint=digest({"frozen":sorted(frozen),"variables":variables,"target":target})
  if fingerprint in prior:
   ledger.append({"case":case,"seed":seed,"anchors":anchor_group,"anchor_count":len(anchor_group),"delete_count":len(delete),"eligible_alternatives":len(eligible),"variables":len(variables),"clauses":len(clauses),"target":target,"frozen":len(frozen),"fingerprint":fingerprint,"classification":"DUPLICATE_PRIOR","duplicate_of":"prior-ledger"})
   continue
  if fingerprint in seen:
   ledger.append({"case":case,"seed":seed,"anchors":anchor_group,"anchor_count":len(anchor_group),"delete_count":len(delete),"eligible_alternatives":len(eligible),"variables":len(variables),"clauses":len(clauses),"target":target,"frozen":len(frozen),"fingerprint":fingerprint,"classification":"DUPLICATE_RUN","duplicate_of":"same-run"})
   continue
  seen.add(fingerprint)
  planted=set(delete); planted_ok=all(sum(variables[i] in planted for i in vs)<=k for vs,k in clauses)
  # Exhaustive direct-vs-clause control on the first min(8,n) variables.
  small=min(8,len(variables)); mismatch=0
  for mask in range(1<<small):
   got=frozen|{variables[i] for i in range(small) if mask>>i&1}
   encoded=all(sum((mask>>i)&1 for i in vs if i<small)<=k for vs,k in clauses)
   mismatch += direct(got)!=encoded
  if len(variables)<target:
   status,witness,elapsed,backend="CARDINALITY_PRUNED",[],0.0,"none"
  else:
   status,witness,elapsed,backend=solve(variables,clauses,target,a.seconds)
  candidate=frozen|set(witness)
  valid=(status=="SAT" and len(candidate)>=513 and direct(candidate))
  if valid:
   best=max(best,len(candidate)); (out/f"candidate-case-{case}.json").write_text(json.dumps({"points":[list(vec(q)) for q in sorted(candidate)]},indent=2)+"\n")
  ledger.append({"case":case,"seed":seed,"anchors":anchor_group,"anchor_count":len(anchor_group),"delete_count":len(delete),"eligible_alternatives":len(eligible),"yield_numerator":yield_num,"yield_denominator":yield_den,"yield_benchmark":{"numerator":a.min_yield_num,"denominator":a.min_yield_den},"variables":len(variables),"clauses":len(clauses),"target":target,"frozen":len(frozen),"fingerprint":fingerprint,"planted_ok":planted_ok,"small_assignments":1<<small,"small_mismatches":mismatch,"classification":status,"elapsed_seconds":elapsed,"backend":backend,"selected":len(witness),"candidate_size":len(candidate) if status=="SAT" else None,"direct_candidate_valid":valid})
 # A concrete positive-gain control for the scanner: replacing 0 by the two
 # other points on its coordinate line increases size 1 -> 2 and is valid.
 toy_old={0}; toy_new={P[0],2*P[0]}; toy={"old_size":1,"new_size":2,"old_valid":direct(toy_old),"new_valid":direct(toy_new),"gain":1}
 assert toy['old_valid'] and toy['new_valid'] and toy['gain']==1
 counts={s:sum(x['classification']==s for x in ledger) for s in ['YIELD_PRUNED','DUPLICATE_PRIOR','DUPLICATE_RUN','CARDINALITY_PRUNED','SAT','UNSAT','TIMEOUT']}
 manifest={"fixture_sha256":hashlib.sha256(Path(a.input).read_bytes()).hexdigest(),"screen_sha256":hashlib.sha256(Path(a.screen).read_bytes()).hexdigest(),"scope":{"fixed":264,"optional":813,"planted_selected":248,"target_optional":249,"target_total":513},"method":"deterministic witness-directed restricted neighborhoods; all assignments outside each fingerprint are frozen to incumbent","anchors_per_case":a.anchors,"seed_start":a.seed_start,"seed_count":a.seed_count,"case_seconds":a.seconds,"strict_yield_benchmark":{"numerator":a.min_yield_num,"denominator":a.min_yield_den,"comparison":"eligible * denominator > numerator * deletions"},"prior_fingerprint_count":len(prior),"baseline_direct_valid":direct(base),"planted_direct_valid":direct(fixed|selected),"toy_positive_gain":toy,"best_verified_size":best,"counts":counts,"cases":ledger,"resume":{"next_seed":a.seed_start+a.seed_count,"next":"continue deterministic seeds with larger groups only if the completed boundary strictly beats the retained yield benchmark; never infer full-pool UNSAT from a restricted case"}}
 (out/'ledger.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 (out/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256((out/n).read_bytes()).hexdigest()}  {n}\n' for n in ['ledger.json']))
 print(json.dumps({"best":best,"cases":len(ledger),"counts":counts},sort_keys=True))
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('--input',required=True); p.add_argument('--screen',required=True); p.add_argument('--output',required=True); p.add_argument('--anchors',type=int,default=4); p.add_argument('--seconds',type=float,default=65); p.add_argument('--seed-start',type=int,default=17); p.add_argument('--seed-count',type=int,default=6); p.add_argument('--min-yield-num',type=int,default=0); p.add_argument('--min-yield-den',type=int,default=1); p.add_argument('--prior-ledger',action='append',default=[]); main(p.parse_args())
