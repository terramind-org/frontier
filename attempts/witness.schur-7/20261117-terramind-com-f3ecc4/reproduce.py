"""Re-run the call that produced the 1698 colouring: base = first 536 colours of BASE.json (base b1_0014),
537 -> colour 6, mirror x -> 1699 - x on 1..1698, CaDiCaL 3.1.0 binary with seed 781351734 (the same seed also
fixes the variable renaming). Prints the status, the number of violations and whether the result equals
COMPARE.json. usage: reproduce.py BASE.json COMPARE.json OUT.json"""
import sys
from schur import *
base = load(sys.argv[1])[:536]
inst = rowley_modes(1698, base, mirror_S=1699, mirror_range=range(1, 850))
o = solve_bin(inst, 300, seed=781351734, tag='repro')
print('status', o['status'], 'rc', o['rc'], 'seconds', o['seconds'], 'conflicts', o.get('conflicts'))
if o['status'] == 'SAT':
    save(sys.argv[3], o['cols'])
    print('violations', len(violations(o['cols'])), 'identical to compare file', o['cols'] == load(sys.argv[2]))
