import pathlib,importlib.util,json,time,subprocess,datetime
S=pathlib.Path(__file__).resolve().parent

def module(name):
    spec=importlib.util.spec_from_file_location(name,S/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
h=module('hunter');w=module('window')
start=json.load(open(S/'budget.json'))['start_epoch'] if (S/'budget.json').exists() else time.time();(S/'budget.json').write_text(json.dumps({'start_epoch':start,'deadline_epoch':start+7200,'utc':datetime.datetime.fromtimestamp(start,datetime.timezone.utc).isoformat(),'calibration_launch_utc':h.utc(),'budget_seconds':7200}))
base=[tuple(x) for x in json.load(open(S/'baseline.json'))['comparators']]
broken=base[:33]+base[34:]
for label,gates in [('baseline',base),('broken76',broken)]:
    count=len(w.failures(w.apply(w.inputs(18),gates)));print(json.dumps({'utc':h.utc(),'control':label,'failing_inputs':count}),flush=True)
    assert (count==0)==(label=='baseline')
    (S/(label+'.json')).write_text(json.dumps({'comparators':gates}))
small=[tuple(x) for x in json.load(open(S/'optimal8.json'))['comparators']]
assert not len(w.failures(w.apply(w.inputs(8),small)))
padded=small[:5]+[small[4]]+small[5:]
cfg=h.config(padded,8,False,0,719,1000,2,'cal_hunter8')
r=h.run(cfg,20,'cal_hunter8',expected=20,calibration_target=19)
assert r['calibration_reached']
padded18=base[:74]+[(0,17)]+base[74:]
status,full=w.solve(padded18,18,73,3,2,30,710,str(S/'cal_sat18.json'))
assert status=='SAT' and len(full)==77
for s in range(16):
    status,_=w.solve(small,8,s,4,3,15,720+s,str(S/f'cal_neg{s}.json'))
    assert status=='UNSAT', (s,status)
print(json.dumps({'utc':h.utc(),'calibration':'PASS'}),flush=True)
