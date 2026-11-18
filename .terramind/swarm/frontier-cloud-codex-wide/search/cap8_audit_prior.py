"""Audit the recorded c8 cap replacement pools against the fixture itself."""
import argparse, hashlib, itertools, json
from pathlib import Path

P=[3**k for k in range(7,-1,-1)]
def vec(q): return tuple((q//p)%3 for p in P)
def ident(v): return sum(x*p for x,p in zip(v,P))
def third(a,b): return ident(tuple((-x-y)%3 for x,y in zip(vec(a),vec(b))))
def valid(s): return all(third(a,b) not in s for a,b in itertools.combinations(s,2))

def main(a):
 root=Path(a.root); raw=json.load(open(a.input))["points"]
 by=[set() for _ in range(3)]
 for p in raw: by[p[0]].add(ident(p))
 base=set().union(*by); report=[]
 for n in (1,2,4,8,16,32):
  folder=root if n==1 else root/f"batch-{n}"
  screen=json.load(open(folder/"screen.json"))
  result=json.load(open(folder/"result.json"))
  # The historical screen omitted delete_a.  cover_steps is the actual greedy
  # deletion trace, so it is the only complete reconstruction source.
  delete={step["point"] for step in screen["cover_steps"]}
  fixed=base-delete
  ins=set(screen["insert_b"])|set(screen["insert_c"])
  stored=result["counts"]
  report.append({"batch":n,"unique_delete_total":len(delete),"delete_in_frozen":len(delete&by[0]),
    "actual_fixed":len(fixed),"stored_fixed":stored["fixed"],"stored_delete_b":stored["delete_b"],
    "stored_delete_c":stored["delete_c"],"unreported_delete_a":sorted(delete&by[0]),"partition":len(fixed)+len(delete)==len(base),
    "fixed_valid":valid(fixed),"selected_anchors_all_survive":set(screen["survived_anchors"])==set(screen["selected_anchors"]),
    "survivors_direct_valid_with_fixed":all(valid(fixed|{q}) for q in ins),
    "stored_target":stored["target_selected"],"actual_target":513-len(fixed),
    "stored_target_total":len(fixed)+stored["target_selected"],"input_sha256":hashlib.sha256(open(a.input,"rb").read()).hexdigest()})
 out={"baseline_size":len(base),"slice_sizes":[len(s) for s in by],"baseline_valid":valid(base),"batches":report}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps(out,sort_keys=True))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--input",required=True);p.add_argument("--root",required=True);p.add_argument("--output",required=True);main(p.parse_args())
