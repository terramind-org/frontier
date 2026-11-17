"""Exact maximum (weighted) independent set with OR-Tools CP-SAT. Edge constraints plus a greedy clique cover
(each clique gives sum x <= 1). Returns (status_name, best_value, bound, chosen indices, wall seconds)."""
import time
import numpy as np
from ortools.sat.python import cp_model

def clique_cover(n, adj):
    """greedy cover of the edges by cliques; adj: list of sets"""
    cliques = []
    covered = set()
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    for v in order:
        for u in sorted(adj[v], key=lambda u: -len(adj[u])):
            if (min(u, v), max(u, v)) in covered:
                continue
            K = [v, u]; cand = adj[v] & adj[u]
            while cand:
                w = max(cand, key=lambda w: len(adj[w] & cand))
                K.append(w); cand &= adj[w]
            for i in range(len(K)):
                for j in range(i + 1, len(K)):
                    covered.add((min(K[i], K[j]), max(K[i], K[j])))
            cliques.append(K)
    return cliques

def solve(n, edges, weights=None, time_limit=60.0, workers=2, forbid=None, hint=None, cover=True, seed=0):
    t0 = time.time()
    adj = [set() for _ in range(n)]
    for i, j in edges:
        adj[i].add(j); adj[j].add(i)
    m = cp_model.CpModel()
    x = [m.NewBoolVar(f'x{i}') for i in range(n)]
    if cover and n <= 30000:
        for K in clique_cover(n, adj):
            m.AddAtMostOne([x[i] for i in K])
    else:
        for i, j in edges:
            m.AddBoolOr([x[i].Not(), x[j].Not()])
    if forbid is not None:
        idx, cap = forbid
        m.Add(sum(x[i] for i in idx) <= cap)
    w = weights if weights is not None else [1] * n
    m.Maximize(sum(int(w[i]) * x[i] for i in range(n)))
    if hint is not None:
        for i in range(n):
            m.AddHint(x[i], 1 if i in hint else 0)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_workers = workers
    s.parameters.random_seed = seed
    st = s.Solve(m)
    name = s.StatusName(st)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = [i for i in range(n) if s.Value(x[i])]
        return name, int(round(s.ObjectiveValue())), int(round(s.BestObjectiveBound())), chosen, time.time() - t0
    return name, None, int(round(s.BestObjectiveBound())) if st != cp_model.MODEL_INVALID else None, [], time.time() - t0
