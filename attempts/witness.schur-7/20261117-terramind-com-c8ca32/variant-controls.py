import pathlib,json,subprocess,sys,hashlib,datetime
P=pathlib.Path(__file__).resolve().parent
print('START',datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
seen=set()
for i in range(5):
 a=json.loads((P/f'basevariant{i}.json').read_text())['colors'];seen.add(tuple(a))
 fixed={str(x):a[x-1] for x in range(1,537)};fixed['537']=6
 for x in range(1,538):fixed[str(1697-x)]=fixed[str(x)]
 spec={'label':f'variant{i}_control1696','n':1696,'free':[x for x in range(1,1697) if str(x) not in fixed],'fixed':fixed}
 path=P/(spec['label']+'.request.json');path.write_text(json.dumps(spec));log=P/(spec['label']+'.log')
 with log.open('w') as out:
  proc=subprocess.Popen([sys.executable,'-I',str(P/'sat.py'),'child',str(path)],stdout=out,stderr=subprocess.STDOUT)
  try:code=proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill();proc.wait();code=124
 print(log.read_text(),end='',flush=True);print('EXIT',i,code,flush=True)
 if code==0 and 'RESULT True' in log.read_text():subprocess.run([str(pathlib.Path.home()/'.bun/bin/bun'),'frontier','diagnose',str(P/(spec['label']+'.json')),'--problem','witness.schur-7'],check=True)
print('UNIQUE_BASE_VARIANTS',len(seen),'of 5',flush=True)
