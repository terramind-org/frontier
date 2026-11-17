"""Summarise DESCENT lines of search logs: per tag, descents, final-rank distribution, lowest rank, flips, distinct
best schemes, sampled distinct states. Usage: python3 -I summarize.py logs/<tag>.log ..."""
import re, sys, collections
for path in sys.argv[1:]:
    rows = []
    start = None
    for line in open(path):
        if " START " in line:
            start = line.split()[0]
            part = re.search(r"partition=(\S+)", line).group(1)
            r0 = re.search(r" rank=(\d+)", line).group(1)
        if " DESCENT " in line:
            kv = dict(re.findall(r" (\w+)=(\S+)", line))
            kv["utc"] = line.split()[0]
            rows.append(kv)
    if not rows:
        print(f"{path}: no descents"); continue
    full = [r for r in rows if r["timeup"] == "0" and r["stuck"] == "0" and r.get("overflow", "0") == "0"]
    dist = collections.Counter(int(r["best"]) for r in full)
    lo = min(int(r["best"]) for r in rows)
    first_lo = next(r["utc"] for r in rows if int(r["best"]) == lo)
    flips = sum(int(r["flips"]) for r in rows)
    hashes = collections.defaultdict(set)
    for r in rows:
        hashes[int(r["best"])].add(r["best_hash"])
    samp = sum(int(r["sampled"]) for r in rows); dsamp = sum(int(r["distinct_sampled"]) for r in rows)
    print(f"{path}: partition={part} start_rank={r0} start_utc={start} descents={len(rows)} completed={len(full)} "
          f"cut_by_time={sum(r['timeup'] == '1' for r in rows)} stuck={sum(r['stuck'] == '1' for r in rows)} overflow={sum(r.get('overflow', '0') == '1' for r in rows)} final_rank_dist={dict(sorted(dist.items()))} lowest={lo} first_lowest_utc={first_lo} "
          f"flips={flips:.3e} distinct_best_schemes_at_lowest={len(hashes[lo])} "
          f"distinct_best_schemes_by_rank={ {k: len(v) for k, v in sorted(hashes.items())} } "
          f"sampled_states={samp} distinct_within_descent={dsamp}")
