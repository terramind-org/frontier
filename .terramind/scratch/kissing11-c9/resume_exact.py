#!/usr/bin/env python3
"""c9 wrapper: resume the recovered c8 ledger without generating pairs."""
import importlib.util
from pathlib import Path

SOURCE = Path('.terramind/scratch/kissing11-c7/resume_exact.py')
spec = importlib.util.spec_from_file_location('c7_solver', SOURCE)
solver = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(solver)
solver.RUN = Path('.terramind/scratch/kissing11-c9')
solver.RUN.mkdir(parents=True, exist_ok=True)
solver.main()
