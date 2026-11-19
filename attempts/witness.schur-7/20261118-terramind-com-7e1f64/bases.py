import hashlib
import random
import sys
from pysat.solvers import Cadical195
from searchlib import *

def features(colors, row, anchor):
    groups = [[i for i,c in enumerate(colors,1) if c==g] for g in range(6)]
    gaps = [[b-a for a,b in zip(group,group[1:])] for group in groups]
    return {"sizes":list(map(len,groups)), "small":colors[:32],
            "max_gaps":[max(g,default=0) for g in gaps],
            "median_gaps":[sorted(g)[len(g)//2] if g else 0 for g in gaps],
            "distance_rowley":sum(a!=b for a,b in zip(colors,row)),
            "distance_anchor":sum(a!=b for a,b in zip(colors,anchor))}

def key(colors):
    return hashlib.sha256(bytes(colors)).hexdigest()

def legal_moves(colors):
    groups = [[i for i,c in enumerate(colors,1) if c==g] for g in range(6)]
    length = len(colors)
    blocked = [set() for _ in groups]
    for g, group in enumerate(groups):
        banned = blocked[g]
        for i,x in enumerate(group):
            if 2*x <= length:
                banned.add(2*x)
            if x%2 == 0:
                banned.add(x//2)
            for y in group[i+1:]:
                banned.add(y-x)
                if x+y <= length:
                    banned.add(x+y)
    return [(i,g) for i,c in enumerate(colors,1) for g in range(6) if c!=g and i not in blocked[g]]

def allowed_near(source, rng, recipe, i):
    if recipe == "window":
        width = rng.choice((8,16,32,60,120,240,400))
        start = rng.randrange(1,538-width)
        free = range(start,start+width)
    elif recipe == "prefix":
        prefix = rng.choice((200,300,380,420,450,480,500,520))
        free = range(prefix+1,537)
    elif recipe == "sparse":
        free = rng.sample(range(1,537),rng.choice((24,48,100,160,260,390)))
    else:
        free = range(1,537)
    fixed = {1:source[0],2:source[1]}
    fixed.update({x:source[x-1] for x in range(1,537) if x not in free})
    return fixed, tuple(free)

def xlit(x,c,k=6):
    return (x-1)*k+c+1

def load_generator(worker):
    cnf = Path(f"tmp/generator-{worker}.cnf")
    req = cnf.with_suffix(".txt")
    encode(dict(n=536,k=6),req,cnf)
    sat = Cadical195()
    with cnf.open() as f:
        next(f)
        for line in f:
            sat.add_clause([int(x) for x in line.split()[:-1]])
    req.unlink()
    cnf.unlink()
    return sat

def gen_with_sat(sat, name, source, rng, recipe, attempt):
    fixed, free = allowed_near(source,rng,recipe,attempt)
    assumptions=[xlit(x,c) for x,c in fixed.items()]
    noise=rng.choice((.03,.10,.25,.60,1.0))
    phase=[xlit(x, source[x-1] if rng.random() >= noise else rng.randrange(6))
           for x in range(1,537)]
    return generation_call(sat,name,source,fixed,assumptions,phase,noise,recipe,attempt,len(free))

def generation_call(sat,name,source,fixed,assumptions,phase,noise,recipe,attempt,free_count):
    start=time.time()
    start_utc=utc()
    before=sat.accum_stats()
    sat.set_phases(phase)
    budget=4000 if recipe!="wide" else 18000
    sat.conf_budget(budget)
    result=sat.solve_limited(assumptions=assumptions)
    after=sat.accum_stats()
    stat=dict(utc_start=start_utc, utc_end=utc(), seed=attempt, source=name,
              status={True:"SAT",False:"UNSAT",None:"BUDGET"}[result],
              rc=0, conflicts=after["conflicts"]-before["conflicts"],
              decisions=after["decisions"]-before["decisions"],
              seconds=round(time.time()-start,3), fixed=fixed, phase=phase,
              noise=noise, recipe=recipe, free_count=free_count, conflict_budget=budget)
    if result:
        positive={lit for lit in sat.get_model() if lit>0}
        cols=decode(dict(n=536,k=6,fixed=fixed),positive)
        sat.add_clause([-xlit(x,c) for x,c in enumerate(cols,1)])
        return cols,stat
    return None,stat

def register(colors, source, recipe, worker, attempt, row, anchor, moves):
    if not valid(colors,6):
        raise ValueError("generator produced invalid base")
    digest=key(colors)
    record=dict(colors=colors,key=digest,source=source,recipe=recipe,worker=worker,
                attempt=attempt,utc=utc(),moves=moves,features=features(colors,row,anchor))
    return digest,archive.store("base",digest,record,unique=True)

def probe(digest, colors, deadline):
    n1696=solve(rowley(1696,colors), f"base-{digest}-1696", 846005,min(10,max(1,deadline-time.time()-5)))
    if n1696["status"]=="SAT" and time.time()<deadline-8:
        tag=f"base-{digest}-1698"
        had=archive.exists("job",tag)
        n1698=solve(rowley(1698,colors), tag, 846005,min(20,max(1,deadline-time.time()-5)))
        if n1698["status"]=="SAT":
            if not had:
                print(f"{utc()} accepted completion base={digest} N=1698",flush=True)
            if Path("variant-ready").exists() and time.time()<deadline-10:
                from variants import batch, unmirrored_batch
                batch(colors,digest,deadline)
                if Path("quickwin-ready").exists():
                    unmirrored_batch(solution(n1698),digest)
            m=536
            for n in (1699,1700,1701,1702):
                if time.time()>deadline-8:
                    break
                solve(rowley(n,colors[:m]),f"base-{digest}-{n}",846005,
                      min(15,max(1,deadline-time.time()-5)))
    return n1696["status"]

def run(worker, deadline):
    row=read("baseline.json")["colors"][:536]
    anchor=read("inputs/base14.json")["colors"]
    sat=load_generator(worker)
    sources={"rowley":row,"anchor":anchor}
    for colors in sources.values():
        sat.add_clause([-xlit(x,c) for x,c in enumerate(colors,1)])
    history=list(archive.select("generation",prefix=f"{worker}:",worker=worker,order="key DESC",limit=1))
    first=int(history[0][0].split(":")[1])+1 if history else 0
    # Restore blockers and finish any probe interrupted before its checkpoint.
    for whose,record in list(archive.select("base",worker=worker)):
        if time.time()<deadline-8:
            probe(whose,record["colors"],deadline)
            sat.add_clause([-xlit(x,c) for x,c in enumerate(record["colors"],1)])
    targeted=None
    for i in range(first,10**8):
        if time.time()>deadline-8 or Path("STOP").exists():
            break
        if worker==2 and i%3==1 and Path("core-ready").exists():
            if targeted is None:
                from core_search import Targeted
                targeted=Targeted(deadline)
            targeted.step(i)
            continue
        seed=857200000+worker*10000000+i
        rng=random.Random(seed)
        if i%16==0:
            sampled=archive.select("solution",prefix="base-",n=1698,order="RANDOM()",limit=96)
            sources={"rowley":row,"anchor":anchor}
            for name,rec in sampled:
                sources[name[5:-5]]=rec["colors"][:536]
        # Focus on the matched control and new productive bases, with Rowley
        # and diverse earlier six-colour partitions as exploration starts.
        prior_files=sorted(Path("inputs").glob("b1_00*.json"))
        choice=rng.random()
        if choice<0.57:
            name, source=rng.choice([(a,b) for a,b in sources.items() if a!="rowley"])
        elif choice<0.77 or not prior_files:
            name, source="rowley",row
        else:
            path=rng.choice(prior_files)
            name,source=path.stem,read(path)["colors"]
        recipe=rng.choice(("window","prefix","sparse","wide","local","local","local"))
        new=None
        if worker==1:
            recipe=rng.choice(("local","local","local","window","sparse"))
        elif worker==2:
            recipe=rng.choice(("wide","window","prefix","sparse","joint"))
        if recipe=="local":
            cols=source.copy()
            moves=[]
            for _ in range(rng.choice((1,1,2,3,5,8))):
                options=legal_moves(cols)
                if not options:
                    break
                x,c=rng.choice(options)
                cols[x-1]=c
                moves.append((x,c))
            stamp=utc()
            stat={"source":name,"recipe":recipe,"status":"CANDIDATE","utc_start":stamp,"utc_end":stamp,"seed":seed}
        elif recipe=="joint":
            control=read("baseline.json")["colors"]
            if name!="rowley":
                if name=="anchor":
                    k="anchor-1696"
                    solve(rowley(1696,anchor),k,259416,15)
                else:
                    k=f"base-{name}-1696"
                success=archive.get("solution",k)
                if success:
                    control=success["colors"]
            retained,_=allowed_near(control,rng,rng.choice(("window","prefix","sparse","wide")),i)
            # Force a change at one freed base position before completing.
            x=rng.choice([x for x in range(3,537) if x not in retained])
            job=rowley(1696,control[:536])
            job["fixed"]={**retained,537:6}
            job["masks"]={a:63 if a!=x else 63^(1<<control[x-1]) for a in range(1,537) if a not in retained}
            stat=solve(job,f"joint-{worker}-{i}",seed,min(20,max(1,deadline-time.time()-5)))
            stat={**stat,"source":name,"recipe":recipe}
            cols=solution(stat)[:536] if stat["status"]=="SAT" else None
            moves=[]
        else:
            cols,stat=gen_with_sat(sat,name,source,rng,recipe,seed)
            moves=[]
        if cols is not None:
            digest,new=register(cols,name,recipe,worker,i,row,anchor,moves)
            stat.update(base=digest,distinct=new,moves=moves)
        stat["worker"]=worker
        archive.store("generation",f"{worker}:{i:07d}",stat)
        if cols is not None and new:
            probe(digest,cols,deadline)
        if i%100==0:
            print(f"{utc()} generator={worker} attempts={i+1}",flush=True)
    sat.delete()

if __name__=="__main__":
    run(int(sys.argv[1]),float(sys.argv[2]))
