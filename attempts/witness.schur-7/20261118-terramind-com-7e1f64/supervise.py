import argparse
import os
import shutil
import signal
import sys
from collections import Counter
from searchlib import *

parser=argparse.ArgumentParser()
parser.add_argument("--seconds",type=int,default=8*3600)
parser.add_argument("--third-base-seconds",type=int,default=4*3600)
parser.add_argument("--resume-error",action="store_true")
args=parser.parse_args()
state=Path("logs/run.json")
if state.exists():
    run=read(state)
    if run.get("end"):
        if not args.resume_error or "exited unexpectedly" not in run.get("reason",""):
            raise SystemExit("Search has ended")
        run["paused"]=True
        run.pop("end")
        run.pop("reason",None)
    if not run.get("paused"):
        raise SystemExit("Previous supervisor lacks a shutdown checkpoint; check for live workers before resuming")
    deadline=run["deadline"]
    run.pop("paused")
else:
    start=time.time()
    deadline=start+args.seconds
    run=dict(start=utc(),start_epoch=start,deadline=deadline,seconds=args.seconds,segments=[],hour=-1)
run["pid"]=os.getpid()
save(state,run)
segment_start=utc()
peak_rss=0
peak_archive=0
stop=None
def on_signal(signum,frame):
    global stop
    stop=f"signal {signum}"
signal.signal(signal.SIGINT,on_signal)
signal.signal(signal.SIGTERM,on_signal)
processes={}
exits=[]

def launch(label,cmd):
    log=open(f"logs/{label}.log","a", buffering=1)
    print(f"{utc()} start {cmd}",file=log)
    child=subprocess.Popen(cmd,stdout=log,stderr=log,start_new_session=True)
    processes[label]=(child,log)
    print(f"{utc()} started {label} pid={child.pid}",flush=True)

def report(hour):
    count,solutions,best=archive.summary()
    by_n=Counter(solutions)
    d=shutil.disk_usage(".")
    line=(f"{utc()} hour={hour} bases={count} "
          f"N1696={by_n[1696]} N1698={by_n[1698]} N>1698={sum(v for n,v in by_n.items() if n>1698)} "
          f"best={max(1698,best or 0)} free_GiB={d.free/2**30:.2f} active={','.join(processes)}")
    with open("progress.md","a") as f:
        f.write(line+"\n")
    print(line,flush=True)
    df=subprocess.run(["df","-h","."],capture_output=True,text=True).stdout
    with open("logs/disks.log","a") as f:
        print(utc(),df,file=f)
    return d

def memory():
    ids={p.pid for p,_ in processes.values()}
    listing=subprocess.run(["ps","-axo","pgid=,rss="],capture_output=True,text=True,check=True).stdout
    return sum(int(rss)*1024 for pgid,rss in (line.split() for line in listing.splitlines())
               if int(pgid) in ids)

if shutil.disk_usage(".").free < 8*2**30:
    stop="free space below 8 GiB at start"
if not stop and time.time()<deadline:
    for i in range(3):
        limit=deadline if i!=2 else min(deadline,run["start_epoch"]+args.third_base_seconds)
        if time.time()<limit:
            launch(f"base-{i}",[sys.executable,"-u","bases.py",str(i),str(limit)])
try:
    while not stop and time.time()<deadline:
        if Path("STOP").exists():
            stop=Path("STOP").read_text().strip() or "stop file"
            break
        for name,(child,log) in list(processes.items()):
            rc=child.poll()
            if rc is not None:
                print(f"{utc()} exit {rc}",file=log)
                log.close()
                del processes[name]
                exits.append(dict(name=name,rc=rc,utc=utc()))
                print(f"{utc()} exited {name} rc={rc}",flush=True)
                if rc!=0:
                    stop=f"{name} exited unexpectedly with {rc}"
                    break
        if stop:
            break
        if Path("push-ready").exists() and "push" not in processes and not any(e["name"]=="push" for e in exits):
            launch("push",[sys.executable,"-u","push.py",str(deadline),str(run["start_epoch"]+args.third_base_seconds)])
        if (Path("side-ready").exists() and "base-2" not in processes and "side" not in processes
                and not any(e["name"]=="side" for e in exits)):
            launch("side",[sys.executable,"-u","side.py",str(deadline)])
        rss=memory()
        d=shutil.disk_usage(".")
        storage=sum(p.stat().st_size for p in Path(".").glob("checkpoints.sqlite*"))
        peak_rss=max(peak_rss,rss)
        peak_archive=max(peak_archive,storage)
        if storage>2.35*2**30:
            stop=f"checkpoint size guard {storage/2**30:.2f} GiB"
        elif rss>5.5*2**30:
            stop=f"RSS guard {rss/2**30:.2f} GiB"
        elif d.free < 8*2**30:
            stop=f"free space {d.free/2**30:.2f} GiB below floor"
        elif time.time()-run["start_epoch"]>1 and run["hour"] >= 0 and not processes:
            stop="all search workers exited early"
        hour=int((time.time()-run["start_epoch"])//3600)
        if hour>run["hour"]:
            report(hour)
            run["hour"]=hour
            save(state,run)
        time.sleep(min(4,max(0,deadline-time.time())))
except BaseException as e:
    stop=repr(e)
    raise
finally:
    for name,(child,log) in processes.items():
        if child.poll() is None:
            os.killpg(child.pid,signal.SIGTERM)
    for name,(child,log) in processes.items():
        try:
            rc=child.wait(timeout=8)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGKILL)
            rc=child.wait()
        record=dict(name=name,rc=rc,utc=utc())
        print(record,file=log)
        log.close()
        exits.append(record)
    processes.clear()
    for p in Path("tmp").glob("*"):
        if p.suffix in {".cnf",".lrat",".txt",".part"}:
            p.unlink()
    report("final")
    run["segments"].append(dict(start=segment_start,end=utc(),end_epoch=time.time(),exits=exits,
                                reason=stop or "deadline",peak_sampled_rss=peak_rss,
                                peak_archive_bytes=peak_archive))
    if stop and stop.startswith("signal ") and time.time()<deadline:
        run["paused"]=True
    else:
        run["end"]=utc()
        run["reason"]=stop or "deadline"
    save(state,run)
    print(f"SEARCH EXIT {run['segments'][-1]}",flush=True)
