import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import time
import archive

ROOT = Path.cwd()
BUN = os.environ.get("SCHUR_BUN", str(Path.home() / ".bun/bin/bun"))
PROBLEM = "witness.schur-7"

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

def read(path):
    return json.loads(Path(path).read_text())

def save(path, obj):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_text(json.dumps(obj, separators=(",", ":")) + "\n")
    tmp.replace(path)

def triples(colors):
    return [(x, y, x+y) for x in range(1, len(colors)//2+1)
            for y in range(x, len(colors)-x+1)
            if colors[x-1] == colors[y-1] == colors[x+y-1]]

def valid(colors, k):
    return all(type(c) is int and 0 <= c < k for c in colors) and not triples(colors)

def rowley(n, base, mirror=True):
    return dict(n=n, k=7, fixed={x:c for x,c in enumerate([*base,6],1)},
                mirror=[[x,n+1-x] for x in range(1,(n+1)//2+1)] if mirror else [])

def reps(n, pairs):
    representative = list(range(n+1))
    for x,y in pairs:
        a,b = representative[x], representative[y]
        if a != b:
            representative = [a if r == b else r for r in representative]
    return representative

def diagnose(path):
    run = subprocess.run([BUN, "frontier", "diagnose", str(Path(path).resolve()), "--problem", PROBLEM],
                         cwd=ROOT.parent.parent.parent, capture_output=True, text=True, timeout=25)
    return run.stdout + run.stderr

def certified(colors, path):
    save(path, {"colors": colors})
    report = diagnose(path)
    (ROOT / "diagnoses" / (Path(path).stem + ".txt")).write_text(report)
    if not re.search(r"^valid:\s+yes$", report, re.M) or not valid(colors, 7):
        raise ValueError(f"Verifier rejected candidate {path}: {report}")

def encode(job, request, cnf):
    n,k = job["n"],job["k"]
    mirrors=job.get("mirror", [])
    masks=[(int(x),1<<c) for x,c in job.get("fixed",{}).items()]
    masks += [(int(x),mask) for x,mask in job.get("masks",{}).items()]
    with request.open("w") as f:
        print(n,k,len(mirrors),len(masks),file=f)
        for a,b in [*mirrors,*masks]:
            print(a,b,file=f)
    subprocess.run(["bin/encode", str(request), str(cnf)], check=True, timeout=20)

def decode(job, positive):
    k = job["k"]
    colors = []
    for r in reps(job["n"], job.get("mirror",[]))[1:]:
        opts = [c for c in range(k) if (r-1)*k+c+1 in positive]
        if len(opts) != 1:
            raise ValueError(f"Malformed model at representative {r}")
        colors.append(opts[0])
    if not valid(colors,k):
        raise ValueError("Model violates independent checker")
    for x,c in job.get("fixed",{}).items():
        if colors[int(x)-1] != c:
            raise ValueError("Model violates fixed colour")
    for x,mask in job.get("masks",{}).items():
        if not (mask & (1 << colors[int(x)-1])):
            raise ValueError("Model violates colour mask")
    return colors

def solve(job, name, seed, seconds, proof=False):
    prior=archive.get("job",name)
    if prior is not None:
        return prior
    cnf = Path("tmp") / (name + ".cnf")
    req = cnf.with_suffix(".txt")
    prf = cnf.with_suffix(".lrat")
    start = time.time()
    result = dict(utc_start=utc(), name=name, job=job, seed=seed, timeout_seconds=seconds)
    try:
        encode(job, req, cnf)
        with cnf.open() as f:
            _,_,v,c = f.readline().split()
        result.update(vars=int(v), clauses=int(c), build_seconds=round(time.time()-start, 3))
        cmd = ["bin/cadical", "-t", str(max(1,int(seconds))), f"--seed={seed}",
               "--shuffle", "--shufflerandom", str(cnf)]
        if proof:
            cmd[1:1] = ["--lrat", "--binary=false"]
            cmd += [str(prf)]
        def limit_proof():
            import resource
            cap = 800 * 1024**2
            resource.setrlimit(resource.RLIMIT_FSIZE, (cap,cap))
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=seconds+3,
                               preexec_fn=limit_proof if proof else None)
            result.update(rc=p.returncode, status={10:"SAT",20:"UNSAT",0:"TIMEOUT"}.get(p.returncode,"ERROR"))
            for field in ("conflicts","decisions","propagations"):
                m = re.search(r"^c " + field + r":\s*(\d+)", p.stdout, re.M)
                result[field] = int(m[1]) if m else None
            if result["status"] == "SAT":
                positive = {int(s) for line in p.stdout.splitlines() if line.startswith("v ")
                            for s in line[2:].split() if int(s)>0}
                colors = decode(job, positive)
                output = Path("solutions") / (name + ".json")
                if job["n"] > 1696:
                    certified(colors, output)
                    if job["n"]==1698 and not name.startswith("calib-"):
                        report=Path("diagnoses")/(name+".txt")
                        archive.store("diagnose",name,{"output":"\n".join(line for line in report.read_text().splitlines() if not line.startswith("$ bun"))})
                        report.unlink()
                        output.unlink()
                archive.store("solution",name,{"colors":colors})
                result["solution"] = name
            elif result["status"] == "ERROR":
                result["output"] = (p.stdout+p.stderr)[-2000:]
            if proof and result["status"] == "UNSAT":
                if Path("bin/lrat-check").exists():
                    sha = subprocess.check_output(["shasum","-a","256",str(prf)],text=True).split()[0]
                    try:
                        run = subprocess.run(["bin/lrat-check",str(cnf),str(prf)],
                                             text=True,capture_output=True,timeout=120)
                        result["certificate"] = dict(sha256=sha, rc=run.returncode,
                                                     output=run.stdout+run.stderr, bytes=prf.stat().st_size)
                    except subprocess.TimeoutExpired:
                        result["certificate"] = dict(sha256=sha,error="proof checker time limit")
                else:
                    result["certificate"] = {"error":"lrat-check unavailable"}
        except subprocess.TimeoutExpired:
            result.update(rc=-9,status="TIMEOUT",conflicts=None)
    except Exception as e:
        result.update(status="ERROR", error=repr(e))
    finally:
        for x in (cnf,req,prf):
            x.unlink(missing_ok=True)
    result.update(utc_end=utc(), seconds=round(time.time()-start,3))
    archive.store("job",name,result)
    return result

def solution(result):
    name=Path(result["solution"]).stem
    return archive.get("solution",name)["colors"]
