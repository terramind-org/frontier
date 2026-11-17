"""Fixed-end LKH re-solves with diverse initial orders, after a stationary seeded phase."""
import hashlib,json,os,pathlib,random,sys,time
r=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(r));import lkh_search as L
root=r/'second';L.ROOT=root
rows=[json.loads(x) for x in (root/'lkh.jsonl').read_text().splitlines()]
tours=[x for x in rows if x.get('event')=='tour']
assert all(x.get('distance',0)==0 for x in tours), 'continuation requires unchanged paths'
paths=[L.path(json.loads((root/f).read_text())['word'],7) for f in ['baseline.json','sol2.json']]
seen={x['hash'] for x in tours if 'hash' in x};best=5905;it=max(x['iteration'] for x in tours)+1
rng=random.Random(20261120);deadline=json.loads((r/'budget.json').read_text())['deadline']
(r/'second-lkh.lock').write_text(str(os.getpid()))
L.emit(root/'lkh.jsonl',event='phase_start',phase='perturbed_initial_orders',pid=os.getpid(),rng_seed=20261120)
while time.time()<deadline-10:
 which=it%2;p=paths[which];heavy=[i for i in range(len(p)-1) if L.weight(p[i],p[i+1])>=3]
 anchor=rng.choice(heavy);size=rng.choice([1000,1500,2000,2500,3000]);lo=max(0,min(len(p)-size,anchor-rng.randrange(size)));hi=lo+size
 seg=p[lo:hi];order=list(range(size));mode=it%4
 if mode==1:
  for _ in range(rng.randint(1,8)):
   a=rng.randrange(1,size-2);order[a],order[a+1]=order[a+1],order[a]
 elif mode==2:
  for _ in range(rng.randint(1,4)):
   width=rng.randint(5,20);a,b=sorted(rng.sample(range(1,size-width-1),2))
   if b>=a+width:order[a:a+width],order[b:b+width]=order[b:b+width],order[a:a+width]
 elif mode==3:
  a=rng.randrange(1,size-101);part=order[a:a+100];rng.shuffle(part);order[a:a+100]=part
 bad=[seg[i] for i in order];seed=rng.randrange(1,2**30);cap=min(120,deadline-time.time()-5)
 if cap<5:break
 q,row=L.solve(bad,root/f'segment{which}',seed,cap,trials=20000,runs=10,candidates=30)
 row.update(initial_order=order,perturbation=['unchanged','adjacent_swaps','block_swaps','shuffle_100'][mode],initial_distance=sum(a!=b for a,b in zip(order,range(size))),initial_segment_length=len(L.word(bad)))
 if q:
  candidate=p[:lo]+q+p[hi:];w=L.word(candidate);assert L.valid(w,7)
  digest=hashlib.sha256(w.encode()).hexdigest();seen.add(digest);rc=L.diagnose(w,root/f'latest-{which}.json')
  old=len(L.word(p));new=len(w)
  if new<=old:paths[which]=candidate
  if new<best:best=new;L.diagnose(w,r/f'best-{new}.json')
  row.update(old=old,returned_length=new,accepted=new<=old,heavy=sum(v for k,v in L.stats(candidate).items() if k>=3),hash=digest,distinct_words=len(seen),distance=sum(a!=b for a,b in zip(p,candidate)),diagnose_rc=rc)
 L.emit(root/'lkh.jsonl',event='tour',phase='perturbed_initial_orders',iteration=it,start_word=which+1,lo=lo,hi=hi,best=best,**row)
 it+=1
L.emit(root/'lkh.jsonl',event='end',best=best,iterations=it,distinct_words=len(seen))
L.emit(root/'lkh.jsonl',event='process_exit',pid=os.getpid(),rc=0)
print('DIVERSE_LKH_SEARCH_EXIT=0',flush=True)
