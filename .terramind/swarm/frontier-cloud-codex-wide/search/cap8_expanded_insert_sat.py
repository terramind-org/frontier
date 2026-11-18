"""Expanded-insertion, bounded two-slice F_3^8 cap experiment.

This is deliberately independent of the preceding HiGHS PB model.  It builds
Boolean variables for the retained deletions and every safe insertion in two
deterministic Hamming balls, translates each relevant affine line to an
at-most-two Boolean clause, and uses a small deterministic DPLL solver with a
native cardinality propagator.  It writes the full screen certificate, CNF-ish
line clauses, control results, progress events and a resume cursor.
"""
import argparse, hashlib, itertools, json, os, sys, time
from pathlib import Path

os.environ.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
P = [3 ** k for k in range(7, -1, -1)]

def vec(q): return tuple((q // (3 ** k)) % 3 for k in range(7, -1, -1))
def ident(v): return sum(x * p for x, p in zip(v, P))
def third(a, b): return ident(tuple((-x-y) % 3 for x, y in zip(vec(a), vec(b))))
def digest(x): return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

class Solver:
    def __init__(self, clauses, n, target, deadline, log):
        self.clauses, self.n, self.target, self.deadline, self.log = clauses, n, target, deadline, log
        self.deg = [0]*n
        for c in clauses:
            for v in c: self.deg[v] += 1
        self.nodes = self.conflicts = self.propagations = 0
        self.last = time.monotonic()

    def propagate(self, a):
        changed = True
        while changed:
            if time.monotonic() >= self.deadline: raise TimeoutError
            changed = False
            ones = sum(x == 1 for x in a); unknown = [i for i,x in enumerate(a) if x < 0]
            if ones + len(unknown) < self.target: return False
            if ones == self.target:
                for i in unknown: a[i] = 0
                self.propagations += len(unknown); changed = True
            elif ones + len(unknown) == self.target:
                for i in unknown: a[i] = 1
                self.propagations += len(unknown); changed = True
            for c in self.clauses:
                t = sum(a[v] == 1 for v in c)
                if t > 2: return False
                if t == 2:
                    for v in c:
                        if a[v] < 0:
                            a[v] = 0; self.propagations += 1; changed = True
        return True

    def run(self, a):
        self.nodes += 1
        if self.nodes % 4096 == 0 and time.monotonic() - self.last > 5:
            self.log({"event":"progress", "nodes":self.nodes, "conflicts":self.conflicts,
                      "propagations":self.propagations, "seconds":time.monotonic()-self.started})
            self.last = time.monotonic()
        b = a[:]
        if not self.propagate(b): self.conflicts += 1; return None
        if all(x >= 0 for x in b): return b
        # Deterministic maximum-degree, index-tiebroken decision. Try 1 first:
        # a 513-point witness needs 25 of these variables selected.
        v = max((i for i,x in enumerate(b) if x < 0), key=lambda i:(self.deg[i], -i))
        for bit in (1, 0):
            b2 = b[:]; b2[v] = bit
            out = self.run(b2)
            if out is not None: return out
        return None

def main(args):
    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    raw = json.load(open(args.input))["points"]
    by = [set() for _ in range(3)]
    for r in raw: by[r[0]].add(ident(r))
    assert [len(x) for x in by] == [192,160,160]
    # Match the saved c6 cursor exactly: 12 lexicographically first deletions.
    db, dc = sorted(by[1])[:12], sorted(by[2])[:12]
    fixed = by[0] | (by[1]-set(db)) | (by[2]-set(dc))
    assert len(fixed) == 488
    fpair = {}
    F = sorted(fixed)
    for i,a in enumerate(F):
        for b in F[i+1:]: fpair.setdefault(third(a,b), (a,b))
    def screen(slice_id, seed):
        candidates=[]; rejected=[]
        for q in range(3**8):
            if q in by[slice_id] or vec(q)[0] != slice_id: continue
            d=sum(x != y for x,y in zip(vec(q),vec(seed)))
            if d > args.radius: continue
            if q in fpair: rejected.append({"point":q,"hamming":d,"blocking_fixed_pair":list(fpair[q])})
            else: candidates.append((d,q))
        candidates.sort(); rejected.sort(key=lambda x:(x["hamming"],x["point"]))
        return [q for _,q in candidates], rejected
    ib, rb = screen(1, db[0]); ic, rc = screen(2, dc[0])
    # The screen is exhaustive over the deterministic balls, not an arbitrary prefix.
    variables = db + dc + ib + ic
    pos = {q:i for i,q in enumerate(variables)}
    universe = sorted(fixed | set(variables))
    lines = set(); clauses=[]
    for ai,a in enumerate(universe):
        for b in universe[ai+1:]:
            c=third(a,b); line=tuple(sorted((a,b,c)))
            if len(set(line)) != 3 or line in lines: continue
            lines.add(line)
            f=sum(q in fixed for q in line)
            vs=tuple(sorted(pos[q] for q in line if q in pos))
            if f + len(vs) >= 3 and vs:
                # screening ensures f never equals 2 for a variable line.
                if f == 2: raise AssertionError((line, f, vs))
                clauses.append(vs)
    clauses=sorted(set(clauses))
    # The Boolean interpretation is at-most-two on every exact variable line.
    target=513-len(fixed)
    line_hash=digest(clauses)
    cert={"rule":"all nonbaseline points in coordinate slice, Hamming distance <= radius from first saved deletion; exclude iff third of a fixed-point pair",
          "radius":args.radius,"fixed_count":len(fixed),"delete_b":db,"delete_c":dc,
          "insert_b":ib,"insert_c":ic,"excluded_b":rb,"excluded_c":rc}
    (out/"screen.json").write_text(json.dumps(cert,indent=2,sort_keys=True)+"\n")
    (out/"clauses.json").write_text(json.dumps({"variables":variables,"at_most_two_clauses":clauses,"target_selected":target},indent=2,sort_keys=True)+"\n")
    with open(out/"raw.jsonl","w") as fp:
        def log(ev): fp.write(json.dumps(ev,sort_keys=True)+"\n"); fp.flush()
        log({"event":"start","variables":len(variables),"clauses":len(clauses),"target":target,
             "pool_hash":digest([db,dc,ib,ic]),"line_hash":line_hash,"deadline_seconds":args.seconds})
        # Positive baseline control: 512 original points satisfy every line clause.
        base=by[0]|by[1]|by[2]
        planted=[1 if q in base else 0 for q in variables]
        planted_ok=all(sum(planted[v] for v in c) <= 2 for c in clauses)
        # Independent direct checker + exact 8-variable exhaustive clause comparison.
        small=list(range(min(8,len(variables))))
        sm={"assignments":0,"direct_feasible":0,"clause_feasible":0,"mismatches":0}
        # This is a direct verifier, but factors out the already verified fixed
        # set so the 256-assignment control does not repeatedly scan 119,000
        # fixed-fixed pairs.
        bad_with_fixed = {}
        for q in variables:
            bad_with_fixed[q] = (q in fpair or any(third(q, f) in fixed for f in fixed))
        for mask in range(1<<len(small)):
            chosen=[variables[small[i]] for i in range(len(small)) if mask>>i&1]
            direct=not any(bad_with_fixed[q] for q in chosen)
            if direct:
                chosen_set=set(chosen)
                direct=all(third(a,b) not in fixed|chosen_set for a,b in itertools.combinations(chosen,2))
            assignment=[-1]*len(variables)
            for i,v in enumerate(small): assignment[v]=(mask>>i)&1
            encoded=all(sum(assignment[v] == 1 for v in c) <= 2 for c in clauses)
            sm["assignments"]+=1; sm["direct_feasible"]+=direct; sm["clause_feasible"]+=encoded
            sm["mismatches"]+=direct != encoded
        control={"baseline_size":len(base),"baseline_direct_valid":all(third(a,b) not in base for a,b in itertools.combinations(base,2)),
                 "planted_baseline_satisfies_line_clauses":planted_ok,"small_window":sm}
        (out/"control.json").write_text(json.dumps(control,indent=2,sort_keys=True)+"\n")
        start=time.monotonic(); solver=Solver(clauses,len(variables),target,start+args.seconds,log); solver.started=start
        try:
            answer=solver.run([-1]*len(variables)); classification="SAT" if answer else "UNSAT"
        except TimeoutError:
            answer=None; classification="TIMEOUT"
        elapsed=time.monotonic()-start
        selected=[] if answer is None else [variables[i] for i,x in enumerate(answer) if x]
        log({"event":"finish","classification":classification,"elapsed_seconds":elapsed,"nodes":solver.nodes,"conflicts":solver.conflicts,"propagations":solver.propagations,"selected":len(selected)})
    result={"kind":"expanded-insertion-independent-boolean-sat","input_sha256":hashlib.sha256(open(args.input,"rb").read()).hexdigest(),
      "classification":classification,"elapsed_seconds":elapsed,"counts":{"fixed":len(fixed),"variables":len(variables),"clauses":len(clauses),"target_selected":target,"target_total":513,"insert_b":len(ib),"insert_c":len(ic),"excluded_b":len(rb),"excluded_c":len(rc)},
      "solver":{"nodes":solver.nodes,"conflicts":solver.conflicts,"propagations":solver.propagations,"backend":"custom deterministic Boolean DPLL + cardinality propagation"},
      "hashes":{"pool":digest([db,dc,ib,ic]),"line_clauses":line_hash,"screen":hashlib.sha256((out/"screen.json").read_bytes()).hexdigest()},
      "resume_cursor":{"fixed_deletion_pool_hash":"14e5ced4a500c1631227d93fcbeafeb818221a797e027f18a3388c2f17e8c4a5","radius":args.radius,"next_phase":"try alternate deterministic deletion pool if this full insertion ball is UNSAT or times out"}}
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    if classification == "SAT":
        points=sorted(fixed|set(selected))
        (out/"candidate.json").write_text(json.dumps({"points":[list(vec(q)) for q in points]},indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))
if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--output",required=True); p.add_argument("--seconds",type=float,default=1740); p.add_argument("--radius",type=int,default=7); main(p.parse_args())
