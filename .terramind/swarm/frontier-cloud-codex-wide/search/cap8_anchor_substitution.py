"""Deterministic one-anchor substitutions of recorded 12-anchor cap neighborhoods.

The original seed generator is intentionally not advanced here.  Instead, this
program ranks recorded 12-anchor groups by their completed eligible/deletion
ratio, then tries compatible replacements in (ratio, fingerprint, dropped ID,
added ID) order.  Each resulting frozen assignment is fingerprinted before a
restricted solve, so this remains a reproducible neighborhood experiment.
"""
import argparse, hashlib, itertools, json, os, time
from pathlib import Path

os.environ.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csr_matrix

P = [3**k for k in range(7, -1, -1)]
def vec(q): return tuple((q // p) % 3 for p in P)
def ident(v): return sum(x * p for x, p in zip(v, P))
def third(a, b): return ident(tuple((-x-y) % 3 for x, y in zip(vec(a), vec(b))))
def digest(x): return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def direct(s): return all(third(a, b) not in s for a, b in itertools.combinations(sorted(s), 2))

def clauses(fixed, variables):
    pos = {q: i for i, q in enumerate(variables)}; universe = sorted(fixed | set(variables)); seen = set(); out = []
    for i, x in enumerate(universe):
        for y in universe[i+1:]:
            line = tuple(sorted((x, y, third(x, y))))
            if len(set(line)) < 3 or line in seen: continue
            seen.add(line); f = sum(q in fixed for q in line); vs = tuple(sorted(pos[q] for q in line if q in pos))
            if vs:
                assert f <= 2
                out.append((vs, 2-f))
    return sorted(set(out))

def solve(variables, constraints, target, seconds):
    if len(variables) < target: return "CARDINALITY_PRUNED", [], 0.0
    matrix = np.zeros((len(constraints)+1, len(variables))); upper = []
    for row, (vs, bound) in enumerate(constraints): matrix[row, list(vs)] = 1; upper.append(bound)
    matrix[-1, :] = -1; upper.append(-target); started = time.monotonic()
    result = milp(c=np.zeros(len(variables)), integrality=np.ones(len(variables)), bounds=Bounds(np.zeros(len(variables)), np.ones(len(variables))), constraints=LinearConstraint(csr_matrix(matrix), -np.inf*np.ones(len(upper)), np.array(upper)), options={"time_limit": seconds, "presolve": True, "mip_rel_gap": 0})
    status = {0: "SAT", 1: "TIMEOUT", 2: "UNSAT"}.get(int(result.status), "OTHER")
    chosen = [] if result.x is None else [variables[i] for i, value in enumerate(result.x) if value > .5]
    return status, chosen, time.monotonic() - started

def main(a):
    out = Path(a.output); out.mkdir(parents=True, exist_ok=True)
    fixture = json.loads(Path(a.input).read_text()); screen = json.loads(Path(a.screen).read_text())
    by = [set() for _ in range(3)]
    for row in fixture["points"]: by[row[0]].add(ident(row))
    base = set().union(*by); selected = {x["point"] for x in screen["cover_steps"]}; fixed = base-selected; outside = set(screen["insert_b"] + screen["insert_c"])
    assert len(base) == 512 and [len(x) for x in by] == [192, 160, 160] and len(fixed) == 264 and len(selected) == 248 and len(outside) == 565 and direct(base)
    pairs = {}
    for i, x in enumerate(sorted(base)):
        for y in sorted(base)[i+1:]: pairs.setdefault(third(x, y), []).append((x, y))
    prior = set(); groups = {}
    for path in a.prior_ledger:
        for case in json.loads(Path(path).read_text()).get("cases", []):
            fingerprint = case.get("fingerprint")
            if fingerprint: prior.add(fingerprint)
            anchors = case.get("anchors", [])
            if case.get("anchor_count") == 12 and len(anchors) == 12:
                key = tuple(sorted(anchors)); ratio = (case.get("eligible_alternatives", 0), case.get("delete_count", 1))
                groups[key] = min(groups.get(key, (ratio, fingerprint or "~")), (ratio, fingerprint or "~"))
    # Continuation ledgers contribute fingerprints for deduplication but must
    # not become new bases: doing so would alter the r1 deterministic order
    # that the checkpoint cursor names.
    for path in a.dedup_ledger:
        for case in json.loads(Path(path).read_text()).get("cases", []):
            fingerprint = case.get("fingerprint")
            if fingerprint: prior.add(fingerprint)
    def cover_and_eligible(group):
        uncovered = {(q, x, y) for q in group for x, y in pairs.get(q, []) if x in selected or y in selected}; deleted = set()
        while uncovered:
            score = {}
            for _, x, y in uncovered:
                for point in (x, y):
                    if point in selected: score[point] = score.get(point, 0) + 1
            if not score: return None
            point = max(score, key=lambda z: (score[z], -z)); deleted.add(point); uncovered = {item for item in uncovered if point not in item[1:]}
        frozen = base-deleted; eligible = [q for q in sorted(outside) if not any(x in frozen and y in frozen for x, y in pairs.get(q, [])) and (q in group or any(x in deleted or y in deleted for x, y in pairs.get(q, [])))]
        return deleted, frozen, eligible
    ranked = []
    for group, (_, old_fp) in groups.items():
        boundary = cover_and_eligible(group)
        if boundary:
            deleted, _, eligible = boundary; ranked.append((len(eligible), len(deleted), old_fp, group))
    ranked.sort(key=lambda r: (-r[0] / r[1], r[2], r[3]))
    records = []; seen = set(); candidate_index = 0; screened = 0; first_unvisited = None
    checkpoint_dir = out / "cases"
    checkpoint_dir.mkdir(exist_ok=True)
    def append(record):
        """Persist each classified substitution before advancing the stream."""
        records.append(record)
        path = checkpoint_dir / f"{len(records):04d}.json"
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        os.replace(temporary, path)
    # A checkpoint points to the next valid substitution.  Reconcile it with
    # the fully ordered, compatibility-filtered stream; never approximate by
    # a raw loop index, which could replay or skip a screened candidate.
    resume = None
    if a.resume_base is not None:
        if a.resume_dropped is None or a.resume_added is None:
            raise ValueError("resume cursor requires base, dropped, and added")
        resume = (a.resume_base, a.resume_dropped, a.resume_added)
    resume_found = resume is None
    for eligible0, deleted0, old_fp, group in ranked:
        for dropped in sorted(group):
            for added in sorted(outside-set(group)):
                if vec(added)[0] != vec(dropped)[0]: continue
                mutated = tuple(sorted((set(group)-{dropped}) | {added}))
                if not direct(set(mutated)): continue
                identity = (old_fp, dropped, added)
                if not resume_found:
                    if identity != resume:
                        continue
                    resume_found = True
                if candidate_index >= a.max_cases:
                    first_unvisited = {"base_fingerprint": old_fp, "dropped": dropped, "added": added}; break
                candidate_index += 1; screened += 1; boundary = cover_and_eligible(mutated)
                if boundary is None:
                    append({"base_fingerprint": old_fp, "dropped": dropped, "added": added, "classification": "MIXED_INVARIANT_PRUNED"}); continue
                deleted, frozen, eligible = boundary; ratio_pass = len(eligible)*125 > 60*len(deleted)
                record = {"base_fingerprint": old_fp, "dropped": dropped, "added": added, "anchors": list(mutated), "anchor_count": 12, "delete_count": len(deleted), "eligible_alternatives": len(eligible), "yield_numerator": len(eligible), "yield_denominator": len(deleted)}
                if not ratio_pass:
                    record.update(classification="YIELD_PRUNED"); append(record); continue
                variables = sorted(deleted) + sorted(set(eligible)); constraint_list = clauses(frozen, variables); target = len(deleted)+1
                fp = digest({"frozen": sorted(frozen), "variables": variables, "target": target}); record.update(fingerprint=fp, frozen=len(frozen), variables=len(variables), clauses=len(constraint_list), target=target)
                if fp in prior:
                    record.update(classification="DUPLICATE_PRIOR"); append(record); continue
                if fp in seen:
                    record.update(classification="DUPLICATE_RUN"); append(record); continue
                seen.add(fp); planted = set(deleted); record["planted_ok"] = all(sum(variables[i] in planted for i in vs) <= k for vs, k in constraint_list)
                small = min(8, len(variables)); mismatches = 0
                for mask in range(1 << small):
                    trial = frozen | {variables[i] for i in range(small) if mask >> i & 1}; encoded = all(sum((mask >> i) & 1 for i in vs if i < small) <= k for vs, k in constraint_list); mismatches += direct(trial) != encoded
                status, witness, elapsed = solve(variables, constraint_list, target, a.seconds); cap = frozen | set(witness); valid = status == "SAT" and len(cap) >= 513 and direct(cap)
                record.update(classification=status, elapsed_seconds=elapsed, selected=len(witness), candidate_size=len(cap) if status == "SAT" else None, direct_candidate_valid=valid, small_assignments=1 << small, small_mismatches=mismatches)
                if valid: (out/f"candidate-{len(records)}.json").write_text(json.dumps({"points": [list(vec(q)) for q in sorted(cap)]}, indent=2) + "\n")
                append(record)
            if first_unvisited: break
        if first_unvisited: break
    if not resume_found:
        raise ValueError("resume cursor was not found in the deterministic substitution stream")
    counts = {name: sum(r.get("classification") == name for r in records) for name in ["YIELD_PRUNED", "MIXED_INVARIANT_PRUNED", "DUPLICATE_PRIOR", "DUPLICATE_RUN", "CARDINALITY_PRUNED", "SAT", "UNSAT", "TIMEOUT"]}
    toy = {"old_size": 1, "new_size": 2, "old_valid": direct({0}), "new_valid": direct({P[0], 2*P[0]}), "gain": 1}; assert toy["old_valid"] and toy["new_valid"]
    manifest = {"method": "recorded 12-anchor single-substitution restricted neighborhoods; original generator cursor remains parked", "fixture_sha256": hashlib.sha256(Path(a.input).read_bytes()).hexdigest(), "screen_sha256": hashlib.sha256(Path(a.screen).read_bytes()).hexdigest(), "scope": {"fixed":264,"optional":813,"planted_selected":248,"target_total":513}, "strict_yield_benchmark": "125 * eligible > 60 * deletions", "prior_fingerprint_count": len(prior), "recorded_group_count": len(ranked), "resume_cursor": {"base_fingerprint": a.resume_base, "dropped": a.resume_dropped, "added": a.resume_added, "found": resume_found}, "screened": screened, "counts": counts, "best_verified_size": 512, "baseline_direct_valid": direct(base), "planted_direct_valid": direct(fixed|selected), "toy_positive_gain": toy, "first_unvisited": first_unvisited, "original_generator_cursor_parked": 197, "cases": records}
    (out/"ledger.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    (out/"SHA256SUMS").write_text(hashlib.sha256((out/"ledger.json").read_bytes()).hexdigest() + "  ledger.json\n")
    print(json.dumps({"screened": screened, "counts": counts, "first_unvisited": first_unvisited}, sort_keys=True))
if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--input", required=True); p.add_argument("--screen", required=True); p.add_argument("--output", required=True); p.add_argument("--prior-ledger", action="append", default=[]); p.add_argument("--dedup-ledger", action="append", default=[]); p.add_argument("--seconds", type=float, default=75); p.add_argument("--max-cases", type=int, default=48); p.add_argument("--resume-base"); p.add_argument("--resume-dropped", type=int); p.add_argument("--resume-added", type=int); main(p.parse_args())
