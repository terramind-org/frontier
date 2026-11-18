import random
import sys
from searchlib import *
import cubes

def local(n,k,start,tag,seed,seconds):
    old=archive.get("local",tag)
    if old is not None:
        return old
    req=Path("tmp")/(tag+".txt")
    out=Path("tmp")/(tag+".json")
    req.write_text(f"{n} {k}\n"+" ".join(map(str,start))+"\n")
    began=time.time()
    result={"utc_start":utc(),"seed":seed,"n":n,"k":k,"start":start,"limit":seconds}
    run=subprocess.run(["bin/breakout",str(req),str(out),str(seed),str(seconds),"10000000000"],
                       text=True,capture_output=True,timeout=seconds+10)
    best=read(out)["colors"]
    count=len(triples(best))
    result.update(utc_end=utc(),seconds=round(time.time()-began,3),rc=run.returncode,
                  output=run.stdout,stderr=run.stderr,best=count)
    if run.returncode not in (0,10) or count!=int(run.stdout.splitlines()[-1].split()[2]):
        raise RuntimeError(result)
    if n>=1699 and valid(best,7):
        p=Path("solutions")/(tag+".json")
        certified(best,p)
        archive.store("solution",tag,{"colors":best})
        print(f"{utc()} accepted config {tag} N={n}",flush=True)
    archive.store("local",tag,{**result,"best_colors":best})
    out.unlink()
    req.unlink()
    return result

def run(deadline):
    seeds=[read("inputs/"+f)["colors"] for f in (
        "N1698_b1_0014_sym.json","p4_0001_N1698.json","longq_calib_sym1698_F150_m300.json")]
    for i in range(10**7):
        if time.time()>deadline-8 or Path("STOP").exists():
            break
        tag=f"local-1699-{i:05d}"
        if archive.exists("local",tag):
            continue
        seed=634512+i
        rng=random.Random(seed)
        if i%6<3:
            original=seeds[i%3]
        else:
            sample=list(archive.select("solution",prefix="base-",n=1698,order="RANDOM()",limit=3))
            original=rng.choice(sample)[1]["colors"] if sample else seeds[i%3]
        choices=[len(triples([*original,c])) for c in range(7)]
        c=choices.index(min(choices)) if i%7<5 else rng.randrange(7)
        start=[*original,c]
        for x in rng.sample(range(1698),rng.choice((0,0,0,2,5))):
            start[x]=rng.randrange(7)
        result=local(1699,7,start,tag,seed,int(min(120,max(1,deadline-time.time()-6))))
        print(f"{utc()} {tag} min_conflicts={result['best']} rc={result['rc']}",flush=True)
        cubes.run_slice(1,deadline,430)

if __name__=="__main__":
    if sys.argv[1]=="calibrate":
        known=archive.get("solution","calib-canonical-44")["colors"]
        original=known[:43]+[(known[-1]+1)%4]
        assert triples(original)
        r=local(44,4,original,"calib-local-44",1994,15)
        assert r["best"]==0,r
        print("breakout repaired planted length 44",r["output"])
    else:
        run(float(sys.argv[1]))
