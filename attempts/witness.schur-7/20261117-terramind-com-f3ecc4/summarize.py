"""Summarise logs/bases.jsonl, logs/push*.jsonl and logs/cnc*.jsonl into logs/summary.json (counts per status)."""
import collections, glob, json
S = {}
L = [json.loads(l) for l in open('logs/bases.jsonl')]
gen = [l for l in L if l['event'] == 'GEN']
S['bases_generated_distinct'] = sum(1 for l in gen if 'base' in l)
S['gen_calls'] = dict(collections.Counter(f"{l['gen']}:{l['status']}" for l in gen))
S['gen_duplicates'] = sum(1 for l in L if l['event'] == 'GEN_DUP')
S['validate_1696'] = dict(collections.Counter(f"{l['status']}:viol={l.get('violations')}" for l in L if l['event'] == 'VALIDATE'))
S['validate_by_gen'] = {}
names = {l['base']: l['gen'] for l in gen if 'base' in l}
for l in L:
    if l['event'] == 'VALIDATE':
        k = f"{names.get(l['base'])}:{l['status']}"; S['validate_by_gen'][k] = S['validate_by_gen'].get(k, 0) + 1
S['modes'] = dict(collections.Counter(f"{l['mode']}:{l['status']}" for l in L if l['event'] in ('MODE', 'MODE_SAT')))
S['mode_sat'] = [(l['base'], l['mode'], l['N'], l['violations']) for l in L if l['event'] == 'MODE_SAT']
S['ham_rowley'] = sorted(l['ham_rowley'] for l in gen if 'ham_rowley' in l)
S['bases_with_any_N_gt_1696'] = sorted({l['base'] for l in L if l['event'] == 'MODE_SAT' and l['violations'] == 0})
S['bases_tested_full_modes'] = len({l['base'] for l in L if l['event'] in ('MODE', 'MODE_SAT') and l['mode'] == 'free1697'})
P = []
for f in sorted(glob.glob('logs/push*.jsonl')):
    P += [json.loads(l) for l in open(f)]
S['push_tries'] = dict(collections.Counter(f"{l['N']}:{l['mode']}:{l['status']}" for l in P if l['event'] == 'TRY'))
S['push_gen'] = dict(collections.Counter(f"{l['N']}:{l['status']}" for l in P if l['event'] == 'GEN'))
S['push_new_best'] = [(l['N'], l['base'], l['mode']) for l in P if l['event'] == 'NEW_BEST']
C = []
for f in sorted(glob.glob('logs/cnc*.jsonl')):
    C += [dict(json.loads(l), file=f) for l in open(f)]
S['cubes'] = dict(collections.Counter(f"{l['file']}:N{l['N']}:F{l['F']}:{l['status']}" for l in C if l['event'] == 'CUBE'))
json.dump(S, open('logs/summary.json', 'w'), indent=1)
print(json.dumps(S, indent=1))
