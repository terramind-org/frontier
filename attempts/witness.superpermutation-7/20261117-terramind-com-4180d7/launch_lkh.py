import sys,pathlib,subprocess,json,os
r=pathlib.Path(__file__).resolve().parent
lock=os.open(r/'lkh.lock',os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(lock,str(os.getpid()).encode());os.close(lock)
p=subprocess.run([sys.executable,'-I',str(r/'calibrate_segments.py')]);
if p.returncode:sys.exit(p.returncode)
sys.path.insert(0,str(r));import lkh_search as L
L.emit(r/'lkh.jsonl',event='start',pid=os.getpid())
L.search(json.loads((r/'budget.json').read_text())['deadline'])
L.emit(r/'lkh.jsonl',event='process_exit',pid=os.getpid(),rc=0)
print('LKH_SEARCH_EXIT=0',flush=True)
