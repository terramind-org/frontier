from collections import Counter
import hashlib
import random
import sys
from searchlib import *
import cubes
import repair

def caps(deadline, seconds):
    return min(seconds,max(1,deadline-time.time()-5))

def running(deadline):
    return time.time()<deadline-8 and not Path("STOP").exists()

def pivot(n, base, m, mirror=True, prefix=None):
    prefix=min(len(base),m) if prefix is None else min(prefix,m)
    job=rowley(n,base[:prefix],mirror)
    job["fixed"].pop(prefix+1)
    job["fixed"][m+1]=6
    job["masks"]={x:63 for x in range(prefix+1,m+1)}
    return job

def windows(n, colors, middle, top):
    mid=(len(colors)+1)//2
    lo,hi=mid-middle//2, mid+(middle+1)//2
    return dict(n=n,k=7,fixed={x:c for x,c in enumerate(colors,1)
                             if x<=n and not (lo<=x<hi or x>len(colors)-top)})

def call(job,name,deadline,seconds,proof=False):
    if not running(deadline):
        return {"status":"PENDING"}
    suffix=hashlib.sha256(name.encode()).digest()
    output=solve(job,"push-"+name,int.from_bytes(suffix[:3],"big"),caps(deadline,seconds),proof=proof)
    if output["status"]=="SAT" and job["n"]>=1699:
        print(f"{utc()} accepted candidate N={job['n']} file={output['solution']}",flush=True)
    return output

def extend(found, start, label, deadline):
    current=found
    for n in range(start,min(1800,start+20)):
        if not running(deadline):
            break
        improved=None
        for width in ((128,128),(300,300),(500,400),(800,600)):
            w,t=width
            status=call(windows(n,current,w,t),f"{label}-extended-{n}-{w}-{t}",deadline,300)
            if status["status"]=="SAT":
                improved=solution(status)
                break
        if improved is None:
            break
        current=improved

def seeded(deadline):
    inputs=[Path("inputs")/f for f in ("N1698_b1_0014_sym.json",
                                      "p4_0001_N1698.json",
                                      "longq_calib_sym1698_F150_m300.json")]
    for i,p in enumerate(inputs):
        colors=read(p)["colors"]
        assert len(colors)==1698 and valid(colors,7)
        for n in (1699,1700):
            for w,t in ((16,16),(64,64),(144,96),(288,192),(448,360)):
                if not running(deadline):
                    return
                control=call(windows(1698,colors,w,t),f"seed-{i}-control-{w}-{t}",deadline,45)
                if control["status"]!="SAT":
                    continue
                proof=n==1699 and i in (0,2) and (w,t)==(288,192)
                outcome=call(windows(n,colors,w,t),f"seed-{i}-window-{n}-{w}-{t}",deadline,120,proof)
                if outcome["status"]=="SAT":
                    extend(solution(outcome),n+1,f"seed-{i}-{w}-{t}",deadline)
        for n in (1699,1700,1701,1702):
            if not running(deadline):
                return
            for m in (536,530,533,535,537,540,545):
                outcome=call(pivot(n,colors[:536],m),f"seed-{i}-pivot-{n}-{m}",deadline,25,
                             proof=(i==0 and n==1699 and m==536))
                if outcome["status"]=="SAT":
                    extend(solution(outcome),n+1,f"seed-{i}-pivot-{m}",deadline)
    for i,p in enumerate(inputs):
        colors=read(p)["colors"]
        base=colors[:536]
        control=call(rowley(1698,base,False),f"seed-{i}-plain-control-1698",deadline,240)
        if control["status"] not in ("SAT","TIMEOUT"):
            print(f"{utc()} unmirrored comparator {i} {control['status']}",flush=True)
        for n in (1699,1700):
            outcome=call(rowley(n,base,False),f"seed-{i}-plain-{n}",deadline,1200)
            if outcome["status"]=="SAT":
                extend(solution(outcome),n+1,f"seed-{i}-plain",deadline)
    for n in (1699,1701,1702):
        for cut in (500,420,360,280,200,150):
            base=read(inputs[(cut//10)%3])["colors"][:536]
            for m in (536,534,538):
                if not running(deadline):
                    return
                # Long retries focus on fewer fixed base colors while still
                # retaining the six-colour and pivot constraints.
                limit=1800 if m==536 and cut in (420,360,280) and n==1699 else 90
                if m==536 and cut==150 and n==1699:
                    limit=3600
                outcome=call(pivot(n,base,m,prefix=cut),f"soft-{n}-{m}-{cut}",deadline,limit)
                if outcome["status"]=="SAT":
                    extend(solution(outcome),n+1,f"soft-{m}-{cut}",deadline)

def discovery(name, colors, deadline):
    label=name[5:-5]
    base=colors[:536]
    seed=int(label[:8],16)
    rng=random.Random(seed)
    n=1699
    for m in (rng.choice((530,531,532,533,534,535)),rng.choice(tuple(range(537,546)))):
        status=call(pivot(n,base,m),f"new-{label}-pivot-{n}-{m}",deadline,8)
        if status["status"]=="SAT":
            extend(solution(status),n+1,f"new-{label}-{m}",deadline)
    for n in (1699,1700):
        for w,t in ((64,48),(160,144)):
            outcome=call(windows(n,colors,w,t),f"new-{label}-window-{n}-{w}-{t}",deadline,12)
            if outcome["status"]=="SAT":
                extend(solution(outcome),n+1,f"new-{label}-{w}-{t}",deadline)

def flex(deadline):
    samples=[read("inputs/"+f)["colors"] for f in (
        "N1698_b1_0014_sym.json","p4_0001_N1698.json","longq_calib_sym1698_F150_m300.json")]
    candidates=[]
    for n in (1699,1700):
        for w,t in ((608,500),(704,620),(800,700),(900,720)):
            for i,colors in enumerate(samples):
                name=f"broad-{i}-window-{n}-{w}-{t}"
                candidates.append((windows(n,colors,w,t),name,300))
    for i,n,f,limit in ((0,1699,350,1800),(1,1699,250,3600),(2,1700,350,1800),
                        (2,1699,200,1800),(0,1700,250,1800)):
        job={"n":n,"k":7,"fixed":dict(enumerate(samples[i][:f],1))}
        candidates.append((job,f"broad-{i}-prefix-{n}-{f}",limit))
    for job,name,seconds in candidates:
        if running(deadline) and not archive.exists("job","push-"+name):
            outcome=call(job,name,deadline,seconds)
            if outcome["status"]=="SAT":
                extend(solution(outcome),job["n"]+1,name,deadline)
            return

def run(deadline,cube_start):
    seeded(deadline)
    while running(deadline):
        if Path("side-ready").exists() and time.time()>cube_start:
            cubes.run_slice(0,deadline,430)
            if Path("repair-ready").exists():
                result=repair.job_slice(deadline,call)
                if result and result["status"]=="SAT":
                    extend(solution(result),1700,result["name"],deadline)
            flex(deadline)
        candidates=list(archive.select("solution",prefix="base-",n=1698,order="RANDOM()",limit=128))
        bins={}
        for name,record in candidates:
            if archive.exists("pushed",name):
                continue
            base=archive.get("base",name[5:-5])
            bins.setdefault(base["features"]["distance_anchor"]//5,[]).append((name,record))
        if not bins:
            time.sleep(2)
            continue
        for _,group in sorted(bins.items(),reverse=True):
            if not running(deadline):
                break
            name,record=group[0]
            discovery(name,record["colors"],deadline)
            if running(deadline):
                archive.store("pushed",name,{"utc":utc()})

if __name__=="__main__":
    run(float(sys.argv[1]),float(sys.argv[2]))
