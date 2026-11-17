"""Run with the scratch venv Python -I. Child mode builds a simplified exact CNF."""
import json,time,sys,pathlib,random,subprocess,datetime,itertools
from pysat.solvers import Cadical195
P=pathlib.Path(__file__).resolve().parent

def objective(a):
 return sum(a[x-1]==a[y-1]==a[x+y-1] for x in range(1,len(a)//2+1) for y in range(x,len(a)-x+1))

def child(spec):
 base=json.loads((P/spec.get('base','baseline.json')).read_text())['colors']; n=spec['n']; k=spec.get('k',7); original_length=len(base); base=base[:n]+[0]*max(0,n-len(base));
 for x,c in spec.get('fixed',{}).items():base[int(x)-1]=c
 free={x for x in spec['free'] if x<=n}|{x for x in range(original_length+1,n+1) if str(x) not in spec.get('fixed',{})}; v=lambda x,c:(x-1)*k+c+1
 (P/(spec['label']+'.spec.json')).write_text(json.dumps(dict(spec,effective_free=sorted(free)))+'\n')
 assert all(0<=base[x-1]<k for x in range(1,n+1) if x not in free)
 t=time.monotonic(); print('START',datetime.datetime.now(datetime.timezone.utc).isoformat(),spec['label'],'N',n,'free',len(free),flush=True)
 with Cadical195() as s:
  clauses=0
  for x in sorted(free):
   s.add_clause([v(x,c) for c in range(k)]); clauses+=1
   for c,d in itertools.combinations(range(k),2):s.add_clause([-v(x,c),-v(x,d)]);clauses+=1
  for x in range(1,n//2+1):
   for y in range(x,n-x+1):
    vs=set((x,y,x+y)); fixed={base[z-1] for z in vs if z not in free}
    if len(fixed)>1:continue
    fv=vs & free
    if not fv:
     if len(fixed)==1: s.add_clause([]); clauses+=1
     continue
    for c in fixed if fixed else range(k):s.add_clause([-v(z,c) for z in fv]);clauses+=1
  if spec.get('different'):s.add_clause([-v(x,base[x-1]) for x in spec['different']])
  print('BUILT clauses',clauses,'seconds',time.monotonic()-t,flush=True)
  # Positive phases seed the published colouring, but are not assumptions.
  phase=base
  if n==1697 and k==7 and len(free)==n and (P/'local-best.json').exists():
   phase=json.loads((P/'local-best.json').read_text())['colors']
   (P/(spec['label']+'.phase.json')).write_text(json.dumps({'colors':phase})+'\n')
   print('PHASE_SEED saved local-best; independent objective',objective(phase),flush=True)
  s.set_phases([v(x,phase[x-1]) for x in free if x<=len(phase) and phase[x-1]<k])
  sat=s.solve();print('RESULT',sat,'seconds',time.monotonic()-t,'stats',s.accum_stats(),flush=True)
  if sat:
   model=set(s.get_model()); a=[next(c for c in range(k) if v(x,c) in model) if x in free else base[x-1] for x in range(1,n+1)]
   o=objective(a);assert o==0
   (P/(spec['label']+'.json')).write_text(json.dumps({'colors':a})+'\n')
   print('INDEPENDENT_OBJECTIVE',o,flush=True)
  return sat

def main():
 b=json.loads((P/'baseline.json').read_text())['colors'];bad=b.copy();bad[1]=bad[0]
 print('SELFTEST baseline',objective(b),'broken',objective(bad),flush=True);assert objective(b)==0 and objective(bad)>0
 start=time.monotonic(); deadline=start+float(sys.argv[1]);rng=random.Random(7301697)
 print('SEARCH_START',datetime.datetime.now(datetime.timezone.utc).isoformat(),'budget',sys.argv[1],'seed',7301697,flush=True)
 cases=[]
 for w in [32,64,128,256,400,600,800,848,1000,1160]:cases.append((f'top{w}',list(range(1697-w,1697)),120))
 for w in [256,512,848,1160]:cases.append((f'random{w}',rng.sample(range(1,1697),w),120))
 for c in range(7):cases.append((f'class{c}',[i+1 for i,x in enumerate(b) if x==c],90))
 for modulus in [2,3,4]:
  for residue in range(modulus):cases.append((f'residue{modulus}_{residue}',[x for x in range(1,1697) if x%modulus==residue],90))
 # Recreate Rowley's construction at a new order by fixing the 536 base and its new complements.
 for n in [1697,1698,1700]:
  fixed=set(range(1,537));free=[x for x in range(1,1697) if x not in fixed]
  cases.append((f'base536_N{n}',free,300))
 idx=0
 while time.monotonic()<deadline:
  if idx<len(cases):label,free,limit=cases[idx]
  else:
   w=rng.choice([1000,1200,1400,1600,1696]);label=f'broad{idx}_{w}';free=rng.sample(range(1,1697),w);limit=300
  idx+=1
  n=int(label.split('_N')[1]) if '_N' in label else 1697
  for size in [1696,n]:
   remaining=deadline-time.monotonic()
   if remaining<5:break
   spec={'label':label+f'_n{size}','n':size,'free':free}
   path=P/'current.json';path.write_text(json.dumps(spec))
   log=P/(spec['label']+'.log')
   with log.open('w') as out:
    proc=subprocess.Popen([sys.executable,'-I',str(P/'sat.py'),'child',str(path)],stdout=out,stderr=subprocess.STDOUT)
    try:code=proc.wait(timeout=min(limit if size!=1696 else 45,remaining))
    except subprocess.TimeoutExpired:
     proc.kill();proc.wait();code=124
   content=log.read_text();print(content,end='',flush=True);print('EXIT',spec['label'],code,'elapsed_total',time.monotonic()-start,flush=True)
   if code!=0 and size==1696:print('CONTROL FAILED OR TIMEOUT; no UNSAT inference for this pair',flush=True)
   if size>1696 and 'RESULT True' in content:
    print('CANDIDATE',spec['label'],flush=True)
    subprocess.run([str(pathlib.Path.home()/'.bun/bin/bun'),'frontier','diagnose',str(P/(spec['label']+'.json')),'--problem','witness.schur-7'],check=True)
    return
 print('SEARCH_END',datetime.datetime.now(datetime.timezone.utc).isoformat(),'wall_seconds',time.monotonic()-start,flush=True)
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='child':child(json.loads(pathlib.Path(sys.argv[2]).read_text()))
 else:main()
