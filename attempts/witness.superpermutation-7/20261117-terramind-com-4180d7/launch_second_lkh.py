import json,os,pathlib,shutil,sys
r=pathlib.Path(__file__).resolve().parent
rows=[json.loads(x) for x in (r/'kernel.jsonl').read_text().splitlines()]
assert any(x.get('event')=='kernel_stage_dropped' for x in rows), 'kernel core is still reserved'
lock=os.open(r/'second-lkh.lock',os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(lock,str(os.getpid()).encode());os.close(lock)
sys.path.insert(0,str(r));import lkh_search as L
wd=r/'second';wd.mkdir(exist_ok=True)
shutil.copy(r/'sol2.json',wd/'baseline.json');shutil.copy(r/'baseline.json',wd/'sol2.json')
L.ROOT=wd
L.emit(wd/'lkh.jsonl',event='start',pid=os.getpid(),rng_seed=20261119,baseline_mapping='baseline=published-sol2; sol2=published-sol1')
L.search(json.loads((r/'budget.json').read_text())['deadline'],20261119)
L.emit(wd/'lkh.jsonl',event='process_exit',pid=os.getpid(),rc=0)
print('SECOND_LKH_SEARCH_EXIT=0',flush=True)
