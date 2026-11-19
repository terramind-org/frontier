"""Extract the shortest network printed by SorterHunter (sh_*.out) into best_sh.json (witness format)."""
import re, json, sys, glob
best = None
for f in glob.glob('sh_*.out'):
    for line in open(f):
        m = re.search(r"'L':(\d+).*'nw':(\[.*\])", line)
        if not m: continue
        L = int(m.group(1)); g = [(int(a), int(b)) for a, b in re.findall(r'\((\d+),(\d+)\)', m.group(2))]
        if best is None or L < best[0]: best = (L, g, f)
print(best[0], best[2], len(best[1]))
json.dump({"comparators": [list(x) for x in best[1]]}, open('best_sh.json', 'w'))
