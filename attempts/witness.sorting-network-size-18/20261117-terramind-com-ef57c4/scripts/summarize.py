"""Summarize retained evidence without treating interrupted calls as solver answers."""
import pathlib,json,ast,re,collections
S=pathlib.Path(__file__).resolve().parent
out={'budget':json.load(open(S/'budget.json')),'hunter':[],'SAT':[]}
printed=set();best=10000;best_gates=None
for f in sorted(S.glob('hunt_*.log')):
    path=S/(f.stem+'.summary.json')
    row=json.loads(path.read_text()) if path.exists() else {'name':f.stem}
    for line in f.read_text().splitlines():
        if "{'N':" in line:
            obj=ast.literal_eval(line[line.index("{'N':"):]);gates=tuple(obj['nw']);printed.add(gates)
            if len(gates)<best:best=len(gates);best_gates=gates
        for token,pattern,keys in [
            ('SampledCandidates',r'SampledCandidates (\d+) DistinctSampled (\d+) MaxPositionDistance (\d+)',['samples_reported','distinct_sampled_reported','max_position_distance_reported']),
            ('HLLDistinctEstimate',r'HLLDistinctEstimate ([\d.]+) CandidateObservations (\d+)',['estimated_distinct_reported','candidate_observations_reported']),
            ('Iteration ',r'Iteration (\d+)  t=([\d.]+) s',['iterations_reported','CPU_seconds_reported'])]:
            match=re.search(pattern,line)
            if match:
                for key,val in zip(keys,match.groups()):row[key]=float(val) if '.' in val else int(val)
    out['hunter'].append(row)
out['distinct_printed_valid_ordered_networks']=len(printed)
out['printed_sizes']=dict(collections.Counter(map(len,printed)))
out['best_printed_size']=best
if best_gates is not None:(S/'best-valid.json').write_text(json.dumps({'comparators':best_gates}))
for f in sorted(S.glob('sat_[0-9][0-9][0-9]_*.log')):
    m=re.fullmatch(r'sat_(\d+)_(baseline|round1)_order(\d+)_s(\d+)_w(\d+)',f.stem)
    if not m:continue
    index,start,order,offset,width=m.groups()
    row={'name':f.stem,'index':int(index),'start':start,'order':int(order),'s':int(offset),'w':int(width)}
    path=S/(f.stem+'.exit.json')
    if path.exists():row.update(json.loads(path.read_text()))
    for line in f.read_text().splitlines():
        try:x=json.loads(line)
        except ValueError:continue
        if x.get('event') in ['encoded','solve','result']:row['last_solver_event']=x
        if x.get('event')=='result':row['result']=x
        if x.get('event')=='best_candidate':row['best_failing_inputs']=x['failing_inputs']
    if 'result' in row:row['classification']=row['result']['status']
    elif row.get('termination')=='deadline':row['classification']='outer deadline, no answer'
    elif row.get('returncode',0)!=0:row['classification']='error'
    else:row['classification']='running'
    out['SAT'].append(row)
out['SAT_classifications']=dict(collections.Counter(r['classification'] for r in out['SAT']))
rep=S/'repair.log'
if rep.exists():
    events=[]
    for line in rep.read_text().splitlines():
        try:events.append(json.loads(line))
        except ValueError:pass
    phase=None;research=[];controls=[]
    for event in events:
        if event.get('event')=='start':phase=event.get('name')
        if phase=='repair76':research.append(event)
        else:controls.append(event)
    out['repair_events']=research
    out['repair_calibration_events']=controls
    exitpath=S/'repair.exit.json'
    if exitpath.exists():out['repair_exit']=json.loads(exitpath.read_text())
(S/'evidence-summary.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k not in ['hunter','SAT','repair_events']},indent=2))
