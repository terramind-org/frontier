"""Driver: slide windows of size w over the 77-gate record, one subprocess per (s,w) with a hard timeout."""
import subprocess, sys, json, time
LIM = int(sys.argv[1]) if len(sys.argv) > 1 else 240
deadline = float(sys.argv[2]) if len(sys.argv) > 2 else 1e18  # unix time
jobs = []
for w in [9, 11, 10]:
    step = 1
    ss = list(range(40, 77 - w + 1, step))
    if 77 - w not in ss:
        ss.append(77 - w)
    jobs += [(s, w) for s in ss]
# small windows first, interleaved by increasing w so every size gets sampled early
jobs.sort(key=lambda j: (j[1], -j[0]))
timedout = {}
for s, w in jobs:
    if s < timedout.get(w, -1): continue
    if time.time() > deadline:
        print("DEADLINE", flush=True); break
    try:
        r = subprocess.run([".venv/bin/python", "window_sat.py", "baseline.json", str(s), str(w), str(LIM)],
                           capture_output=True, text=True, timeout=LIM)
        print(r.stdout.strip(), r.stderr.strip()[-200:], flush=True)
        if '"timeout"' in r.stdout: timedout[w] = s
    except subprocess.TimeoutExpired:
        print(json.dumps(dict(s=s, w=w, result="timeout", secs=LIM)), flush=True)
        timedout[w] = s  # smaller s only has more prefix vectors: skip them
