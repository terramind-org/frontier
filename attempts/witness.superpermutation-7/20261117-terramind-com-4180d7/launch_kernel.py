import pathlib,sys,json,time,os
r=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(r));import kernel_runs as K
lock=os.open(r/'kernel.lock',os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(lock,str(os.getpid()).encode());os.close(lock)
K.emit(event='process_start',pid=os.getpid())
rows=[json.loads(x) for x in (r/'kernel.jsonl').read_text().splitlines()]
ok=any(x.get('event')=='positive_control' and x.get('passed') for x in rows)
for i,k in enumerate(['666646664466646666','66466466466644666466466466']):
 if ok:break
 remaining=json.loads((r/'budget.json').read_text())['start_epoch']+25*60-time.time()
 if remaining<10:break
 row=K.run(k,['symmPairs','fullSymm','branchMostFree'],min(300,remaining-2),f'positive5906-retry{i}')
 ok=any(w['length']==5906 for w in row['solutions'])
K.emit(event='completion_calibration',passed=ok)
if ok:K.search(json.loads((r/'budget.json').read_text())['deadline'])
else:K.emit(event='kernel_stage_dropped',reason='No published 5906 completion reproduced within preflight caps')
K.emit(event='process_exit',pid=os.getpid(),rc=0 if ok else 2)
print('KERNEL_SEARCH_EXIT='+str(0 if ok else 2),flush=True)
sys.exit(0 if ok else 2)
