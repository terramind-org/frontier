from searchlib import *

baseline = read("baseline.json")["colors"]
assert len(baseline) == 1696 and valid(baseline, 7)
broken = baseline.copy()
broken[1] = broken[0]
assert (1,1,2) in triples(broken)
save("inputs/broken1696.json", {"colors":broken})
for p, ok in [("baseline.json", True), ("inputs/broken1696.json",False),
              ("inputs/N1698_b1_0014_sym.json",True),
              ("inputs/p4_0001_N1698.json",True),
              ("inputs/longq_calib_sym1698_F150_m300.json",True)]:
    out=diagnose(p)
    assert (re.search(r"^valid:\s+yes$", out, re.M) is not None) == ok and (re.search(r"^valid:\s+no$", out, re.M) is not None) != ok, out
    print(p, out, flush=True)
source=read("inputs/N1698_b1_0014_sym.json")["colors"]
broken=source.copy()
broken[1]=broken[0]
save("inputs/broken1698.json",{"colors":broken})
out=diagnose("inputs/broken1698.json")
assert re.search(r"^valid:\s+no$", out, re.M) is not None and (1,1,2) in triples(broken),out
print(out,flush=True)
for n,k,status in [(13,3,"SAT"),(14,3,"UNSAT"),(44,4,"SAT"),(45,4,"UNSAT")]:
    run=solve(dict(n=n,k=k,fixed={1:0,2:1}),f"calib-canonical-{n}",1736,120)
    print({x: y for x,y in run.items() if x!="job"},flush=True)
    assert run["status"] == status,run
base14=read("inputs/base14.json")["colors"]
assert base14 == source[:536] and valid(base14,6)
for n,base in [(1696,baseline[:536]),(1698,base14)]:
    run=solve(rowley(n,base),f"calib-{n}",781351734,180)
    print({x:y for x,y in run.items() if x!="job"},flush=True)
    assert run["status"] == "SAT", run
print("CALIBRATION PASS",flush=True)
