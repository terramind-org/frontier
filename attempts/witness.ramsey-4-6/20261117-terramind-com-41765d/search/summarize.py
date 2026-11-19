"""Summarize distinct labelled-state counts and minima from machine-readable logs."""
from collections import Counter
import json
from pathlib import Path
import re


RESULTS = Path('results')


def events(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.startswith('{')]


def fields(line):
    return {k:int(v) for k,v in re.findall(r'\b([a-z_]+)=(\d+)\b',line)}


def search_log(path):
    best = None
    visits = None
    distinct = 0
    probes = 0
    ended = False
    for line in path.read_text().splitlines():
        values = fields(line)
        if ' best ' in line:
            score = (values['zero'],values['one'])
            best = dict(zero=score[0],one=score[1],total=sum(score),utc=line.split()[0],
                        distance=values.get('distance'),step=values.get('step'))
        if 'visited' in values:
            visits = values['visited']
        if 'distinct' in values:
            distinct = max(distinct,values['distinct'])
        if 'tried' in values:
            probes += values['tried']
        if ' end visited=' in line:
            ended = True
    return dict(file=str(path),best=best,visited=visits,distinct=distinct,
                completed_restart_proposals=probes,enumeration_complete=ended)


def summarize():
    examples = {}
    for path in sorted(RESULTS.glob('*.log')):
        if path.name.startswith(('n36-','n37-','g36-','local-','catalogue-seed-',
                                 'guided-control-','refine-')):
            data = search_log(path)
            if data['best'] is not None:
                examples[path.stem] = data
    if Path('supplemental.log').exists():
        log = Path('supplemental.log')
        auto = [line for line in log.read_text().splitlines()
                if line.endswith('aut-base-01.orbits high_override=0.8 low=0.055 focus=0 pair_rate=0')]
        if auto:
            # The unwrapped involution run stops before the following machine-readable stage.
            lines = log.read_text().splitlines()
            a = lines.index(auto[0])
            b = next((i for i in range(a+1,len(lines)) if lines[i].startswith('aut_status=')),len(lines))
            tmp = Path('aut-base-history.log')
            tmp.write_text('\n'.join(lines[a:b])+'\n')
            examples['aut-base-01'] = search_log(tmp)
    statuses = {}
    for path in (Path('structured.log'),Path('unrestricted.log'),Path('supplemental.log'),Path('extra-lane.log'),Path('growth.log')):
        if path.exists():
            for event in events(path):
                if 'job' in event and event.get('event')=='end':
                    statuses[event['job']] = event['status']
    local = {}
    for label,data in examples.items():
        if not label.startswith('local-'):
            continue
        family = 'structured' if label.startswith('local-structured-') else (
            'published extension' if label.startswith('local-exoo-extension-') else 'random')
        local.setdefault(family,[]).append((label,data))
    local_totals = {}
    for group,data in local.items():
        label,best = min(data,key=lambda pair:pair[1]['best']['total'])
        local_totals[group] = dict(batches=len(data),successful_exits=sum(statuses.get(name)==0 for name,_ in data),
            largest_distinct_batch=max(m['distinct'] for _,m in data), best_batch=label,best=best['best'])
    for label,data in examples.items():
        if label.startswith(('n36-','n37-','g36-')):
            print(label,json.dumps(data))
    print('local',json.dumps(local_totals))
    for pattern in ('aut-base-','catalogue-seed-','refine-'):
        entries = [(name,row) for name,row in examples.items() if name.startswith(pattern)]
        if entries:
            name,row = min(entries,key=lambda pair:pair[1]['best']['total'])
            print(pattern,json.dumps(dict(batches=len(entries),minimum_name=name, **row)))
    for path in [Path('all-extensions.log'),RESULTS/'catalogue-extension.log',RESULTS/'delete-three.log']:
        if path.exists():
            rows = [e for e in events(path) if 'status' in e]
            print(str(path),json.dumps(dict(Counter(e['status'] for e in rows))))


if __name__ == '__main__':
    summarize()
