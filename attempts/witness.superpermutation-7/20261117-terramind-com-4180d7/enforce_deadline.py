import datetime,json,os,pathlib,select,shlex,signal,subprocess,time
r=pathlib.Path(__file__).resolve().parent
budget=json.loads((r/'budget.json').read_text());wait=max(1,int((budget['deadline']-time.time())*1000))
q=select.kqueue();q.control([select.kevent(1,filter=select.KQ_FILTER_TIMER,flags=select.KQ_EV_ADD|select.KQ_EV_ONESHOT,data=wait)],1,None)
rows=[]
for line in subprocess.check_output(['ps','-Ao','pid,command'],text=True).splitlines()[1:]:
 bits=line.strip().split(None,1)
 if len(bits)!=2:continue
 pid,cmd=bits
 try:exe=shlex.split(cmd)[0]
 except (ValueError,IndexError):continue
 if str(r) in exe and pathlib.Path(exe).name in ['LKH','PC-audit','bridge','PermutationChains']:
  try:os.kill(int(pid),signal.SIGTERM);rows.append({'pid':int(pid),'exe':pathlib.Path(exe).name,'signal':15})
  except ProcessLookupError:pass
(r/'deadline-stop.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deadline':budget['deadline'],'terminated':rows,'rc':0}))
print('DEADLINE_ENFORCER_EXIT=0',flush=True)
