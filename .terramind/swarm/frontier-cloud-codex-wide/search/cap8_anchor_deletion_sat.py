"""Anchor-directed two-slice replacement search for the F_3^8 512-cap.

Unlike the preceding fixed deletion window, this first enumerates anchors in
the two mutable coordinate slices.  It rejects anchors with an immutable
(0-slice, 0-slice) blocker, then chooses a deterministic greedy endpoint
cover of the remaining baseline blockers for a compatible anchor batch.
The selected deletions are intentionally allowed to exceed 12 per slice.
Every surviving point in the full mutable slices is then screened against the
new fixed set, and an exact PB model includes every affine line that touches a
variable point.
"""
import argparse, hashlib, itertools, json, os, platform, time
from pathlib import Path
os.environ.update({"OMP_NUM_THREADS":"1", "OPENBLAS_NUM_THREADS":"1", "MKL_NUM_THREADS":"1"})
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix

POW=[3**k for k in range(7,-1,-1)]
def vec(q): return tuple((q//p)%3 for p in POW)
def ident(v): return sum(a*p for a,p in zip(v,POW))
def third(a,b): return ident(tuple((-x-y)%3 for x,y in zip(vec(a),vec(b))))
def sha(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def main(a):
 out=Path(a.output); out.mkdir(parents=True,exist_ok=True)
 rows=json.load(open(a.input))["points"]; by=[set() for _ in range(3)]
 for r in rows: by[r[0]].add(ident(r))
 assert list(map(len,by))==[192,160,160]
 base=set().union(*by); frozen=by[0]
 # Full baseline blocking pairs for each nonbaseline mutable-slice anchor.
 pairmap={}
 for i,x in enumerate(sorted(base)):
  for y in sorted(base)[i+1:]: pairmap.setdefault(third(x,y),[]).append((x,y))
 anchors=[]; permanently=[]
 for s in (1,2):
  for q in range(3**8):
   if vec(q)[0]!=s or q in base: continue
   bs=pairmap.get(q,[])
   if any(x in frozen and y in frozen for x,y in bs):
    permanently.append(q); continue
   # An anchor is coverable only when no blocker endpoint is frozen twice;
   # remaining endpoints all lie in mutable layers and may be deleted.
   anchors.append((q,bs))
 anchors.sort(key=lambda z:(len(z[1]),z[0]))
 # Deterministically take a compatible seed batch with low blocker burden.
 # Greedy set cover scores endpoints by the number of uncovered anchor-pairs.
 if not a.mixed:
  batch=anchors[:a.anchor_count]
 else:
  chosen=[]; freq={}; quotas={1:(a.anchor_count+1)//2,2:a.anchor_count//2}; used={1:0,2:0}
  while len(chosen)<a.anchor_count:
   want=1 if used[1]<quotas[1] and (used[1]<=used[2] or used[2]>=quotas[2]) else 2
   options=[z for z in anchors if vec(z[0])[0]==want and z not in chosen]
   def score(z):
    pts=[p for x,y in z[1] for p in (x,y) if p not in frozen]
    return (sum(freq.get(p,0) for p in pts),-len(z[1]),-z[0])
   pick=max(options,key=score); chosen.append(pick); used[want]+=1
   for x,y in pick[1]:
    if x not in frozen:freq[x]=freq.get(x,0)+1
    if y not in frozen:freq[y]=freq.get(y,0)+1
  batch=chosen
 uncovered={(q,x,y) for q,bs in batch for x,y in bs}
 delete=set()
 cover_steps=[]
 while uncovered:
  score={}
  # Slice 0 is frozen.  A cover may only remove endpoints in the two
  # mutable slices; the old experiment accidentally omitted this filter.
  for _,x,y in uncovered:
   if x not in frozen: score[x]=score.get(x,0)+1
   if y not in frozen: score[y]=score.get(y,0)+1
  if not score: raise AssertionError("uncoverable anchor has only frozen blockers")
  p=max(score,key=lambda z:(score[z],-z))
  hit=sum(p in (x,y) for _,x,y in uncovered)
  delete.add(p); uncovered={t for t in uncovered if p not in t[1:]}
  cover_steps.append({"point":p,"covers":hit,"remaining":len(uncovered)})
 db=sorted(delete & by[1]); dc=sorted(delete & by[2])
 assert not (delete & frozen)
 fixed=base-delete
 # Full post-deletion fixed-pair screen, retaining all safe nonbaseline points.
 fpair={}; F=sorted(fixed)
 for i,x in enumerate(F):
  for y in F[i+1:]: fpair.setdefault(third(x,y),(x,y))
 ins=[[],[]]; blocked=[[],[]]
 for s in (1,2):
  for q in range(3**8):
   if vec(q)[0]!=s or q in base: continue
   if q in fpair: blocked[s-1].append({"point":q,"pair":list(fpair[q])})
   else: ins[s-1].append(q)
 # Explicitly verify every selected anchor survives the new screen.
 selected_anchors=[q for q,_ in batch]
 survived=[q for q in selected_anchors if q in ins[vec(q)[0]-1]]
 vars_=db+dc+ins[0]+ins[1]; pos={q:i for i,q in enumerate(vars_)}
 universe=sorted(fixed|set(vars_)); lines=set(); clauses=[]
 for i,x in enumerate(universe):
  for y in universe[i+1:]:
   z=third(x,y); line=tuple(sorted((x,y,z)))
   if len(set(line))<3 or line in lines: continue
   lines.add(line); f=sum(q in fixed for q in line); vs=tuple(sorted(pos[q] for q in line if q in pos))
   if vs:
    if f>2: raise AssertionError((line,f))
    clauses.append((vs,2-f))
 clauses=sorted(set(clauses)); target=513-len(fixed)
 cert={"baseline_sha256":hashlib.sha256(open(a.input,"rb").read()).hexdigest(),"anchor_rule":"all nonbaseline points in slices 1 and 2, excluding anchors with an immutable frozen-slice pair; select lowest blocker-count anchors","coverage":"full baseline pair enumeration for all 4054 anchors; full post-deletion screen for all 4054 anchors","anchor_count_requested":a.anchor_count,"cover_algorithm":"deterministic greedy maximum uncovered endpoint incidence restricted to mutable slices, tie: lowest base-3 id","selected_anchors":selected_anchors,"survived_anchors":survived,"permanently_blocked_count":len(permanently),"cover_steps":cover_steps,"delete_a":sorted(delete & by[0]),"delete_b":db,"delete_c":dc,"delete_total":len(delete),"fixed_count":len(fixed),"partition_check":len(fixed)+len(delete)==len(base),"insert_b":ins[0],"insert_c":ins[1],"blocked_b":blocked[0],"blocked_c":blocked[1]}
 (out/"screen.json").write_text(json.dumps(cert,indent=2,sort_keys=True)+"\n")
 (out/"clauses.json").write_text(json.dumps({"variables":vars_,"clauses":[{"variables":list(v),"upper":b} for v,b in clauses],"target":target},indent=2,sort_keys=True)+"\n")
 # Controls: direct baseline validity, planted baseline in encoded clauses, and
 # an exhaustive 8-variable direct-vs-encoding window without cardinality.
 def direct(S): return all(third(x,y) not in S for x,y in itertools.combinations(S,2))
 planted=np.array([int(q in base) for q in vars_])
 plant=all(sum(planted[i] for i in v)<=b for v,b in clauses)
 small=list(range(min(8,len(vars_)))); mismatch=0
 for mask in range(1<<len(small)):
  S=fixed|{vars_[small[i]] for i in range(len(small)) if mask>>i&1}
  enc=all(sum(((mask>>small.index(i))&1) if i in small else 0 for i in v)<=b for v,b in clauses)
  mismatch+=direct(S)!=enc
 control={"baseline_valid":direct(base),"baseline_size":len(base),"planted_baseline_satisfies_clauses":plant,"small_assignments":1<<len(small),"small_mismatches":mismatch}
 (out/"control.json").write_text(json.dumps(control,indent=2,sort_keys=True)+"\n")
 status="UNSAT"; elapsed=0; witness=[]; backend="skipped: target exceeds available variables"
 with open(out/"raw.jsonl","w") as log:
  log.write(json.dumps({"event":"start","variables":len(vars_),"clauses":len(clauses),"target":target,"deadline_seconds":a.seconds,"host":platform.node()})+"\n")
  if len(vars_)>=target:
   data=[]; rr=[]; ub=[]
   for vs,b in clauses:
    data.extend((len(rr),i,1) for i in vs); rr.append(len(rr)); ub.append(b)
   # simpler dense sparse construction sized for this bounded experiment
   A=np.zeros((len(clauses)+1,len(vars_)))
   for r,(vs,b) in enumerate(clauses): A[r,list(vs)]=1
   A[-1,:]=-1; ub.append(-target)
   start=time.monotonic(); res=milp(c=np.zeros(len(vars_)),integrality=np.ones(len(vars_)),bounds=Bounds(np.zeros(len(vars_)),np.ones(len(vars_))),constraints=LinearConstraint(csr_matrix(A),-np.inf*np.ones(len(ub)),np.array(ub)),options={"time_limit":a.seconds,"presolve":True,"mip_rel_gap":0}); elapsed=time.monotonic()-start
   status={0:"SAT",1:"TIMEOUT",2:"UNSAT"}.get(int(res.status),"OTHER"); backend="scipy.optimize.milp/HiGHS"
   if res.x is not None: witness=[vars_[i] for i,x in enumerate(res.x) if x>.5]
  log.write(json.dumps({"event":"finish","classification":status,"elapsed_seconds":elapsed,"selected":len(witness)})+"\n")
 result={"classification":status,"elapsed_seconds":elapsed,"counts":{"baseline":len(base),"fixed":len(fixed),"delete_a":len(delete & by[0]),"delete_b":len(db),"delete_c":len(dc),"delete_total":len(delete),"insert_b":len(ins[0]),"insert_c":len(ins[1]),"variables":len(vars_),"clauses":len(clauses),"target_selected":target,"target_total":len(fixed)+target},"backend":backend,"hashes":{"screen":hashlib.sha256((out/"screen.json").read_bytes()).hexdigest(),"clauses":sha(clauses)},"resume_cursor":{"anchor_count":a.anchor_count,"next":"increase anchor_count or choose next lexicographic anchor batch; preserve frozen slice 0"}}
 (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 if status=="SAT": (out/"candidate.json").write_text(json.dumps({"points":[list(vec(q)) for q in sorted(fixed|set(witness))]},indent=2)+"\n")
 print(json.dumps(result,sort_keys=True))
if __name__=="__main__":
 p=argparse.ArgumentParser(); p.add_argument("--input",required=True);p.add_argument("--output",required=True);p.add_argument("--anchor-count",type=int,default=1);p.add_argument("--seconds",type=float,default=1740);p.add_argument("--mixed",action="store_true");main(p.parse_args())
