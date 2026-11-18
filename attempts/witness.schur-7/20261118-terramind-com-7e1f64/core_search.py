import random

from pysat.solvers import Cadical195

from searchlib import *

def solver_for(job, name):
    cnf=Path("tmp")/f"{name}.cnf"
    request=cnf.with_suffix(".txt")
    encode(job,request,cnf)
    sat=Cadical195()
    with cnf.open() as f:
        next(f)
        for line in f:
            sat.add_clause([int(x) for x in line.split()[:-1]])
    request.unlink()
    cnf.unlink()
    return sat

class Oracle:
    def __init__(self,n,m):
        self.n,self.m=n,m
        self.job=rowley(n,[0]*m)
        self.job["fixed"]={m+1:6}
        self.job["masks"]={x:63 for x in range(1,m+1)}
        self.sat=solver_for(self.job,f"oracle-{n}-{m}")
        self.representative=reps(n,self.job["mirror"])
        assert all(self.representative[x]==x for x in range(1,m+1))

    def ask(self,base,name,budget=3500):
        prior=archive.get("oracle",name)
        if prior is not None:
            return prior
        assumptions=[(x-1)*7+c+1 for x,c in enumerate(base,1)]
        before=self.sat.accum_stats()
        start=time.time()
        utc_start=utc()
        self.sat.conf_budget(budget)
        result=self.sat.solve_limited(assumptions=assumptions)
        after=self.sat.accum_stats()
        out=dict(n=self.n,m=self.m,utc_start=utc_start,utc_end=utc(),budget=budget,
                 seconds=round(time.time()-start,3),rc=0,assumptions=assumptions,
                 status={True:"SAT",False:"UNSAT",None:"BUDGET"}[result],
                 conflicts=after["conflicts"]-before["conflicts"],
                 decisions=after["decisions"]-before["decisions"])
        if result is False:
            failed=self.sat.get_core()
            if failed is None:
                # An immediate unrestricted contradiction is an empty core.
                failed=[]
            if not set(failed).issubset(assumptions):
                raise ValueError("Unexpected failed assumptions")
            out["core"]=sorted(failed)
        elif result is True:
            positive={lit for lit in self.sat.get_model() if lit>0}
            job={**self.job,"fixed":{**self.job["fixed"],**dict(enumerate(base,1))}}
            colors=decode(job,positive)
            output=Path("solutions")/f"{name}.json"
            certified(colors,output)
            archive.store("solution",name,{"colors":colors})
            out["solution"]=name
            print(f"{utc()} accepted oracle N={self.n} job={name}",flush=True)
        archive.store("oracle",name,out)
        return out

def block(out,sat):
    if out["status"]=="UNSAT":
        clause=[-(((lit-1)//7)*6+(lit-1)%7+1) for lit in out["core"]]
        sat.add_clause(clause)
        return len(clause)
    return None

class Targeted:
    def __init__(self,deadline):
        from bases import legal_moves, xlit
        self.deadline=deadline
        self.name="core1699-536"
        self.oracle=Oracle(1699,536)
        self.gen=solver_for(dict(n=536,k=6),"targeted-generator")
        self.anchor=read("inputs/base14.json")["colors"]
        self.row=read("baseline.json")["colors"][:536]
        self.fixes={1:self.anchor[0],2:self.anchor[1]}
        self.disabled=False
        for _,out in archive.select("oracle",prefix=self.name):
            if block(out,self.gen)==0:
                self.disabled=True
        for x in (self.anchor,self.row):
            self.gen.add_clause([-xlit(i,c) for i,c in enumerate(x,1)])

    def step(self,i):
        from bases import xlit, gen_with_sat, register, probe, key
        seed=851780000+i
        rng=random.Random(seed)
        tag=f"{self.name}-{i:07d}"
        if self.disabled or archive.exists("generation",tag):
            return
        nearby=list(archive.select("solution",prefix="base-",n=1698,order="RANDOM()",limit=6))
        name,src=rng.choice(nearby) if nearby else ("anchor",{"colors":self.anchor})
        src=src["colors"][:536]
        if i<160 or i%3==0:
            out=self.oracle.ask(src,self.name+"-observed-"+key(src))
            if block(out,self.gen)==0:
                self.disabled=True
            archive.store("generation",tag,{"utc":utc(),"worker":2,"status":"OBSERVED","source":name,
                                           "seed":seed,"oracle":out["status"]})
            return
        mode=rng.choice(["prefix","window","sparse","wide","wide"])
        colors,gen=gen_with_sat(self.gen,name,src,rng,mode,seed)
        gen.update(worker=2,targeted=True)
        if colors is not None:
            digest,new=register(colors,name,"targeted-"+mode,2,i,self.row,self.anchor,[])
            out=self.oracle.ask(colors,self.name+"-generated-"+digest)
            if block(out,self.gen)==0:
                self.disabled=True
            gen.update(base=digest,distinct=new,oracle=out["status"])
            if new:
                probe(digest,colors,self.deadline)
        archive.store("generation",tag,gen)

if __name__=="__main__":
    control=Oracle(1698,536).ask(read("inputs/base14.json")["colors"],"calib-oracle-1698")
    assert control["status"]=="SAT",control
    print(control["status"],control["conflicts"],flush=True)
