-- (f) Forges the environment: adds `solution` with a bogus proof (`True.intro`) while the kernel's
-- type checker is switched off. The source pre-check rejects it (run_cmd, skipKernelTC); built without
-- the pre-check, the declaration lands in the .olean and Check.lean's kernel replay must reject it.
import FormalConjectures.ErdosProblems.«1»

open Lean Elab Command in
set_option debug.skipKernelTC true in
run_cmd liftCoreM do
  let stmt := (← getConstInfo `Erdos1.erdos_1.variants.weaker).type
  addDecl <| .thmDecl
    { name := `OpenProblemsAttempt.solution, levelParams := [], type := stmt,
      value := mkConst ``True.intro }
