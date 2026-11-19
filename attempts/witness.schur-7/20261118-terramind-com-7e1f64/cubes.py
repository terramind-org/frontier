import hashlib
from searchlib import *

def domains(n,k,fixed):
    allowed=[(1<<k)-1]*(n+1)
    classes=[[] for _ in range(k)]
    for x,c in fixed.items():
        allowed[x]=1<<c
        classes[c].append(x)
    for c,group in enumerate(classes):
        group.sort()
        bit=1<<c
        for i,x in enumerate(group):
            if x%2==0:
                allowed[x//2]&=~bit
            for y in group[i:]:
                if x+y<=n:
                    allowed[x+y]&=~bit
                if y>x:
                    allowed[y-x]&=~bit
    return allowed

def split(n,k,fixed):
    allowed=domains(n,k,fixed)
    if 0 in allowed[1:]:
        # Keep a single explicit branch for the exact solver/certificate.
        return [fixed]
    candidates=[x for x in range(1,n+1) if x not in fixed and allowed[x].bit_count()>1]
    if not candidates:
        return [fixed]
    minimum=min(allowed[x].bit_count() for x in candidates)
    candidates=[x for x in candidates if allowed[x].bit_count()==minimum]
    # Include positions across the range, plus the beginning of the free interval.
    chosen=sorted(set([*candidates[:4],*candidates[::max(1,len(candidates)//8)]]))
    before=sum(a.bit_count() for a in allowed)
    def trials(x):
        return [{**fixed,x:c} for c in range(k) if allowed[x]&(1<<c)]
    def score(x):
        reductions=[before-sum(a.bit_count() for a in domains(n,k,q)) for q in trials(x)]
        return min(reductions),sum(reductions),-x
    x=max(chosen,key=score)
    return trials(x)

def cube_specs(n,k,fixed,levels):
    cubes=[fixed]
    for _ in range(levels):
        cubes=[child for parent in cubes for child in split(n,k,parent)]
    return cubes

def plan():
    inputs=[read("inputs/"+f)["colors"] for f in (
        "N1698_b1_0014_sym.json",
        "p4_0001_N1698.json",
        "longq_calib_sym1698_F150_m300.json")]
    for n in (1699,1700):
        for index,prefix in ((0,500),(0,460),(1,420),(2,360),(0,300),(1,250),(2,200),(0,150)):
            root=f"{index}-{n}-{prefix}"
            marker=archive.get("cube-plan",root)
            if marker is None:
                fixed={x:c for x,c in enumerate(inputs[index][:prefix],1)}
                children=cube_specs(n,7,fixed,2)
                marker={"n":n,"prefix":prefix,"index":index,"fixed":fixed,"children":children}
                archive.store("cube-plan",root,marker,unique=True)
            yield root,marker

def run_slice(shard,deadline,wall):
    end=min(deadline-6,time.time()+wall)
    for label,root in plan():
        for i,branch in enumerate(root["children"]):
            if i%2!=shard:
                continue
            if time.time()>end-4:
                return
            name=f"cube-{label}-{i:02d}"
            if archive.exists("job",name):
                continue
            seed=int.from_bytes(hashlib.sha256(name.encode()).digest()[:3],"big")
            result=solve(dict(n=root["n"],k=7,fixed=branch),name,seed,min(420,max(1,end-time.time()-4)))
            if result["status"]=="SAT":
                print(f"{utc()} accepted config {name} N={root['n']}",flush=True)
            return

if __name__=="__main__":
    n,k=44,4
    known=archive.get("solution","calib-canonical-44")["colors"]
    fixed={x:c for x,c in enumerate(known[:20],1)}
    runs=[]
    for i,branch in enumerate(cube_specs(n,k,fixed,2)):
        runs.append(solve(dict(n=n,k=k,fixed=branch),f"calib-cube-{i}",421,30))
    assert any(x["status"]=="SAT" for x in runs)
    assert any(all(known[x-1]==c for x,c in branch.items()) for branch in cube_specs(n,k,fixed,2))
    print([(x["name"],x["status"],x.get("conflicts")) for x in runs])
