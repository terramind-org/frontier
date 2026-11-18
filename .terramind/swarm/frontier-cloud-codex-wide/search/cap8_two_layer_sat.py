"""Bounded exact two-layer replacement experiment for the F_3^8 512-cap.

The 0-slice (192 points) is frozen.  In each of the other coordinate-0
slices, deterministic pools replace a few baseline points by nearby points.
Every line that meets a variable point is translated to a pseudo-Boolean SAT
clause.  SciPy/HiGHS solves this exact 0/1 feasibility instance; the emitted
JSON contains the clauses and a complete resume cursor for independent replay.
"""
import argparse, hashlib, itertools, json, os, time
os.environ.update({"OMP_NUM_THREADS":"1", "OPENBLAS_NUM_THREADS":"1", "MKL_NUM_THREADS":"1"})
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix

P = 3 ** np.arange(7, -1, -1, dtype=np.int64)
def ident(row): return int(np.asarray(row, dtype=np.int64) @ P)
def vec(i): return np.array([(i // (3 ** k)) % 3 for k in range(7, -1, -1)], dtype=np.int8)
def third(a,b): return ident((-vec(a)-vec(b)) % 3)
def h(obj): return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",",":")).encode()).hexdigest()

def near_pool(base, frozen, slice_id, deletes, inserts):
    """Stable pools: lexicographic baseline deletions and nearest valid inserts."""
    dels = sorted(base)[:deletes]
    fixed = set(frozen) | (set(base)-set(dels))
    candidates=[]
    for q in range(3**8):
        if q in base: continue
        if vec(q)[0] != slice_id: continue
        # Deterministic Hamming-distance neighbourhood of the first deletable seed.
        if sum(vec(q) != vec(dels[0])) > 3: continue
        # Any line with two fixed points makes q impossible, so omit it early.
        bad=False
        fl=sorted(fixed)
        for a_i,a in enumerate(fl):
            for b in fl[a_i+1:]:
                if third(a,b)==q: bad=True; break
            if bad: break
        if not bad: candidates.append(q)
    candidates.sort(key=lambda q:(sum(vec(q)!=vec(dels[0])), q))
    return dels, candidates[:inserts]

def solve(args):
    experiment_started=time.monotonic()
    raw=json.load(open(args.input))["points"]
    by=[set() for _ in range(3)]
    for row in raw: by[row[0]].add(ident(row))
    assert [len(x) for x in by]==[192,160,160]
    frozen_a=set(by[0])
    db, ib=near_pool(by[1], frozen_a, 1, args.deletes, args.inserts)
    dc, ic=near_pool(by[2], frozen_a, 2, args.deletes, args.inserts)
    fixed=frozen_a | (by[1]-set(db)) | (by[2]-set(dc))
    variables=db+dc+ib+ic
    # Baseline deletions have x=1 when retained; inserts x=1 when included.
    baseline_keep=len(fixed)
    # Enumerate all variable-containing affine lines exactly once.
    pos={p:i for i,p in enumerate(variables)}
    clauses={}
    universe=sorted(fixed | set(variables))
    for ai,a in enumerate(universe):
        for b in universe[ai+1:]:
            c=third(a,b)
            if c not in fixed and c not in pos: continue
            line=tuple(sorted((a,b,c)))
            if len(set(line))<3 or line in clauses: continue
            f=sum(x in fixed for x in line)
            vs=tuple(sorted(pos[x] for x in line if x in pos))
            if vs: clauses[line]=(vs, 2-f)
    # Required exact-cap clauses. Negative bound would mean invalid fixed baseline.
    assert all(bound >= 0 for _,bound in clauses.values())
    rows=[]; ub=[]
    for vs,bound in clauses.values():
        row=np.zeros(len(variables)); row[list(vs)]=1; rows.append(row); ub.append(bound)
    # At least 513 points: sum variables >= 513 - frozen-cardinality.
    rows.append(-np.ones(len(variables))); ub.append(-(513-baseline_keep))
    A=csr_matrix(np.vstack(rows))
    started=time.monotonic()
    result=milp(c=np.zeros(len(variables)), integrality=np.ones(len(variables)),
        bounds=Bounds(np.zeros(len(variables)),np.ones(len(variables))),
        constraints=LinearConstraint(A, -np.inf*np.ones(len(ub)), np.array(ub)),
        options={"time_limit":args.seconds, "presolve":True, "mip_rel_gap":0})
    elapsed=time.monotonic()-started
    selected=[]
    if result.x is not None: selected=[variables[i] for i,x in enumerate(result.x) if x>.5]
    points=sorted(fixed | set(selected))
    meta={"kind":"exact-pb-sat", "input_sha256":hashlib.sha256(open(args.input,"rb").read()).hexdigest(),
      "pool":{"delete_b":db,"delete_c":dc,"insert_b":ib,"insert_c":ic,"rule":"lexicographic first deletion seeds; Hamming radius <=3; candidates excluding lines with two fixed points"},
      "counts":{"frozen_a":len(frozen_a),"fixed_total":len(fixed),"variables":len(variables),"clauses":len(clauses),"target":513},
      "status":int(result.status),"message":result.message,"elapsed_seconds":elapsed,
      "classification": {0:"SAT",2:"UNSAT",1:"TIMEOUT"}.get(int(result.status),"OTHER"),
      "objective_value":None if result.x is None else len(points),
      "resume_cursor":{"pool_hash":h([db,dc,ib,ic]),"deadline_seconds":args.seconds,"next_phase":"expand inserts then deletes"},
      "clause_hash":h(sorted((list(k),list(v),b) for k,(v,b) in clauses.items()))}
    json.dump(meta, open(args.output,"w"), indent=2, sort_keys=True)
    if selected: json.dump({"points":[list(map(int,vec(p))) for p in points]},open(args.witness,"w"))
    # Controls: planted baseline assignment and exhaustive 2+2 variable window.
    base=set(by[0])|set(by[1])|set(by[2])
    def valid(S):
        for a,b in itertools.combinations(S,2):
            if third(a,b) in S: return False
        return True
    planted=np.array([1 if v in base else 0 for v in variables])
    control={"baseline_valid":valid(base),"baseline_size":len(base),
      "planted_baseline_satisfies_line_clauses":bool(np.all((A[:-1] @ planted) <= np.array(ub[:-1]))),
      "small_window":"first 2 deletes/inserts per layer", "small_bruteforce_assignments":0,
      "small_bruteforce_feasible":0,"small_clause_feasible":0,"small_clause_mismatches":0}
    small=variables[:2]+variables[len(db):len(db)+2]+variables[len(db)+len(dc):len(db)+len(dc)+2]+variables[-2:]
    # Exhaustive agreement for a small relaxation (no size target).
    for mask in range(1<<len(small)):
        control["small_bruteforce_assignments"]+=1
        S=fixed|{small[i] for i in range(len(small)) if mask>>i&1}
        direct=valid(S)
        if direct: control["small_bruteforce_feasible"]+=1
        selected_idx={pos[x] for x in small if x in S}
        clause_ok=all(sum(i in selected_idx for i in vs)<=bound for vs,bound in clauses.values())
        if clause_ok: control["small_clause_feasible"]+=1
        if direct != clause_ok: control["small_clause_mismatches"]+=1
    json.dump(control,open(args.control,"w"),indent=2,sort_keys=True)
    meta["total_elapsed_seconds"]=time.monotonic()-experiment_started
    json.dump(meta, open(args.output,"w"), indent=2, sort_keys=True)

if __name__=="__main__":
 p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--output",required=True); p.add_argument("--witness",required=True); p.add_argument("--control",required=True); p.add_argument("--seconds",type=float,default=1740); p.add_argument("--deletes",type=int,default=12); p.add_argument("--inserts",type=int,default=24); solve(p.parse_args())
