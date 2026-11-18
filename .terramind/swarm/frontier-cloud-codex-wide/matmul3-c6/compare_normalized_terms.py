#!/usr/bin/env python3
"""Compare per-term projective triads without claiming orbit inequivalence."""
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location("screen", "seven_term_laderman.py")
screen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(screen)

def triad_key(term):
    return tuple(tuple(str(x) for x in screen.normalize(vector)) for vector in term)

old_path = Path("../matmul3-c4/perminov-cr58-cn122.json")
new_path = Path("laderman-frontier-witness.json")
old = screen.decode(new_path)  # direct JSON decoder

# Perminov uses a sparse-program representation; import its retained decoder.
other_spec = importlib.util.spec_from_file_location("perminov", "../matmul3-c5/six_term_neighbors.py")
other = importlib.util.module_from_spec(other_spec)
other_spec.loader.exec_module(other)
perminov = other.decode(old_path)
laderman = old
kp, kl = set(map(triad_key, perminov)), set(map(triad_key, laderman))
report = {
  "comparison": "termwise projective normalization: each factor vector divided by its first nonzero entry; term order ignored",
  "perminov_sha256": hashlib.sha256(old_path.read_bytes()).hexdigest(),
  "laderman_sha256": hashlib.sha256(new_path.read_bytes()).hexdigest(),
  "perminov_terms": len(perminov), "laderman_terms": len(laderman),
  "shared_normalized_triads": len(kp & kl),
  "only_perminov": len(kp - kl), "only_laderman": len(kl - kp),
  "conclusion": "not identical under term permutation and independent per-factor scaling; this is not a proof of GL(3)^3 orbit inequivalence",
}
Path("normalized-term-comparison.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print(json.dumps(report, sort_keys=True))
