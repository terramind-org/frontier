#!/usr/bin/env python3
"""Exact, single-writer screening of the preserved c10 triple-pool ledger.

The source ledger is copied before this program writes.  It never draws from
the seeded triple stream and only changes rows already recorded as unvisited.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
C10 = ROOT / '.terramind/scratch/kissing11-c10/triple_exchange.py'
OUT = Path(__file__).resolve().parent
LEDGER = OUT / 'triple_ledger.sqlite'
EXPECTED = '5c35df0e69d6385cab9699f92f6235527425d85b0f5828e350cc8ae18e5c3fca'

spec = importlib.util.spec_from_file_location('c10', C10)
c10 = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(c10)


def read_pool(key: str) -> tuple[int, set[int]]:
    members = {int(x) for x in key.split(',')}
    return sum(1 << x for x in members), members


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=1440)
    ap.add_argument('--per-pool', type=float, default=0.15)
    ap.add_argument('--batch', type=int, default=4096)
    args = ap.parse_args()
    if hashlib.sha256(LEDGER.read_bytes()).hexdigest() != EXPECTED:
        raise SystemExit('copied ledger does not match c10 checkpoint')
    begin = time.monotonic()
    # These controls exercise the exact branch-and-bound independently.
    c10.controls()
    P, Q, CP, CQ, B, select, order = c10.load()
    assert len(P) == 604 and len(CP) == 6116 and len(select) == 5156
    M = [sum(1 << x for x in b) for b in B]
    # Every nonempty blocker set has one designated anchor.  A direction can
    # only be eligible if its anchor belongs to the deletion pool, so this is
    # an exact index that avoids re-testing the entire shell for every pool.
    anchors: list[list[int]] = [[] for _ in range(604)]
    empty: list[int] = []
    for i, blockers in enumerate(B):
        (empty if not blockers else anchors[blockers[0]]).append(i)
    db = sqlite3.connect(LEDGER)
    db.execute('pragma journal_mode=WAL')
    db.execute('pragma synchronous=FULL')
    assert db.execute('pragma quick_check(1)').fetchone()[0] == 'ok'
    first = db.execute("select d from pools where status='unvisited' order by d limit 1").fetchone()
    expected_first = '1,2,9,10,21,22,67,101,102,113,117,201,283,284,291,292,465,534,542,548,557,558,566,594'
    assert first and first[0] == expected_first
    # Independent direct set/mask equality on the deterministic lexical prefix.
    for (key,) in db.execute("select d from pools where status='unvisited' order by d limit 32"):
        mask, members = read_pool(key)
        direct = [i for i, blockers in enumerate(B) if set(blockers) <= members]
        indexed = empty[:] + [i for b in members for i in anchors[b] if M[i] & ~mask == 0]
        assert sorted(direct) == sorted(indexed)
    deadline = begin + args.seconds
    processed = 0
    candidates: list[dict[str, object]] = []
    while time.monotonic() < deadline:
        rows = db.execute("select d,n from pools where status='unvisited' order by d limit ?", (args.batch,)).fetchall()
        if not rows:
            break
        updates = []
        for key, n in rows:
            if time.monotonic() >= deadline:
                break
            mask, members = read_pool(key)
            elig = empty[:] + [i for b in members for i in anchors[b] if M[i] & ~mask == 0]
            # The anchor partition proves this has no duplicates and includes
            # every full-shell direction whose blockers are contained in D.
            if len(elig) <= n:
                updates.append(('pruned', len(elig), None, key))
            else:
                adj = [set() for _ in elig]
                for x, u in enumerate(elig):
                    for y in range(x):
                        v = elig[y]
                        if c10.comp(CP[u], CQ[u], CP[v], CQ[v]):
                            adj[x].add(y); adj[y].add(x)
                best, timed = c10.clique(adj, min(deadline, time.monotonic() + args.per_pool))
                picked = [elig[x] for x in best]
                status = 'timeout' if timed else 'exhaustive'
                updates.append((status, len(best), json.dumps(picked), key))
                if len(best) > n:
                    candidates.append({'pool': key, 'deleted': n, 'directions': picked})
                    with db:
                        db.executemany('update pools set status=?,clique=?,detail=? where d=?', updates)
                    raise SystemExit('GAIN ' + json.dumps(candidates[-1], sort_keys=True))
            processed += 1
        if updates:
            with db:
                db.executemany('update pools set status=?,clique=?,detail=? where d=?', updates)
        if len(rows) < args.batch:
            break
    counts = dict(db.execute('select status,count(*) from pools group by status'))
    first = db.execute("select d from pools where status='unvisited' order by d limit 1").fetchone()
    out = {
        'source_ledger_sha256': EXPECTED,
        'fixture_sha256': c10.FIXTURE,
        'candidate_order_sha256': order,
        'full_shell_directions': len(CP),
        'controls': 'planted K4; exhaustive 32768 labelled six-vertex graphs; direct set/mask/index equivalence on 32 lexical unvisited pools',
        'processed': processed,
        'counts': counts,
        'first_unvisited': first[0] if first else None,
        'candidates': candidates,
        'elapsed_seconds': time.monotonic() - begin,
    }
    (OUT / 'summary.json').write_text(json.dumps(out, sort_keys=True, indent=2) + '\n')
    print(json.dumps(out, sort_keys=True))


if __name__ == '__main__':
    main()
