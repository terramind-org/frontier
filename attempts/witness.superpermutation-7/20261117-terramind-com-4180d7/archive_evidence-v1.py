import datetime,hashlib,json,os,pathlib,select,shutil,time
r=pathlib.Path(__file__).resolve().parent
out=r/'archive';out.mkdir(exist_ok=True);done=set();q=select.kqueue();handles=[]
roots=[r,r/'second']
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def collect():
 for root in roots:
  log=root/'lkh.jsonl'
  if not log.exists():continue
  for row in map(json.loads,log.read_text().splitlines()):
   if row.get('event')!='tour':continue
   key=(root.name,row['iteration'])
   if key in done:continue
   which=row['start_word']-1
   wd=root/(('full' if row['full'] else 'segment')+str(which))
   candidate=root/f'latest-{which}.json'
   match=candidate.exists() and hashlib.sha256(json.loads(candidate.read_text())['word'].encode()).hexdigest()==row.get('hash')
   target=out/('primary' if root==r else 'second')/str(row['iteration']);target.mkdir(parents=True,exist_ok=True)
   (target/'row.json').write_text(json.dumps(row))
   if match:
    for f in ['stdout.log','result.tour','status.json','initial.tour','run.par']:
     if (wd/f).exists():shutil.copy(wd/f,target/f)
    shutil.copy(candidate,target/'word.json')
    if candidate.with_suffix('.diagnose.log').exists():shutil.copy(candidate.with_suffix('.diagnose.log'),target/'diagnose.log')
   with (out/'manifest.jsonl').open('a') as f:f.write(json.dumps({'utc':utc(),'run':key[0],'iteration':key[1],'hash':row.get('hash'),'captured':match})+'\n')
   done.add(key)
collect()
for root in roots:
 fd=os.open(root/'lkh.jsonl',os.O_RDONLY);handles.append(fd)
 q.control([select.kevent(fd,filter=select.KQ_FILTER_VNODE,flags=select.KQ_EV_ADD|select.KQ_EV_CLEAR,fflags=select.KQ_NOTE_WRITE)],0,0)
wait=max(1,int((json.loads((r/'budget.json').read_text())['deadline']+5-time.time())*1000))
q.control([select.kevent(1,filter=select.KQ_FILTER_TIMER,flags=select.KQ_EV_ADD|select.KQ_EV_ONESHOT,data=wait)],0,0)
while True:
 events=q.control([],10,None);collect()
 if any(e.filter==select.KQ_FILTER_TIMER for e in events):break
(out/'exit.json').write_text(json.dumps({'utc':utc(),'rc':0,'calls':len(done)}))
print('EVIDENCE_ARCHIVE_EXIT=0',flush=True)
