"""605-point all-vector L-BFGS relaxation with Lp overlap continuation."""
import datetime
import argparse
import json
from pathlib import Path
import time
import numpy as np
from scipy.optimize import minimize

root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--p-max',type=int,choices=[16,32,64],default=16)
parser.add_argument('--seed',type=int,default=17112027)
parser.add_argument('--label',default='relax')
args=parser.parse_args()
powers=[p for p in [2,4,8,16,32,64] if p<=args.p_max]
prefix=args.label
deadline=datetime.datetime.fromisoformat((root/'launch-utc.txt').read_text().strip().replace('Z','+00:00')).timestamp()+7200
started=time.time(); rng=np.random.default_rng(args.seed)
def unit(x):return x/np.linalg.norm(x,axis=1,keepdims=True)
def score(x):
    g=x@x.T;np.fill_diagonal(g,-1)
    return float(g.max())
def load(name):
    v=np.array(json.loads((root/name).read_text())['vectors'])
    return (v[:,::2]+np.sqrt(2)*v[:,1::2])/6
base=load('baseline.json');alt=load('expanded-best.json')
print(json.dumps({'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deadline_epoch':deadline,
    'seed':args.seed,'method':'all 605 vectors movable; Lp of positive cosine overlaps','powers':powers,
    'maxiter_per_p':1500,'time_remaining_seconds':deadline-started}),flush=True)
best=1.;restarts=0;latest=time.time();evaluations=0
warm_path=root/'relax-best605.npz'
if (root/(prefix+'-best605.npz')).exists():warm_path=root/(prefix+'-best605.npz')
if warm_path.exists():
    warm=np.load(warm_path)['vectors'];best=score(warm)
    np.savez(root/(prefix+'-best605.npz'),vectors=warm,score=best)
def save(x,stage):
    global best
    s=score(x)
    if s<best-1e-10:
        best=s;np.savez(root/(prefix+'-best605.npz'),vectors=x,score=s)
        print(json.dumps({'new_best':s,'stage':stage,'elapsed_seconds':time.time()-started,'angle':float(np.degrees(np.arccos(s)))}),flush=True)
def progress(x,stage):
    global latest
    if time.time()-latest>=20:
        save(unit(x.reshape(605,11)),stage)
        print(json.dumps({'elapsed_seconds':time.time()-started,'best_max_dot_605':best,'restarts':restarts,'evaluations':evaluations,'stage':stage}),flush=True)
        latest=time.time()
def loss(z,p):
    global evaluations
    if time.time()>=deadline:raise TimeoutError('shared 120-minute deadline')
    evaluations+=1
    raw=z.reshape(605,11);norm=np.linalg.norm(raw,axis=1,keepdims=True);x=raw/norm
    h=np.maximum(x@x.T-.5,0);np.fill_diagonal(h,0)
    top=h.max()
    if top==0:return 0.,np.zeros_like(z)
    scaled=h/top;s=np.sum(scaled**p)/2
    value=top*s**(1/p)
    grad=(scaled**(p-1))@x/(s**((p-1)/p))
    grad=(grad-x*np.sum(grad*x,axis=1,keepdims=True))/norm
    return value,grad.ravel()
# Central finite differences on a real 605-point state, including p=16.
test=np.vstack([base,unit(rng.normal(size=(1,11)))])
for p in powers:
    z=test.ravel();value,gradient=loss(z,p)
    errs=[]
    for idx in rng.choice(len(z),20,replace=False):
        plus=z.copy();minus=z.copy();plus[idx]+=1e-6;minus[idx]-=1e-6
        numeric=(loss(plus,p)[0]-loss(minus,p)[0])/2e-6
        errs.append(abs(numeric-gradient[idx]))
    assert max(errs)<1e-6,(p,max(errs))
    print('GRADIENT_SELF_TEST p',p,'max_absolute_error',max(errs),flush=True)
try:
    while time.time()<deadline:
        if restarts%4==0 and (root/(prefix+'-best605.npz')).exists():
            x=np.load(root/(prefix+'-best605.npz'))['vectors'].copy()
        else:
            fixed=base if restarts%2==0 else alt
            if (root/'holes.npz').exists():
                holes=np.load(root/'holes.npz')['directions'];h=holes[rng.integers(min(64,len(holes)))][None,:]
            else:h=unit(rng.normal(size=(1,11)))
            x=np.vstack([fixed,h])
        x=unit(x+rng.normal(size=x.shape)*[0,.003,.015,.05][restarts%4])
        for p in powers:
            result=minimize(loss,x.ravel(),args=(p,),jac=True,method='L-BFGS-B',
                callback=lambda z:progress(z,'p='+str(p)),
                options={'maxiter':1500,'ftol':1e-13,'gtol':1e-9,'maxcor':10,'maxls':30})
            x=unit(result.x.reshape(605,11));save(x,'p='+str(p))
        restarts+=1
except TimeoutError:pass
summary={'elapsed_seconds':time.time()-started,'best_max_dot_605':best,'best_min_angle_degrees':float(np.degrees(np.arccos(best))),
    'restarts':restarts,'evaluations':evaluations,'exit':'shared wall-clock deadline; no exact candidate claimed'}
(root/(prefix+'-summary.json')).write_text(json.dumps(summary,indent=2))
print('END',json.dumps(summary),flush=True)
