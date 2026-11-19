"""Switch at a completed-call boundary, preserving every completed call and stopping no solver mid-call."""
import datetime,json,os,pathlib,select,signal,subprocess,sys
r=pathlib.Path(__file__).resolve().parent;pid=int((r/'second-lkh.lock').read_text());log=r/'second/lkh.jsonl'
fd=os.open(log,os.O_RDONLY);q=select.kqueue()
q.control([select.kevent(fd,filter=select.KQ_FILTER_VNODE,flags=select.KQ_EV_ADD|select.KQ_EV_CLEAR,fflags=select.KQ_NOTE_WRITE)],0,0)
while True:
 q.control([],1,None)
 rows=[json.loads(x) for x in log.read_text().splitlines()];tours=[x for x in rows if x.get('event')=='tour']
 if any(x.get('distance',0)>0 for x in tours):
  print('SWITCH_SKIPPED_NEW_ORDERING',flush=True);sys.exit(0)
 os.kill(pid,signal.SIGSTOP)
 children=[x for x in subprocess.check_output(['ps','-Ao','pid,ppid'],text=True).splitlines()[1:] if int(x.split()[1])==pid]
 if children:os.kill(pid,signal.SIGCONT);continue
 q.control([select.kevent(pid,filter=select.KQ_FILTER_PROC,flags=select.KQ_EV_ADD|select.KQ_EV_ONESHOT,fflags=select.KQ_NOTE_EXIT)],0,0)
 os.kill(pid,signal.SIGTERM);os.kill(pid,signal.SIGCONT);events=q.control([],2,5)
 if not any(x.filter==select.KQ_FILTER_PROC for x in events):raise RuntimeError('old process exit not observed')
 (r/'second-phase-stop.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':pid,'signal':15,'last_completed_iteration':tours[-1]['iteration'],'solver_children_at_stop':0}))
 break
os.execv(sys.executable,[sys.executable,'-I',str(r/'diverse_lkh.py')])
