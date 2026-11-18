#!/usr/bin/env python3
"""Exact, frozen-core exchanges in the affine 713-point pool.

The previous greedy schedule consumed the first 256 pair specifications.  This
program works only on the remaining *distinct frozen cores*.  A domain freezes
CF-236 outside the union of two anchors' blocker endpoints and asks, by a
complete deterministic DPLL search, whether its compatible local pool can add
one point beyond the 236-point incumbent.  The DPLL result is a restricted
domain result, never a certificate about the full 713-point pool.
"""
import argparse
import hashlib
import itertools
import json
import os
import platform
import time
from pathlib import Path

from cap7_affine_pool_pb import ROOT, enumerate_lines, fixture_controls, rebuild_pool, sha
from cap7_hittingset_search import blockers, third, valid
from cap7_seeded_pool_exchange import EXPECTED_POOL, forbidden_pairs, hash_ids


def atomic(path, value):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    tmp.replace(path)


def domain_catalog(base, points, ids, rows, inherited):
    """Return remaining unique frozen cores ranked by eligible/free ratio.

    Tie-break: descending eligible alternatives per removable endpoint, then
    descending eligible count, ascending frozen-core hash, then anchor ids.
    """
    old_hashes = {s['neighborhood_sha256'] for s in inherited['domain_summaries']}
    earlier = {tuple(p) for p in json.loads((ROOT / 'raw' / 'cap7_hittingset_result.json').read_text())['minimum_points']}
    base_set = set(base)
    for p in points:
        if p not in base_set and len(blockers(base, p)) == 11:
            earlier.add(p)
    novel = []
    for row in rows:
        p = tuple(row['point'])
        nonidentity = any(not o.endswith(':id') and 'retained' not in o for o in row['origins'])
        if p not in base_set and p not in earlier and nonidentity:
            novel.append(p)
    endpoint = {p: frozenset(i for q in blockers(base, p) for i in q) for p in novel}
    # Compatibility with a frozen core can be evaluated from a single
    # precomputed blocker table.  Re-enumerating C(220,2) pairs for each of
    # the 53k pair specifications was needlessly expensive and would make the
    # ranking itself consume the search budget.
    base_index = {p: i for i, p in enumerate(base)}
    all_blockers = {p: blockers(base, p) for p in points if p not in base_set}
    # Same pair ordering as the exhausted schedule, but collapse identical
    # frozen assignments before doing expensive compatibility work.
    raw = []
    for a, b in itertools.combinations(novel, 2):
        shared = len(endpoint[a] & endpoint[b])
        if shared:
            free = endpoint[a] | endpoint[b]
            raw.append((-shared, len(free), ids[a], ids[b], a, b, hash_ids(free)))
    raw.sort()
    seen = set(old_hashes)
    remaining = []
    for neg_shared, _, aid, bid, a, b, h in raw:
        if h in seen:
            continue
        seen.add(h)
        free = endpoint[a] | endpoint[b]
        compatible = tuple(
            p for p in points
            if (p in base_index and base_index[p] in free)
            or (p not in base_index and not any(i not in free and j not in free
                                                for i, j in all_blockers[p]))
        )
        eligible = len(compatible) - len(free)
        remaining.append({
            'anchor_ids': [aid, bid], 'anchor_points': [list(a), list(b)],
            'free_indices': sorted(free), 'free_endpoint_count': len(free),
            'shared_endpoint_count': -neg_shared, 'frozen_core_hash': h,
            'compatible_ids': [ids[p] for p in compatible],
            'compatible_pool_count': len(compatible), 'eligible_alternatives': eligible,
        })
    remaining.sort(key=lambda d: (-d['eligible_alternatives'] / d['free_endpoint_count'],
                                  -d['eligible_alternatives'], d['frozen_core_hash'], d['anchor_ids']))
    return novel, raw, remaining, old_hashes


def exact_target(candidate_ids, triples, target, deadline):
    """Complete DPLL for cardinality plus at-most-two triple clauses.

    Returns UNKNOWN only at its hard deadline.  UNSAT is from exhaustive
    search; no external proof certificate is claimed.
    """
    local = {v: i for i, v in enumerate(candidate_ids)}
    clauses = []
    incidence = [[] for _ in candidate_ids]
    for tri in triples:
        if all(v in local for v in tri):
            c = tuple(sorted(local[v] for v in tri))
            ix = len(clauses); clauses.append(c)
            for v in c: incidence[v].append(ix)
    n = len(candidate_ids)
    # Branch high-degree first; every branch makes one permanent assignment.
    order = sorted(range(n), key=lambda v: (-len(incidence[v]), candidate_ids[v]))
    state = [-1] * n  # -1 unassigned, 0 false, 1 true
    nodes = 0
    timed = False

    def dfs(pos, chosen):
        nonlocal nodes, timed
        nodes += 1
        if (nodes & 1023) == 0 and time.monotonic() >= deadline:
            timed = True; return None
        if chosen + (n - pos) < target:
            return None
        if pos == n:
            return list(state) if chosen >= target else None
        v = order[pos]
        # True first creates a model quickly when one exists.
        state[v] = 1
        bad = False
        for ci in incidence[v]:
            if sum(state[x] == 1 for x in clauses[ci]) == 3:
                bad = True; break
        if not bad:
            ans = dfs(pos + 1, chosen + 1)
            if ans is not None or timed:
                state[v] = -1; return ans
        state[v] = 0
        ans = dfs(pos + 1, chosen)
        state[v] = -1
        return ans

    model = dfs(0, 0)
    return ('SAT' if model is not None else ('UNKNOWN' if timed else 'UNSAT'), model, len(clauses), nodes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=1500.0)
    ap.add_argument('--domains', type=int, default=24)
    ap.add_argument('--start-rank', type=int, default=0,
                    help='first ranked new frozen-core domain; enables no-replay continuation')
    ap.add_argument('--raw-dir', type=Path, default=ROOT / 'raw')
    args = ap.parse_args(); args.raw_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic(); deadline = started + args.seconds
    base, points, ids, rows, baseline_ids = rebuild_pool()
    triples = enumerate_lines(points, ids)
    assert len(points) == 713 and len(triples) == 20907 and sha({'points': rows}) == EXPECTED_POOL
    inherited = json.loads((ROOT / 'raw' / 'cap7_seeded_pool_exchange_result.json').read_text())
    assert inherited['resume'] == {'domain_index': 256, 'restart': 0, 'state': 'done'}
    assert inherited['restarts_completed'] == 32768
    controls = fixture_controls(base, points, ids, triples)
    # Non-vacuous local line control and planted frozen-core baseline control.
    line = next(t for t in triples)
    controls.update({'nonvacuous_line_fixture_ids': list(line),
                     'nonvacuous_line_fixture_three_selected_violates': True,
                     'planted_cf236_assignment_size': 236,
                     'planted_cf236_assignment_valid': valid(base)})
    novel, raw, catalog, old_hashes = domain_catalog(base, points, ids, rows, inherited)
    out = {'format': 'cap7-disjoint-exact-exchange-v1', 'pool_sha256': EXPECTED_POOL,
           'pool_size': len(points), 'line_constraints': len(triples),
           'baseline_size': 236, 'baseline_valid': valid(base), 'controls': controls,
           'inherited_completed_neighborhoods': 256, 'inherited_restart_count': 32768,
           'old_frozen_assignment_fingerprints': len(old_hashes),
           'novel_affine_anchor_count': len(novel), 'all_shared_blocker_pairs': len(raw),
           'remaining_distinct_frozen_assignments': len(catalog),
           'ranking': 'eligible alternatives/free removable endpoints desc; eligible desc; frozen hash asc; anchor ids asc',
           'restrictions': 'each result fixes CF-236 outside one new two-anchor blocker-endpoint set; not a full-pool query',
           'full_pool_status': 'unresolved: no full witness or independently checkable certificate',
           'domains_budget': args.domains, 'start_rank': args.start_rank, 'seconds_budget': args.seconds, 'records': [],
           'domain_results': [], 'cardinality_prunes': 0, 'solver_unsat': 0, 'solver_unknown': 0,
           'solver_sat': 0, 'best_directly_checked_size': 236, 'timed_out': False}
    for rank, d in enumerate(catalog[args.start_rank:args.start_rank + args.domains], args.start_rank):
        core = tuple(p for i, p in enumerate(base) if i not in set(d['free_indices']))
        target_local = 237 - len(core)
        item = {**d, 'rank': rank, 'frozen_core_size': len(core), 'local_target': target_local}
        if len(d['compatible_ids']) < target_local:
            item['status'] = 'CARDINALITY_PRUNED'; out['cardinality_prunes'] += 1; out['domain_results'].append(item); continue
        status, model, local_lines, nodes = exact_target(d['compatible_ids'], triples, target_local, deadline)
        item.update({'local_line_constraints': local_lines, 'dpll_nodes': nodes, 'status': status,
                     'proof_artifact': None, 'independently_checked_certificate': False})
        if status == 'SAT':
            chosen = core + tuple(points[i] for i, x in zip(d['compatible_ids'], model) if x == 1)
            item['candidate_size'] = len(chosen); item['candidate_direct_line_free'] = valid(chosen)
            item['candidate_ids'] = [ids[p] for p in chosen]
            out['solver_sat'] += 1
            if valid(chosen) and len(chosen) > out['best_directly_checked_size']:
                out['best_directly_checked_size'] = len(chosen); out['records'].append(item)
        elif status == 'UNSAT': out['solver_unsat'] += 1
        else:
            out['solver_unknown'] += 1; out['timed_out'] = True
        out['domain_results'].append(item)
        if status == 'UNKNOWN': break
    done = len(out['domain_results'])
    next_rank = args.start_rank + done
    out['unvisited_rank'] = next_rank if next_rank < len(catalog) else None
    out['unvisited_frozen_assignment_fingerprint'] = (catalog[next_rank]['frozen_core_hash'] if next_rank < len(catalog) else None)
    out['elapsed_seconds'] = time.monotonic() - started
    out['platform'] = platform.platform(); out['python'] = platform.python_version()
    out['source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    atomic(args.raw_dir / 'cap7_disjoint_exact_exchange_control.json', controls)
    atomic(args.raw_dir / 'cap7_disjoint_exact_exchange_result.json', out)
    print(json.dumps({k: out[k] for k in ('remaining_distinct_frozen_assignments','cardinality_prunes','solver_unsat','solver_unknown','solver_sat','best_directly_checked_size','unvisited_rank','elapsed_seconds')}, sort_keys=True))


if __name__ == '__main__':
    main()
