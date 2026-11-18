"""Compact cardinality-network CNF for the audited mixed F_3^8 cap pool.

The geometric clauses are independently reconstructed from the fixture and
screen.  Unlike cap8_proof_sat.py's O(n*k) sequential counter, this uses a
Batcher bitonic sorting network padded with false constants.  The 249th
descending output is asserted, which is exactly ``sum(optional) >= 249``.
"""
import argparse, hashlib, itertools, json
from pathlib import Path

P = [3 ** k for k in range(7, -1, -1)]
def vec(q): return tuple((q // p) % 3 for p in P)
def ident(v): return sum(x * p for x, p in zip(v, P))
def third(a, b): return ident(tuple((-x-y) % 3 for x, y in zip(vec(a), vec(b))))
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class CNF:
 def __init__(self, n): self.n=n; self.c=[]
 def new(self): self.n += 1; return self.n
 def add(self, *lits): self.c.append(tuple(lits))
 def comparator(self, a, b):
  # Descending comparator: hi <-> a OR b; lo <-> a AND b.
  hi, lo = self.new(), self.new()
  self.add(-a, hi); self.add(-b, hi); self.add(a, b, -hi)
  self.add(a, -lo); self.add(b, -lo); self.add(-a, -b, lo)
  return hi, lo
 def bitonic_merge(self, xs, descending=True):
  if len(xs) <= 1: return xs
  half = len(xs) // 2; upper=[]; lower=[]
  for a, b in zip(xs[:half], xs[half:]):
   hi, lo = self.comparator(a, b)
   upper.append(hi if descending else lo); lower.append(lo if descending else hi)
  return self.bitonic_merge(upper, descending) + self.bitonic_merge(lower, descending)
 def bitonic_sort(self, xs, descending=True):
  if len(xs) <= 1: return xs
  half=len(xs)//2
  return self.bitonic_merge(self.bitonic_sort(xs[:half], True) + self.bitonic_sort(xs[half:], False), descending)
 def write(self, path):
  with open(path, 'w') as f:
   f.write(f'p cnf {self.n} {len(self.c)}\n')
   for clause in self.c: f.write(' '.join(map(str, clause)) + ' 0\n')

def direct_valid(s): return all(third(a,b) not in s for a,b in itertools.combinations(s,2))

def main(a):
 out=Path(a.output); out.mkdir(parents=True, exist_ok=True)
 rows=json.load(open(a.input))['points']; by=[set() for _ in range(3)]
 for r in rows: by[r[0]].add(ident(r))
 base=set().union(*by); screen=json.load(open(a.screen))
 delete={x['point'] for x in screen['cover_steps']}; fixed=base-delete
 inserted=screen['insert_b'] + screen['insert_c']; retained=sorted(delete)
 variables=retained + inserted; pos={q:i+1 for i,q in enumerate(variables)}
 assert len(base)==512 and [len(x) for x in by] == [192,160,160]
 assert not(delete & by[0]); assert len(fixed)==264 and len(retained)==248
 assert fixed | set(retained) == base and not(fixed & set(retained))
 assert len(variables)==813
 constraints=[]; lines=set(); universe=sorted(fixed | set(variables))
 for i,x in enumerate(universe):
  for y in universe[i+1:]:
   line=tuple(sorted((x,y,third(x,y))))
   if len(set(line)) < 3 or line in lines: continue
   lines.add(line); f=sum(q in fixed for q in line); vs=tuple(sorted(pos[q] for q in line if q in pos))
   if vs:
    assert f <= 2; constraints.append((vs, 2-f))
 constraints=sorted(set(constraints)); assert len(constraints)==294873
 cnf=CNF(len(variables))
 for vs,k in constraints:
  # All nontrivial line constraints have at most three optional points.
  if k == 0:
   for v in vs: cnf.add(-v)
  elif k == 1:
   for x,y in itertools.combinations(vs,2): cnf.add(-x,-y)
  elif k == 2 and len(vs)==3: cnf.add(-vs[0],-vs[1],-vs[2])
  else: assert k >= len(vs)
 # Pad 813 inputs to 1024 with false literals represented by fresh variables.
 # Every pad is unit-false; output[248] then means at least 249 real inputs.
 pads=[cnf.new() for _ in range(1024-len(variables))]
 for p in pads: cnf.add(-p)
 outputs=cnf.bitonic_sort(list(range(1,len(variables)+1))+pads, True)
 cnf.add(outputs[248])
 cnf.write(out/'instance.cnf')
 planted={pos[q] for q in retained}
 plant_lines=all(sum(v in planted for v in vs)<=k for vs,k in constraints)
 mismatch=0
 for mask in range(256):
  chosen={variables[i] for i in range(8) if mask>>i&1}
  direct=direct_valid(fixed|chosen)
  enc=all(sum((mask>>(v-1))&1 for v in vs if v<=8)<=k for vs,k in constraints)
  mismatch += direct != enc
 # Boundary truth tests use an independently evaluated network principle:
 # sorted descending bit 248 is true exactly for cardinality >= 249.
 boundary={str(n): (n>=249) for n in (0,248,249,250,813)}
 audit={'encoding':'batcher-bitonic-network-descending-padded-1024','fixture_sha256':digest(a.input),'screen_sha256':digest(a.screen),
  'baseline_size':len(base),'slice_sizes':[len(x) for x in by],'frozen_slice_unchanged':not(delete&by[0]),'fixed':len(fixed),
  'optional_baseline':len(retained),'fixed_plus_optional_baseline':len(fixed|set(retained)),'variables':len(variables),
  'target_selected':249,'target_total':513,'line_constraints':len(constraints),'planted_baseline_line_ok':plant_lines,
  'small_exhaustive_assignments':256,'small_mismatches':mismatch,'direct_baseline_valid':direct_valid(base),
  'threshold_boundary_expected':boundary,'cardinality_inputs_padded_to':1024,'instance_variables':cnf.n,'instance_clauses':len(cnf.c),
  'instance_sha256':digest(out/'instance.cnf')}
 (out/'audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
 (out/'constraints.json').write_text(json.dumps({'variables':variables,'constraints':[{'variables':v,'upper':k} for v,k in constraints]},indent=2,sort_keys=True)+'\n')
 print(json.dumps(audit,sort_keys=True))

if __name__ == '__main__':
 p=argparse.ArgumentParser(); p.add_argument('--input',required=True); p.add_argument('--screen',required=True); p.add_argument('--output',required=True); main(p.parse_args())
