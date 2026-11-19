"""LRAT certificates for informative UNSAT instances (usage: proofs.py [P1 P2 ...]): CaDiCaL 3.1.0 --lrat on a kept DIMACS file, then
lrat-check (drat-trim repo). Records SHA-256 of CNF and proof, checker verdict and return code; deletes the proof.
Also a negative control: the first proof truncated to half its lines must NOT verify."""
import json, sys, os, subprocess, hashlib, time
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from lib538 import template, Runner
from schur import utc
bases = json.load(open(f'{H}/inputs/bases537.json'))
zen = json.load(open(f'{H}/inputs/zenodo1698.json'))['colors']
os.makedirs(f'{H}/proofs', exist_ok=True)
specs = [
    ('P1_F1.001_F537_N1699_partial', lambda: template(1699, bases['F1.001'], 537, 538, 'partial')),
    ('P2_F1.001_F141_N1699_full', lambda: template(1699, bases['F1.001'], 141, 538, 'full')),
    ('P3_zen_p537_F150_N1699_full', lambda: template(1699, zen[:536], 150, 537, 'full')),
    ('P4_zen_p537_F66_N1699_full', lambda: template(1699, zen[:536], 66, 537, 'full')),
    ('P5_F5.001_F63_N1699_full', lambda: template(1699, bases['F5.001'], 63, 538, 'full')),
]
if len(sys.argv) > 1:  # run only the named specs (second run added P4, P5)
    specs = [s for s in specs if s[0].split('_')[0] in sys.argv[1:]]
def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for ch in iter(lambda: f.read(1 << 20), b''): h.update(ch)
    return h.hexdigest()
R = Runner(f'{H}/logs/proofs_solve.jsonl', f'{H}/out/proofs', workers=1)
LC = f'{H}/bin/drat-src/lrat-check'
log = open(f'{H}/logs/proofs.jsonl', 'a', buffering=1)
for i, (tag, build) in enumerate(specs):
    cnf, prf = f'{H}/proofs/{tag}.cnf', f'{H}/proofs/{tag}.lrat'
    rec = R.one(dict(spec=dict(tag=tag, line='proof'), build=build, timeout=900, seed=1, proof=prf, keep_cnf=cnf))
    out = dict(tag=tag, solve_status=rec.get('status'), solve_rc=rec.get('rc'), solve_seconds=rec.get('seconds'),
               conflicts=rec.get('conflicts'), cnf_sha256=sha(cnf), cnf_bytes=os.path.getsize(cnf))
    if rec.get('status') == 'UNSAT':
        out.update(proof_sha256=sha(prf), proof_bytes=os.path.getsize(prf))
        t = time.time(); p = subprocess.run([LC, cnf, prf], capture_output=True, text=True)
        out.update(check_rc=p.returncode, check_seconds=round(time.time() - t, 2),
                   check_verdict=[l for l in p.stdout.splitlines() if 'VERIFIED' in l][-1:] or p.stdout[-200:])
        if tag.startswith('P1'):
            lines = open(prf).read().splitlines(); half = f'{H}/proofs/trunc.lrat'
            open(half, 'w').write('\n'.join(lines[: len(lines) // 2]) + '\n')
            p2 = subprocess.run([LC, cnf, half], capture_output=True, text=True)
            out.update(neg_control_rc=p2.returncode, neg_control=[l for l in p2.stdout.splitlines() if 'VERIFIED' in l][-1:] or p2.stdout[-200:])
            os.remove(half)
        os.remove(prf)
    os.remove(cnf)
    out['time'] = utc(); log.write(json.dumps(out) + '\n'); print(out, flush=True)
