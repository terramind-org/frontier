import os,select,json,pathlib,sys,time
r=pathlib.Path(__file__).resolve().parent
pids=[]
for f in ['lkh.lock','kernel.lock','second-lkh.lock']:
 if (r/f).exists():
  pid=int((r/f).read_text())
  try:os.kill(pid,0);pids.append(pid)
  except ProcessLookupError:pass
k=select.kqueue()
for pid in pids:
 try:k.control([select.kevent(pid,filter=select.KQ_FILTER_PROC,flags=select.KQ_EV_ADD|select.KQ_EV_ENABLE,fflags=select.KQ_NOTE_EXIT)],0,0)
 except ProcessLookupError:pass
print('remaining_budget_s',round(json.loads((r/'budget.json').read_text())['deadline']-time.time()),'watching',pids,flush=True)
if pids:print('events',[(e.ident,e.data) for e in k.control([],len(pids),50)],flush=True)
for f in ['lkh.jsonl','second/lkh.jsonl']:
 p=r/f
 if p.exists():
  rows=[json.loads(x) for x in p.read_text().splitlines()]
  tours=[x for x in rows if x.get('event')=='tour']
  print(json.dumps({'log':f,'last_event':rows[-1].get('event'),'calls':len(tours),'best':min([5905]+[x['returned_length'] for x in tours if x.get('returned_length')]),'distinct_returned':len({x['hash'] for x in tours if 'hash' in x}),'last_iteration':tours[-1]['iteration'] if tours else None}),flush=True)
