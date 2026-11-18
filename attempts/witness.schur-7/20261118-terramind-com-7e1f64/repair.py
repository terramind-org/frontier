from itertools import combinations
from searchlib import *

def region(colors,free):
    return dict(n=len(colors),k=7,fixed={x:c for x,c in enumerate(colors,1) if x not in free})

def recipes(colors):
    n=len(colors)
    conflicts=triples(colors)
    active={p for t in conflicts for p in t}
    bad={colors[x-1] for x in active}
    # Every scope leaves all variables from a violated triple movable.
    yield "conflicts",active,20
    for w in (24,64,128,240,400,600):
        free=set(range(1,w+1)) | set(range(max(1,n-w//2),n+1))
        free|={y for x in active for y in range(max(1,x-w//3),min(n+1,x+w//3+1))}
        yield f"window-{w}",free,60
    frozen_classes=sorted(set(range(7))-bad)
    for number in (0,1,2):
        for extra in combinations(frozen_classes,number):
            chosen=bad|set(extra)
            free={x for x,c in enumerate(colors,1) if c in chosen}
            tag="classes-"+"".join(map(str,sorted(chosen)))
            yield tag,free,90
    for w in (120,260,450):
        free=set(range(1,w+1)) | active
        free.update(x for x,c in enumerate(colors,1) if c in bad)
        yield f"prefix-and-bad-{w}",free,180

def job_slice(deadline,call):
    candidates=list(archive.select("local",prefix="local-1699"))
    candidates=sorted((r["best"],name,r["best_colors"]) for name,r in candidates if 0<r["best"]<=4)
    for _,name,colors in candidates:
        if time.time()>deadline-10:
            return
        for recipe,free,limit in recipes(colors):
            tag=f"repair-{name}-{recipe}"
            if archive.exists("job","push-"+tag):
                continue
            result=call(region(colors,free),tag,deadline,limit)
            return result

def calibrate():
    colors=archive.get("solution","calib-1698")["colors"]
    broken=colors.copy()
    broken[1]=broken[0]
    assert triples(broken)
    recipe,free,_=next(recipes(broken))
    result=solve(region(broken,free),f"calib-repair-{recipe}",23400,45)
    assert result["status"]=="SAT",result
    assert valid(solution(result),7)
    print("known solution recovered",result["status"],result.get("conflicts"))

if __name__=="__main__":
    calibrate()
