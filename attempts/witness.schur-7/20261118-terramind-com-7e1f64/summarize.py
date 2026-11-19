import datetime
import gzip
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path
from statistics import median

import archive

def prior():
    fs=json.loads(Path("logs/initial-features.json").read_text())
    labels=Path("logs/initial-base-order.txt").read_text().splitlines()
    control=fs["anchor"]
    others=[fs[x] for x in labels if x!="b1_0014"]
    return dict(anchor=control,baseline=fs["rowley"],other_count=len(others),
                rowley_distances=[min(x["distance_rowley"] for x in others),
                                  median(x["distance_rowley"] for x in others),
                                  max(x["distance_rowley"] for x in others)],
                positions_with_anchor_unique=[x+1 for x,a in enumerate(control["small"])
                                              if all(y["small"][x]!=a for y in others)],
                group_sizes=[[min(y["sizes"][g] for y in others),median(y["sizes"][g] for y in others),
                              max(y["sizes"][g] for y in others)] for g in range(6)],
                group_gaps=[[min(y["max_gaps"][g] for y in others),median(y["max_gaps"][g] for y in others),
                              max(y["max_gaps"][g] for y in others)] for g in range(6)])

def count():
    conn=archive.connection()
    run=json.loads(Path("logs/run.json").read_text())
    start=run["start_epoch"]
    groups=defaultdict(Counter)
    bydist=defaultdict(Counter)
    hourly=defaultdict(Counter)
    canonical=set()
    features=defaultdict(lambda:{"sizes":[[] for _ in range(6)],
                                  "max_gaps":[[] for _ in range(6)],
                                  "median_gaps":[[] for _ in range(6)],
                                  "distance_anchor":[], "distance_rowley":[]})
    complete=conn.execute("""SELECT b.data, a.status, c.status FROM records b
            LEFT JOIN records a ON a.kind='job' AND a.key='base-'||b.key||'-1696'
            LEFT JOIN records c ON c.kind='job' AND c.key='base-'||b.key||'-1698'
            WHERE b.kind='base'""")
    for blob,a,c in complete:
        b=archive.unpack(blob)
        recolor={}
        signature=bytes(recolor.setdefault(col,len(recolor)) for col in b["colors"])
        canonical.add(hashlib.sha256(signature).digest())
        if c in ("SAT","UNSAT"):
            measured=features[c]
            for k in ("sizes","max_gaps","median_gaps"):
                for bins,value in zip(measured[k],b["features"][k]):
                    bins.append(value)
            for k in ("distance_anchor","distance_rowley"):
                measured[k].append(b["features"][k])
        epoch=datetime.datetime.fromisoformat(b["utc"]).timestamp()
        hour=max(0,int((epoch-start)//3600))
        d=b["features"]["distance_anchor"]
        for bucket in (groups[b["recipe"]],bydist[d//5*5],hourly[hour]):
            bucket["distinct"]+=1
            if a is not None:
                bucket[a+"1696"]+=1
            if c is not None:
                bucket[c+"1698"]+=1
    statuses={}
    for group,query in {
        "base":"key LIKE 'base-%'",
        "push":"key LIKE 'push-%'",
        "cubes":"key LIKE 'cube-%'"}.items():
        statuses[group]=list(conn.execute(f"""SELECT n,status,COUNT(*) FROM records
                  WHERE kind='job' AND {query} GROUP BY n,status ORDER BY n,status"""))
    oracle=Counter()
    core_sizes=[]
    for _,job in archive.select("oracle",prefix="core1699"):
        oracle[job["status"]]+=1
        if "core" in job:
            core_sizes.append(len(job["core"]))
    variants=defaultdict(Counter)
    quick=defaultdict(Counter)
    for _,row in archive.select("quick-window"):
        for n,middle,top,status,_,_ in row["res"]:
            quick[f"{n}-{middle}-{top}"][status]+=1
    for _,row in archive.select("variant"):
        for i,r in enumerate(row["results"]):
            variants[1699+i//16][r[0]]+=1
    local=list(archive.select("local",prefix="local-"))
    local_stats=Counter()
    best_local=None
    for _,r in local:
        last=r["output"].splitlines()[-1].split()
        local_stats[r["best"]]+=1
        if best_local is None or r["best"]<best_local["best"]:
            best_local=r
        local_stats["moves"]+=int(last[1])
    cubes=Counter()
    for label,r in archive.select("cube-plan"):
        seen=[archive.get("job",f"cube-{label}-{i:02d}") for i in range(len(r["children"]))]
        s=[z["status"] if z else "MISSING" for z in seen]
        if all(x=="UNSAT" for x in s):
            result="UNSAT"
        elif any(x=="SAT" for x in s):
            result="SAT"
        else:
            result="OPEN"
        cubes[(r["n"],result)]+=1
    summary={
        "run":run, "progress":Path("progress.md").read_text().splitlines(),
        "prior_features":prior(),
        "base_yield_by_recipe":groups, "base_yield_by_distance_bin":bydist, "base_yield_by_generation_hour":hourly,
        "base_total":archive.summary(), "distinct_up_to_color_relabelling":len(canonical),
        "exact_status_by_target":statuses,
        "feature_medians": {s: {**{k:[median(a) for a in d[k]] for k in ("sizes","max_gaps","median_gaps")},
                                       **{k:median(d[k]) for k in ("distance_anchor","distance_rowley")}}
                             for s,d in features.items()},
        "oracle_status":oracle, "core_size_range":(min(core_sizes),median(core_sizes),max(core_sizes)) if core_sizes else None,
        "variants_status":variants, "quick_window_status":quick, "local_status":local_stats,
        "best_local":{k:v for k,v in best_local.items() if k not in ("start","best_colors")} if best_local else None,
        "cube_roots":[[n,s,c] for (n,s),c in sorted(cubes.items())],
        "proofs":[[key,row["certificate"]] for key,row in archive.select("job",prefix="push-") if "certificate" in row],
    }
    return summary

def list_1699():
    """Machine-readable index. Full restrictions are in the named compressed SQLite records."""
    conn=archive.connection()
    with gzip.open("logs/unsat-1699.jsonl.gz","wt",compresslevel=5) as f:
        def emit(row):
            print(json.dumps(row,separators=(",",":")),file=f)
        for key,raw in conn.execute("SELECT key,data FROM records WHERE kind='job' AND n=1699 AND status='UNSAT' ORDER BY key"):
            j=archive.unpack(raw)
            emit({"kind":"SAT solver","key":key,"conflicts":j.get("conflicts"),"seed":j["seed"],"rc":j["rc"],
                  "certificate":j.get("certificate",{}).get("sha256")})
        for key,r in archive.select("oracle",prefix="core1699"):
            if r["status"]=="UNSAT":
                emit({"kind":"assumption SAT solver","key":key,"core_size":len(r["core"]),"rc":r["rc"]})
        for key,r in archive.select("variant"):
            for m,(s,a,c) in enumerate(r["results"][:16],530):
                if s=="UNSAT":
                    emit({"kind":"reflection propagation","key":key,"n":1699,"pivot":m+1,
                          "processed_singletons":a,"empty_domain":c,"rc":r["rc"]})
        for key,r in archive.select("quick-window"):
            for n,middle,top,s,a,c in r["res"]:
                if n==1699 and s=="UNSAT":
                    emit({"kind":"unmirrored window propagation","key":key,"n":n,"middle":middle,"top":top,
                          "processed_singletons":a,"empty_domain":c,"rc":r["rc"]})
        for label,r in archive.select("cube-plan"):
            if r["n"]!=1699:
                continue
            keys=[f"cube-{label}-{i:02d}" for i in range(len(r["children"]))]
            jobs=[archive.get("job",k) for k in keys]
            if all(j and j["status"]=="UNSAT" for j in jobs):
                emit({"kind":"all branches UNSAT","root":label,"keys":keys})

if __name__=="__main__":
    result=count()
    data=json.dumps(result,indent=2)+"\n"
    Path("logs/summary.json").write_text(data)
    list_1699()
    print(data)
