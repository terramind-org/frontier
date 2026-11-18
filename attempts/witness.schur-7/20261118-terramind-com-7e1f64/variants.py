import random
from searchlib import *

def query(requests):
    data=[str(len(requests))]
    for n,k,fixed,allowed,mirror in requests:
        data.append(f"{n} {k} {len(fixed)+len(allowed)} {int(mirror)}")
        data.extend(f"{x} {1<<c}" for x,c in fixed.items())
        data.extend(f"{x} {mask}" for x,mask in allowed.items())
    started=utc()
    proc=subprocess.run([os.environ.get("SCHUR_PROPAGATE_BIN","bin/propagate")],input="\n".join(data)+"\n",text=True,capture_output=True,timeout=20)
    if proc.returncode!=0:
        raise RuntimeError((proc.returncode,proc.stderr))
    lines=proc.stdout.splitlines()
    if len(lines)!=len(requests):
        raise ValueError("Incomplete output from propagation batch")
    out=[]
    for line,(n,k,fixed,allowed,mirror) in zip(lines,requests):
        status,assigned,position,*colors=map(int,line.split())
        status={10:"SAT",20:"UNSAT",0:"OPEN"}[status]
        row=dict(status=status,assigned=assigned,contradiction_at=position,rc=proc.returncode,
                 utc_start=started,utc_end=utc())
        if status=="SAT":
            job=dict(n=n,k=k,fixed=fixed,masks=allowed,mirror=rowley(n,[])["mirror"] if mirror else [])
            positive={(r-1)*k+c+1 for r,c in zip(reps(n,job["mirror"])[1:],colors)}
            assert len(colors)==n and colors==decode(job,positive)
            row["colors"]=colors
        out.append(row)
    return out

def batch(base,digest,deadline):
    tag="variant-"+digest
    memo=archive.get("variant",tag)
    if memo is not None:
        return memo
    requests=[]
    for n in (1699,1700,1701,1702):
        for m in range(530,546):
            fixed=dict(enumerate(base[:m],1))
            fixed[m+1]=6
            masks={x:63 for x in range(len(base)+1,m+1)}
            requests.append((n,7,fixed,masks,True))
    rows=query(requests)
    res=[]
    for i,(r,(n,k,fixed,masks,mirror)) in enumerate(zip(rows,requests)):
        m=530+i%16
        name=f"{tag}-{n}-{m}"
        if r["status"]=="SAT":
            colors=r.pop("colors")
            output=Path("solutions")/f"{name}.json"
            certified(colors,output)
            archive.store("solution",name,{"colors":colors})
            r["solution"]=name
            print(f"{utc()} accepted variant N={n} m={m} base={digest}",flush=True)
        res.append([r["status"],r["assigned"],r["contradiction_at"]])
    checkpoint={"base":digest,"status_order":["n=1699..1702","m=530..545"],"results":res,
                "utc_start":rows[0]["utc_start"],"utc_end":rows[-1]["utc_end"],"rc":rows[0]["rc"]}
    archive.store("variant",tag,checkpoint)
    return checkpoint

WINDOWS=((32,32),(64,48),(160,144),(288,192))

def unmirrored_batch(colors, digest):
    tag="quickwin-"+digest
    prior=archive.get("quick-window",tag)
    if prior is not None:
        return prior
    requests=[]
    labels=[]
    mid=(len(colors)+1)//2
    for n in (1699,1700):
        for middle,top in WINDOWS:
            lo,hi=mid-middle//2,mid+(middle+1)//2
            fixed={x:c for x,c in enumerate(colors,1) if not (lo<=x<hi or x>len(colors)-top)}
            requests.append((n,7,fixed,{},False))
            labels.append((n,middle,top))
    rows=query(requests)
    results=[]
    for r,(n,middle,top) in zip(rows,labels):
        if r["status"]=="SAT":
            found=r.pop("colors")
            name=f"{tag}-{n}-{middle}-{top}"
            certified(found,Path("solutions")/f"{name}.json")
            archive.store("solution",name,{"colors":found})
            print(f"{utc()} accepted unmirrored window N={n} base={digest}",flush=True)
        results.append([n,middle,top,r["status"],r["assigned"],r["contradiction_at"]])
    out=dict(base=digest,res=results,utc_start=rows[0]["utc_start"],utc_end=rows[-1]["utc_end"],rc=rows[0]["rc"])
    archive.store("quick-window",tag,out)
    return out

def calibrate():
    original=read("baseline.json")["colors"]
    near=read("inputs/base14.json")["colors"]
    verified=[]
    for n,base in ((1696,original[:536]),(1698,near)):
        fixed=dict(enumerate([*base,6],1))
        result=query([(n,7,fixed,{},True)])[0]
        assert result["status"]!="UNSAT",result
        verified.append((n,result["status"]))
    rng=random.Random(4095)
    for i in range(30):
        n=rng.randrange(4,15)
        k=rng.choice((2,3,4))
        fixed={x:rng.randrange(k) for x in rng.sample(range(1,n+1),rng.randrange(0,min(5,n)))}
        masks={x:rng.randrange(1,1<<k) for x in rng.sample(range(1,n+1),rng.randrange(0,min(5,n)))}
        mirror=bool(i%2)
        r=query([(n,k,fixed,masks,mirror)])[0]
        if r["status"]=="OPEN":
            continue
        ctrl=solve(dict(n=n,k=k,fixed=fixed,masks=masks,mirror=rowley(n,[])["mirror"] if mirror else []),
                   f"calib-both-variant-{i}",1045,15)
        assert r["status"]==ctrl["status"],(r,ctrl)
        verified.append((n,r["status"]))
    print(verified)

if __name__=="__main__":
    calibrate()
