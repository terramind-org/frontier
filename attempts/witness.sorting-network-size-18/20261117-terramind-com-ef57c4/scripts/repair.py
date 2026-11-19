"""Fixed-length repair using exact all-input bitsets and cached prefix states.
Counts DISTINCT sampled ordered networks, sampled every 128 candidate evaluations.
No claim that the sample counts every network visited.
"""
import pathlib,json,time,random,sys,math,datetime
S=pathlib.Path(__file__).resolve().parent

def emit(**x):print(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**x)),flush=True)
def patterns(n):
    total=1<<n;out=[]
    for w in range(n):
        half=1<<w;v=((1<<half)-1)<<half;width=half*2
        while width<total:v|=v<<width;width*=2
        out.append(v)
    return out

def states(gates,n):
    v=patterns(n);cache=[v.copy()]
    for i,j in gates:
        v=v.copy();v[i],v[j]=v[i]&v[j],v[i]|v[j];cache.append(v)
    return cache

def score(gates,cache,first):
    v=cache[first].copy()
    for i,j in gates[first:]:v[i],v[j]=v[i]&v[j],v[i]|v[j]
    bad=0
    for i in range(len(v)-1):bad|=v[i]&~v[i+1]
    return bad.bit_count()

def run(seconds,n,starts,name,seed,calibration=False):
    rng=random.Random(seed);pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    deadline=time.monotonic()+seconds
    if n==18:
        deadline=min(deadline,time.monotonic()+json.load(open(S/'budget.json'))['deadline_epoch']-time.time())
    visited=set();evaluations=0;best=1<<n;restarts=0;accepted=0
    emit(event='start',name=name,seconds=seconds,n=n,seed=seed)
    start=time.monotonic();next_report=start+10
    while time.monotonic()<deadline:
        gates=starts[restarts%len(starts)].copy();origin=gates.copy();cache=states(gates,n);current=score(gates,cache,0);restarts+=1
        if current<best:
            best=current;(S/(name+'.best.json')).write_text(json.dumps({'comparators':gates}));emit(event='best',failures=best,evaluations=evaluations,restart=restarts)
        if calibration:
            # Enumerate the same legal one-gate replacements used by the search.
            for pos in range(len(gates)):
                for pair in pairs:
                    candidate=gates.copy();candidate[pos]=pair;evaluations+=1
                    result=score(candidate,cache,pos)
                    if result==0:
                        (S/(name+'.best.json')).write_text(json.dumps({'comparators':candidate}));emit(event='result',status='calibration_PASS',failures=0,evaluations=evaluations);return
            raise AssertionError('repair calibration failed')
        for step in range(20000):
            if time.monotonic()>=deadline:break
            candidate=gates.copy();p=rng.randrange(len(gates));kind=rng.randrange(6)
            if kind<3:
                candidate[p]=rng.choice(pairs);first=p
            elif kind==3:
                q=rng.randrange(len(gates));candidate[p],candidate[q]=candidate[q],candidate[p];first=min(p,q)
            elif kind==4:
                q=rng.randrange(len(gates));candidate[p]=rng.choice(pairs);candidate[q]=rng.choice(pairs);first=min(p,q)
            else:
                q=rng.randrange(len(gates));gate=candidate.pop(p);candidate.insert(q,gate);first=min(p,q)
            value=score(candidate,cache,first);evaluations+=1
            if evaluations%128==0:visited.add(bytes(x for g in candidate for x in g))
            if value<best:
                best=value;(S/(name+'.best.json')).write_text(json.dumps({'comparators':candidate}));emit(event='best',failures=best,evaluations=evaluations,restart=restarts)
            if value==0:
                emit(event='result',status='valid_candidate',failures=0,evaluations=evaluations,distinct_sampled=len(visited));return
            # Temperatures are varied by restart; cooling is within a 20k-step restart.
            temp=[0,1,4,16][restarts%4]*(1-step/20000)
            if value<=current or (temp>0 and rng.random()<math.exp(max(-700,(current-value)/temp))):
                gates=candidate;current=value;cache=states(gates,n);accepted+=1
            now=time.monotonic()
            if now>=next_report:
                distance=sum(a!=b for a,b in zip(gates,origin))
                emit(event='heartbeat',evaluations=evaluations,distinct_sampled=len(visited),sampling_interval=128,best_failures=best,current_failures=current,restarts=restarts,accepted=accepted,position_distance=distance,secs=round(now-start,3));next_report=now+10
    emit(event='result',status='budget',evaluations=evaluations,distinct_sampled=len(visited),sampling_interval=128,best_failures=best,restarts=restarts,accepted=accepted,secs=round(time.monotonic()-start,3))

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='calibrate':
        small=[tuple(x) for x in json.load(open(S/'optimal8.json'))['comparators']]
        broken=small.copy();broken[4]=(0,7)
        assert score(broken,states(broken,8),0)>0
        run(10,8,[broken],'cal_repair8',31001,True)
    else:
        small=[tuple(x) for x in json.load(open(S/'optimal8.json'))['comparators']]
        damaged=small.copy();damaged[4]=(0,7)
        run(10,8,[damaged],'cal_repair8_live',31001)
        restored=[tuple(x) for x in json.load(open(S/'cal_repair8_live.best.json'))['comparators']]
        assert len(restored)==19 and score(restored,states(restored,8),0)==0
        emit(event='live_repair_calibration',status='PASS',n=8,size=19)
        baseline=[tuple(x) for x in json.load(open(S/'baseline.json'))['comparators']]
        assert score(baseline,states(baseline,18),0)==0
        broken=baseline[:33]+baseline[34:]
        assert score(broken,states(broken,18),0)==63
        emit(event='checker_control',baseline_failures=0,broken76_failures=63)
        starts=[];counts=[]
        for name in ['baseline','round1']:
            g=[tuple(x) for x in json.load(open(S/(name+'.json')))['comparators']]
            choices=[]
            for pos in range(len(g)):
                c=g[:pos]+g[pos+1:];v=score(c,states(c,18),0);choices.append((v,pos,c))
            choices.sort(key=lambda x:(x[0],x[1]));counts.append({'start':name,'deletion_scores':[(v,p) for v,p,c in choices]})
            starts.extend(c for _,_,c in choices[:8])
        emit(event='deletion_census',data=counts)
        extra=[]
        for f in S.glob('sat_*.candidate.json.near.json'):
            candidate=[tuple(x) for x in json.load(open(f))['comparators']]
            if len(candidate)!=76:continue
            value=score(candidate,states(candidate,18),0)
            extra.append((value,f.name,candidate))
        extra.sort(key=lambda x:(x[0],x[1]))
        emit(event='SAT_near_candidates',best=[(value,name) for value,name,c in extra[:8]])
        starts.extend(c for value,name,c in extra[:8] if value<63)
        run(float(sys.argv[1]),18,starts,'repair76',32003)
