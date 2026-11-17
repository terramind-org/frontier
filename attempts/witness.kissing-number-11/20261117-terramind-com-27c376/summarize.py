"""Summarise the neighbourhood records of all runs: per stage, solves by status, free-set sizes, largest m solved to
optimality, any improvement, moves, distinct configurations visited."""
import json, sys, collections
out = {}
for name in sys.argv[1:]:
    recs = [json.loads(l) for l in open(name)]
    st = collections.defaultdict(lambda: collections.Counter())
    info = collections.defaultdict(lambda: {'max_m_optimal': 0, 'max_free_optimal': 0, 'n': 0, 'improved': 0,
                                            'moves': 0, 'move_attempts': 0, 'move_none_optimal': 0})
    for r in recs:
        lab = r['label']
        stage = 'blocker-set' if lab.startswith('hole') else 'low-conflict' if lab.startswith('lowconf') else 'walk'
        st[stage][r['status']] += 1
        I = info[stage]; I['n'] += 1
        if r['status'] == 'OPTIMAL':
            I['max_m_optimal'] = max(I['max_m_optimal'], r['m']); I['max_free_optimal'] = max(I['max_free_optimal'], r['free'])
        if r.get('improved'): I['improved'] += 1
        if 'move_status' in r:
            I['move_attempts'] += 1
            if r.get('moved'): I['moves'] += 1
            elif r['move_status'] == 'OPTIMAL': I['move_none_optimal'] += 1
    last = recs[-1] if recs else {}
    out[name] = {'records': len(recs), 'status_by_stage': {k: dict(v) for k, v in st.items()},
                 'by_stage': dict(info), 'final_X': last.get('X'), 'distinct_states': last.get('distinct_states'),
                 'last_t': last.get('t')}
json.dump(out, sys.stdout, indent=1)
