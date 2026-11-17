"""Pause the broad SAT slot, test exact repairs of the five-conflict candidate, resume."""
import pathlib,json,os,signal,subprocess,sys,time,datetime,random,itertools
P=pathlib.Path(__file__).resolve().parent
parent=23611
# Historical orchestration PID: refuse PID reuse outside this run.
parent_command=subprocess.run(['ps','-p',str(parent),'-o','command='],capture_output=True,text=True).stdout
if 'windows2.py' not in parent_command or 'schur7' not in parent_command:
 raise SystemExit('Historical pause wrapper: replay saved request files with sat.py child; this controller PID is no longer valid.')
os.kill(parent,signal.SIGSTOP)
kids=subprocess.run(['pgrep','-P',str(parent)],capture_output=True,text=True).stdout.split();pids=[int(x) for x in kids]
for pid in pids:os.kill(pid,signal.SIGSTOP)
start=time.monotonic();rng=random.Random(7301702)
print('START',datetime.datetime.now(datetime.timezone.utc).isoformat(),'seed',7301702,'paused',parent,pids,flush=True)
try:
 a=json.loads((P/'local-best.json').read_text())['colors'];(P/'three-seed.json').write_text(json.dumps({'colors':a})+'\n')
 tri=[(x,y,x+y) for x in range(1,849) for y in range(x,1698-x) if a[x-1]==a[y-1]==a[x+y-1]]
 print('SEED objective',len(tri),flush=True)
 verts={v for t in tri for v in t}|{1697};six={i+1 for i,c in enumerate(a) if c==6}
 cases=[]
 for c,d in itertools.combinations(range(6),2):cases.append((f'class6_plus{c}_{d}',six|{i+1 for i,v in enumerate(a) if v in (c,d)}|verts))
 for label,free in cases:
  for n in [1696,1697]:
   spec={'label':f'three_{label}_n{n}','n':n,'free':sorted(free-{1697}) if n==1696 else sorted(free)}
   if n==1697:spec['base']='three-seed.json'
   path=P/(spec['label']+'.request.json');path.write_text(json.dumps(spec));log=P/(spec['label']+'.log')
   with log.open('w') as out:
    proc=subprocess.Popen([sys.executable,'-I',str(P/'sat.py'),'child',str(path)],stdout=out,stderr=subprocess.STDOUT)
    try:code=proc.wait(timeout=30 if n==1697 else 10)
    except subprocess.TimeoutExpired:proc.kill();proc.wait();code=124
   text=log.read_text();print(text,end='',flush=True);print('EXIT',spec['label'],code,flush=True)
   if code==0 and 'RESULT True' in text:
    subprocess.run([str(pathlib.Path.home()/'.bun/bin/bun'),'frontier','diagnose',str(P/(spec['label']+'.json')),'--problem','witness.schur-7'],check=True)
    if n==1697:raise SystemExit(0)
 print('END seconds',time.monotonic()-start,flush=True)
finally:
 for pid in pids:
  try:os.kill(pid,signal.SIGCONT)
  except ProcessLookupError:pass
 try:os.kill(parent,signal.SIGCONT)
 except ProcessLookupError:pass
 print('RESUMED broad SAT',datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
