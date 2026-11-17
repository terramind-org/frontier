"""Second-stage solver jobs: reflection seeds, six-colour variants, local repair."""
import pathlib,json,time,subprocess,sys,random,datetime
P=pathlib.Path(__file__).resolve().parent
start=time.monotonic();deadline=start+float(sys.argv[1]);rng=random.Random(7301699)
print('START',datetime.datetime.now(datetime.timezone.utc).isoformat(),'budget',sys.argv[1],'seed',7301699,flush=True)

def run(spec,seconds):
 remaining=deadline-time.monotonic()
 if remaining<3:return None
 path=P/'stage2-current.json';path.write_text(json.dumps(spec));log=P/(spec['label']+'.log')
 with log.open('w') as out:
  proc=subprocess.Popen([sys.executable,'-I',str(P/'sat.py'),'child',str(path)],stdout=out,stderr=subprocess.STDOUT)
  try:code=proc.wait(timeout=min(seconds,remaining))
  except subprocess.TimeoutExpired:proc.kill();proc.wait();code=124
 text=log.read_text();print(text,end='',flush=True);print('EXIT',spec['label'],code,'elapsed',time.monotonic()-start,flush=True)
 if code==0 and 'RESULT True' in text:
  subprocess.run([str(pathlib.Path.home()/'.bun/bin/bun'),'frontier','diagnose',str(P/(spec['label']+'.json')),'--problem','witness.schur-7'],stdout=sys.stdout,stderr=sys.stdout)
  return True
 if code==0 and 'RESULT False' in text:return False
 return None

b=json.loads((P/'baseline.json').read_text())['colors']
# Positive controls use the unchanged known partition and the identical free set intersected with 1..1696.
for n in [1697,1698,1700,1704,1712]:
 fixed={str(x):b[x-1] for x in range(1,538)}
 for x in range(1,538):fixed[str(n+1-x)]=b[x-1]
 free=[x for x in range(1,n+1) if str(x) not in fixed]
 control=run({'label':f'reflect{n}_control','n':1696,'free':[x for x in free if x<=1696]},30)
 result=run({'label':f'reflect{n}','n':n,'free':free,'fixed':fixed},120)
 print('PAIRED',n,control,result,flush=True)
# Force a distinct six-colour prefix, fixing its first 100 entries; use actual SAT-produced bases.
for variant in range(5):
 spec={'label':f'basevariant{variant}','n':536,'k':6,'free':list(range(101,537)),'different':list(range(101+variant*30,131+variant*30))}
 if run(spec,90):
  vb=json.loads((P/(spec['label']+'.json')).read_text())['colors']
  for n in [1697,1698]:
   fixed={str(x):vb[x-1] for x in range(1,537)};fixed['537']=6
   for x in range(1,538):fixed[str(n+1-x)]=fixed[str(x)]
   free=[x for x in range(1,n+1) if str(x) not in fixed]
   run({'label':f'variant{variant}_reflect{n}','n':n,'free':free,'fixed':fixed},120)
idx=0
while time.monotonic()<deadline-3:
 try:a=json.loads((P/'local-best.json').read_text())['colors']
 except (ValueError,FileNotFoundError):continue
 triples=[(x,y,x+y) for x in range(1,len(a)//2+1) for y in range(x,len(a)-x+1) if a[x-1]==a[y-1]==a[x+y-1]]
 vertices=set(v for t in triples for v in t); vertices.add(1697)
 radius=[0,1,2,4,8,16][idx%6]
 free={x+d for x in vertices for d in range(-radius,radius+1) if 1<=x+d<=1697}
 extra=[0,64,128,256,512,848][(idx//6)%6]
 free.update(rng.sample(range(1,1698),extra))
 if idx%12==11:free=set(rng.sample(range(1,1698),1400))|vertices
 snapshot=f'local-snapshot{idx}.json';(P/snapshot).write_text(json.dumps({'colors':a})+'\n')
 label=f'repair{idx}_o{len(triples)}_r{radius}_extra{extra}'
 control=run({'label':label+'_control','n':1696,'free':sorted(free-{1697})},30)
 result=run({'label':label,'n':1697,'free':sorted(free),'base':snapshot},120)
 print('PAIRED_REPAIR',label,'control',control,'target',result,'free',len(free),flush=True)
 if result:break
 idx+=1
print('END',datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds',time.monotonic()-start,flush=True)
