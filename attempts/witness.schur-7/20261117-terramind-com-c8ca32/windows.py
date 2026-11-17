"""Progressively enlarge the contiguous top window; timeouts are never UNSAT."""
import datetime,json,pathlib,subprocess,sys,time
P=pathlib.Path(__file__).resolve().parent
end=datetime.datetime.fromisoformat('2026-11-17T18:08:50+00:00').timestamp()
start=time.monotonic();print('START',datetime.datetime.now(datetime.timezone.utc).isoformat(),'deadline',end,flush=True)
def run(w,n,limit,round):
 label=f'window{w}_n{n}_round{round}'
 spec={'label':label,'n':n,'free':list(range(1697-w,1697))}
 path=P/(label+'.request.json');path.write_text(json.dumps(spec))
 remaining=end-time.time()
 if remaining<2:return None
 with (P/(label+'.log')).open('w') as out:
  proc=subprocess.Popen([sys.executable,'-I',str(P/'sat.py'),'child',str(path)],stdout=out,stderr=subprocess.STDOUT)
  try:code=proc.wait(timeout=min(limit,remaining))
  except subprocess.TimeoutExpired:proc.kill();proc.wait();code=124
 text=(P/(label+'.log')).read_text();print(text,end='',flush=True);print('EXIT',label,code,'elapsed',time.monotonic()-start,flush=True)
 if code==0 and 'RESULT True' in text:
  subprocess.run([str(pathlib.Path.home()/'.bun/bin/bun'),'frontier','diagnose',str(P/(label+'.json')),'--problem','witness.schur-7'],check=True)
  return True
 if code==0 and 'RESULT False' in text:return False
 return None
pending=[]
for w in [1001,1016,1032,1048,1064,1080,1096,1112,1128,1144,1160,1200,1300,1400,1500,1600,1696]:
 control=run(w,1696,30,0)
 target=run(w,1697,180,0)
 print('PAIRED_WINDOW',w,'control',control,'target',target,flush=True)
 if target:sys.exit(0)
 if target is None:pending.append(w)
for round in range(1,20):
 for w in pending:
  if time.time()>=end-2:break
  control=run(w,1696,30,round)
  target=run(w,1697,900,round)
  print('PAIRED_WINDOW',w,'control',control,'target',target,flush=True)
  if target:sys.exit(0)
 if time.time()>=end-2:break
print('END',datetime.datetime.now(datetime.timezone.utc).isoformat(),'wall_seconds',time.monotonic()-start,'exit 0',flush=True)
