"""Independent deterministic Boolean/cardinality checker for saved cap clauses."""
import argparse, json, time
from pathlib import Path

class DPLL:
 def __init__(self, clauses,n,target,deadline):
  self.c,self.n,self.t,self.deadline=clauses,n,target,deadline;self.nodes=0;self.conflicts=0
  self.degree=[0]*n
  for vs,_ in clauses:
   for v in vs:self.degree[v]+=1
 def prop(self,a):
  changed=True
  while changed:
   if time.monotonic()>self.deadline:raise TimeoutError
   changed=False; one=sum(x==1 for x in a); unknown=[i for i,x in enumerate(a) if x<0]
   if one+len(unknown)<self.t:return False
   if one==self.t:
    for v in unknown:a[v]=0
    changed=bool(unknown)
   elif one+len(unknown)==self.t:
    for v in unknown:a[v]=1
    changed=bool(unknown)
   for vs,upper in self.c:
    count=sum(a[v]==1 for v in vs)
    if count>upper:return False
    if count==upper:
     for v in vs:
      if a[v]<0:a[v]=0;changed=True
  return True
 def go(self,a):
  self.nodes+=1;b=a[:]
  if not self.prop(b):self.conflicts+=1;return None
  if all(x>=0 for x in b):return b
  v=max((i for i,x in enumerate(b) if x<0),key=lambda i:(self.degree[i],-i))
  for bit in (1,0):
   b[v]=bit;out=self.go(b)
   if out is not None:return out
  return None
def main(a):
 data=json.load(open(a.input));vs=data['variables'];cs=[(tuple(x['variables']),x['upper']) for x in data['clauses']]
 start=time.monotonic();solver=DPLL(cs,len(vs),data['target'],start+a.seconds)
 try:answer=solver.go([-1]*len(vs));status='SAT' if answer else 'UNSAT'
 except TimeoutError:answer=None;status='TIMEOUT'
 out={'backend':'independent deterministic DPLL with generic at-most-k and cardinality propagation','classification':status,'elapsed_seconds':time.monotonic()-start,'nodes':solver.nodes,'conflicts':solver.conflicts,'variables':len(vs),'clauses':len(cs),'target_selected':data['target']}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);p.add_argument('--seconds',type=float,default=300);main(p.parse_args())
