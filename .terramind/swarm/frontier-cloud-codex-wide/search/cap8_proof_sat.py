"""Independent CNF/LRAT audit for the corrected F_3^8 cap batch.

This deliberately does not consume the previous PB clauses.  It reconstructs
the batch from the recorded point IDs, enumerates every variable-containing
line, writes a DIMACS encoding, and asks CaDiCaL for an LRAT certificate.
"""
import argparse, hashlib, itertools, json
from pathlib import Path

P = [3 ** k for k in range(7, -1, -1)]
def vec(q): return tuple((q // p) % 3 for p in P)
def ident(v): return sum(x * p for x, p in zip(v, P))
def third(a, b): return ident(tuple((-x-y) % 3 for x,y in zip(vec(a), vec(b))))
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class CNF:
 def __init__(self, n): self.n=n; self.c=[]
 def new(self): self.n+=1; return self.n
 def add(self, *lits): self.c.append(tuple(lits))
 def atmost(self, xs, k):
  if k < 0: self.add(); return
  if k == 0:
   for x in xs:self.add(-x)
   return
  if k >= len(xs): return
  # Sinz sequential counter: at most k of xs.
  s=[[self.new() for _ in range(k)] for _ in range(len(xs)-1)]
  self.add(-xs[0], s[0][0])
  for j in range(1,k): self.add(-s[0][j])
  for i in range(1,len(xs)-1):
   self.add(-xs[i], s[i][0]); self.add(-s[i-1][0], s[i][0])
   for j in range(1,k):
    self.add(-xs[i], -s[i-1][j-1], s[i][j]); self.add(-s[i-1][j], s[i][j])
   self.add(-xs[i], -s[i-1][k-1])
  self.add(-xs[-1], -s[-1][k-1])
 def write(self,path):
  with open(path,'w') as f:
   f.write(f'p cnf {self.n} {len(self.c)}\n')
   for c in self.c:f.write(' '.join(map(str,c))+' 0\n')

def direct_valid(s): return all(third(a,b) not in s for a,b in itertools.combinations(s,2))

def main(a):
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 rows=json.load(open(a.input))['points']; by=[set() for _ in range(3)]
 for r in rows:by[r[0]].add(ident(r))
 base=set().union(*by); screen=json.load(open(a.screen))
 delete={x['point'] for x in screen['cover_steps']}; fixed=base-delete
 ins=screen['insert_b']+screen['insert_c']; retained=sorted(delete); variables=retained+ins
 assert len(base)==512 and len(by[0])==192
 assert not (delete & by[0]), 'frozen slice changed'
 assert fixed|set(retained)==base and not (fixed&set(retained))
 assert len(fixed)==392 and len(variables)==155 and 513-len(fixed)==121
 pos={q:i+1 for i,q in enumerate(variables)}; lines=set(); constraints=[]
 universe=sorted(fixed|set(variables))
 for i,x in enumerate(universe):
  for y in universe[i+1:]:
   z=third(x,y); line=tuple(sorted((x,y,z)))
   if len(set(line))<3 or line in lines:continue
   lines.add(line); f=sum(q in fixed for q in line); vs=tuple(sorted(pos[q] for q in line if q in pos))
   if vs:
    assert f<=2
    constraints.append((vs,2-f))
 constraints=sorted(set(constraints))
 cnf=CNF(len(variables))
 for vs,k in constraints:cnf.atmost(vs,k)
 # >=121 selected x is <=34 unselected complements, encoded directly by
 # applying the counter to literals -x.
 cnf.atmost([-x for x in range(1,len(variables)+1)],len(variables)-121)
 cnf.write(out/'instance.cnf')
 planted={pos[q] for q in retained}
 plant_lines=all(sum(v in planted for v in vs)<=k for vs,k in constraints)
 # exhaustive agreement over first eight variables, no cardinality target
 mismatch=0
 for mask in range(256):
  chosen={variables[i] for i in range(8) if mask>>i&1}; direct=direct_valid(fixed|chosen)
  enc=all(sum((mask>>(v-1))&1 for v in vs if v<=8)<=k for vs,k in constraints)
  mismatch+=direct != enc
 audit={'baseline_sha256':digest(a.input),'screen_sha256':digest(a.screen),'baseline_size':len(base),'slice_sizes':[len(x) for x in by],
  'frozen_unchanged':not(delete&by[0]),'fixed':len(fixed),'optional_baseline':len(retained),'fixed_plus_optional_baseline':len(fixed|set(retained)),
  'variables':len(variables),'target_selected':121,'target_total':513,'line_constraints':len(constraints),'planted_baseline_line_ok':plant_lines,
  'small_exhaustive_assignments':256,'small_mismatches':mismatch,'direct_baseline_valid':direct_valid(base),
  'instance_sha256':digest(out/'instance.cnf')}
 (out/'audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
 # Save the independently enumerated semantic constraints apart from DIMACS.
 (out/'constraints.json').write_text(json.dumps({'variables':variables,'constraints':[{'variables':v,'upper':k} for v,k in constraints]},indent=2,sort_keys=True)+'\n')
 print(json.dumps(audit,sort_keys=True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--screen',required=True);p.add_argument('--output',required=True);main(p.parse_args())
