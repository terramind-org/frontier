"""Two single-core lanes share a fixed 7200-second wall deadline, including controls."""
import pathlib,importlib.util,json,time,subprocess,random,sys,datetime,resource
S=pathlib.Path(__file__).resolve().parent

def module(name):
    spec=importlib.util.spec_from_file_location(name,S/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
h=module('hunter')
def emit(**x):print(json.dumps(dict(utc=h.utc(),**x)),flush=True)
def bounded(cmd,seconds,logname):
    start=time.time()
    with open(S/(logname+'.log'),'w') as f:
        p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,preexec_fn=h.restrict)
        emit(event='child_start',name=logname,pid=p.pid,seconds=seconds)
        try:
            end=start+seconds; peak_rss=0
            while True:
                try:code=p.wait(timeout=min(5,max(0.01,end-time.time())));termination='exited';break
                except subprocess.TimeoutExpired:
                    rss=subprocess.run(['ps','-o','rss=','-p',str(p.pid)],capture_output=True,text=True).stdout.strip()
                    if rss:
                        peak_rss=max(peak_rss,int(rss))
                        if int(rss)>1300000:
                            p.terminate();code=p.wait(timeout=5);termination='memory_cap';break
                    if time.time()>=end:raise
        except subprocess.TimeoutExpired:
            p.terminate()
            try:code=p.wait(timeout=5)
            except subprocess.TimeoutExpired:p.kill();code=p.wait()
            termination='deadline'
    out=dict(event='child_end',name=logname,pid=p.pid,start_epoch=start,end_epoch=time.time(),returncode=code,termination=termination,peak_rss_kib_sampled=peak_rss)
    (S/(logname+'.exit.json')).write_text(json.dumps(out));emit(**out)
    return code

def reordered(gates,seed):
    rng=random.Random(seed);gates=gates.copy()
    # Adjacent disjoint comparators commute exactly on every input.
    for _ in range(10000):
        k=rng.randrange(len(gates)-1)
        if set(gates[k]).isdisjoint(gates[k+1]):gates[k],gates[k+1]=gates[k+1],gates[k]
    return gates

budget=json.load(open(S/'budget.json'));deadline=budget['deadline_epoch'];mode=sys.argv[1]
emit(event='lane_start',mode=mode,deadline_epoch=deadline)
if mode=='hunter':
    w=module('window');jobs=[]
    for seed_round in range(2):
        for startname in ['baseline','round1','depth11']:
            gates=[tuple(x) for x in json.load(open(S/(startname+'.json')))['comparators']]
            for sym in [True,False]:
                for layers in [0,1,2]:jobs.append((seed_round,startname,gates,sym,layers))
    for k,(roundno,startname,gates,sym,layers) in enumerate(jobs):
        left=deadline-time.time()
        if left<2:break
        name=f'hunt_{k:02d}_{startname}_s{int(sym)}_p{layers}'
        seed=18001+k*101;escape=[300,1000,5000][k%3];mutations=[1,2,4][(k//3)%3]
        cfg=h.config(gates,18,sym,layers,seed,escape,mutations,name)
        # Independently test literal prefix + expanded mutable core from serialized cfg.
        import re
        rows=cfg.read_text().splitlines()
        parse=lambda key:[tuple(map(int,x)) for x in re.findall(r'\((\d+),(\d+)\)',next(r for r in rows if r.startswith(key+'=')))]
        pre=parse('FixedPrefix');core=parse('InitialNetwork');expanded=[]
        for i,j in core:
            expanded.append((i,j))
            if sym and i+j!=17:expanded.append((17-j,17-i))
        start=pre+expanded
        bad=len(w.failures(w.apply(w.inputs(18),start)))
        emit(event='initial_control',name=name,seed=seed,escape=escape,mutations=mutations,size=len(start),failures=bad)
        if len(start)!=len(gates) or bad:
            emit(event='skipped_invalid_compression',name=name);continue
        seconds=max(1,(deadline-time.time()-1)/(len(jobs)-k))
        h.run(cfg,seconds,name,expected=len(gates))
elif mode=='sat':
    jobs=[]
    for startname in ['baseline','round1']:
        g=[tuple(x) for x in json.load(open(S/(startname+'.json')))['comparators']]
        for order in range(3):
            net=g if order==0 else reordered(g,27000+order)
            name=f'{startname}_order{order}'
            (S/(name+'.json')).write_text(json.dumps({'comparators':net}))
            # Diverse earlier windows first, including sizes 11 through 14.
            for width in [11,12,13,14]:
                for offset in [17,25,33,41,9,0]:jobs.append((name,offset,width))
    rng=random.Random(27182);rng.shuffle(jobs)
    sat_end=min(deadline,budget['start_epoch']+5400)
    for k,(startname,offset,width) in enumerate(jobs):
        left=sat_end-time.time()
        if left<5:break
        name=f'sat_{k:03d}_{startname}_s{offset}_w{width}'
        seconds=min(110,max(20,left))
        code=bounded([str(S/'.venv/bin/python'),'-I','-u',str(S/'window.py'),str(S/(startname+'.json')),'18',str(offset),str(width),str(width-1),str(seconds),str(28000+k),str(S/(name+'.candidate.json'))],seconds+10,name)
        candidate=S/(name+'.candidate.json')
        if candidate.exists():
            r=subprocess.run(['bun','frontier','diagnose',str(candidate.relative_to(pathlib.Path.cwd())),'--problem','witness.sorting-network-size-18'],capture_output=True,text=True)
            (S/(name+'.diagnose.log')).write_text(r.stdout+r.stderr);emit(event='candidate_diagnose',name=name,stdout=r.stdout)
    left=deadline-time.time()-1
    if left>10:bounded([str(S/'.venv/bin/python'),'-I','-u',str(S/'repair.py'),str(left)],left+1,'repair')
emit(event='lane_end',mode=mode)
