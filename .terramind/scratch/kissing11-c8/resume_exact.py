#!/usr/bin/env python3
"""c8 wrapper: reuse c7's deterministic solver with a separate run ledger."""
import importlib.util
import sys
from pathlib import Path

SOURCE = Path('.terramind/scratch/kissing11-c7/resume_exact.py')
spec = importlib.util.spec_from_file_location('c7_solver', SOURCE)
solver = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(solver)
solver.RUN = Path('.terramind/scratch/kissing11-c8')
solver.RUN.mkdir(parents=True, exist_ok=True)
solver.main()
