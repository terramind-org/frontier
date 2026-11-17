"""Bounded SorterHunter wrapper: immutable configs, timestamped lines, saved objects, exits."""
import json,pathlib,subprocess,time,datetime,selectors,ast,sys,resource
S=pathlib.Path(__file__).resolve().parent

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def restrict():
    resource.setrlimit(resource.RLIMIT_CPU,(7300,7300))

def config(gates,n,symmetric,prefix_layers,seed,escape,mutations,name):
    # Earliest ASAP layers; a prefix is a downward-closed set of wire dependencies.
    depths=[0]*n;annotated=[]
    for i,j in gates:
        d=max(depths[i],depths[j])+1;depths[i]=depths[j]=d;annotated.append(d)
    prefix=[g for g,d in zip(gates,annotated) if d<=prefix_layers]
    core=[g for g,d in zip(gates,annotated) if d>prefix_layers]
    if symmetric:core=[g for g in core if sum(g)<=n-1]
    pairs=lambda gs:','.join(f'({i},{j})' for i,j in gs)
    cfg=f'''Ninputs={n}
Symmetric={int(symmetric)}
PrefixType=1
FixedPrefix={pairs(prefix)}
InitialNetwork={pairs(core)}
RandomSeed={seed}
EscapeRate={escape}
MaxMutations={mutations}
WeigthRemovePair=1
WeigthSwapPairs=1
WeigthReplacePair=1
WeightCrossPairs=1
WeightSwapIntersectingPairs=2
WeightReplaceHalfPair=1
RestartRate=0
Verbosity=3
'''
    path=S/(name+'.cfg');path.write_text(cfg);return path

def run(cfg,seconds,name,expected=None,calibration_target=None):
    start=time.time();deadline=start+seconds;seen=set();best=10000;initials=[];reached=False
    p=subprocess.Popen([str(S/'SorterHunter'),str(cfg)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,preexec_fn=restrict)
    meta={'event':'start','utc':utc(),'pid':p.pid,'name':name,'seconds':seconds,'config':cfg.name}
    with open(S/(name+'.log'),'w') as log:
        log.write(json.dumps(meta)+'\n');log.flush()
        sel=selectors.DefaultSelector();sel.register(p.stdout,selectors.EVENT_READ)
        last_rss=0;peak_rss=0
        while time.time()<deadline and p.poll() is None:
            if time.time()-last_rss>5:
                last_rss=time.time()
                rss=subprocess.run(['ps','-o','rss=','-p',str(p.pid)],capture_output=True,text=True).stdout.strip()
                if rss:
                    peak_rss=max(peak_rss,int(rss))
                    if int(rss)>1300000:p.terminate();raise RuntimeError('RSS memory cap')
            for key,_ in sel.select(timeout=min(1,max(0,deadline-time.time()))):
                line=key.fileobj.readline()
                if not line:continue
                log.write(utc()+' '+line);log.flush()
                if 'Initial network size:' in line:
                    value=int(line.split(':')[-1]);initials.append(value)
                    if expected is not None and value!=expected:
                        p.terminate();raise RuntimeError(f'{name}: initial size {value}, expected {expected}')
                if "'nw':" in line:
                    x=ast.literal_eval(line.strip());nw=x['nw'];key=tuple(nw);seen.add(key)
                    if len(nw)<best:
                        best=len(nw);(S/(name+'.best.json')).write_text(json.dumps({'comparators':nw}))
                    if len(nw)<77 and len(nw)>19:
                        candidate=S/(name+'.candidate.json');candidate.write_text(json.dumps({'comparators':nw}))
                        result=subprocess.run(['bun','frontier','diagnose',str(candidate.relative_to(pathlib.Path.cwd())),'--problem','witness.sorting-network-size-18'],capture_output=True,text=True)
                        log.write(utc()+' DIAGNOSE '+result.stdout+'\n');log.flush()
                    if calibration_target is not None and best<=calibration_target:
                        reached=True;p.terminate()
        if p.poll() is None:p.terminate()
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:p.kill();p.wait()
        # Drain final pipe bytes without losing buffered lines.
        for line in p.stdout:log.write(utc()+' '+line)
        summary={'event':'end','utc':utc(),'name':name,'start_epoch':start,'end_epoch':time.time(),'returncode':p.returncode,'initials':initials,'best_printed':best,'distinct_printed_networks':len(seen),'calibration_reached':reached,'peak_rss_kib_sampled':peak_rss}
        log.write(json.dumps(summary)+'\n')
    (S/(name+'.summary.json')).write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary),flush=True)
    return summary

if __name__=='__main__':
    cfg,sec,name=sys.argv[1:4];run(pathlib.Path(cfg),float(sec),name)
