/-
frontier proof checker, phase 2.

Usage: lake env lean --run Check.lean <module> <problemDecl> <proof|disproof>

Judges an attempt whose compiled module (normally `Attempt.Solution`) is already on the search path.
It never elaborates attempt source. It reads the module's .olean data, builds an environment from the
module's *imports only* (pristine packages), and replays every constant of the attempt module through the
kernel with `Lean.Environment.replay` (core `Lean.Replay`, the same mechanism as the toolchain's
`leanchecker`, formerly lean4checker). All further checks run on that replayed environment, so nothing
the attempt's .olean says about itself (environment extensions, precomputed axiom tables, attributes) is
trusted: only constants the kernel has just accepted.

Checks, in order (the first failure is the verdict's reason):
1. every direct import of the module is on the allow-list (same list as check-attempt.sh);
2. the problem declaration exists in the imports and is not (re)defined by the attempt module;
3. the attempt module declares no `unsafe` or `partial` constants (replay would skip them);
4. kernel replay of every attempt constant succeeds;
5. `OpenProblemsAttempt.solution` exists in the attempt module and is a theorem;
6. its type is definitionally equal (`Meta.isDefEq`, default transparency) to the problem's type,
   or to `¬ <type>` for a disproof, with the same universe parameters (on a mismatch, both types are
   shown, pretty-printed in an environment of the pristine imports with their extensions loaded (this
   runs the imports' `initialize` code, never the attempt module's); the raw term when that fails);
7. `Lean.collectAxioms` ⊆ {propext, Classical.choice, Quot.sound}.

Prints exactly one JSON line matching `VerdictResult` (src/schema.ts). Exit 0 whenever a verdict was
produced; non-zero only for internal errors (missing .olean, unreadable manifest, bad arguments).
-/
import Lean

open Lean Meta

namespace FrontierCheck

/-- Import prefixes an attempt may use. Kept in sync with `ALLOWED_IMPORT_ROOTS` in check-attempt.sh. -/
def allowedImportRoots : List String :=
  ["Mathlib", "FormalConjectures", "FormalConjecturesForMathlib", "FormalConjecturesUtil",
   "Batteries", "Aesop", "Qq", "Plausible", "Init", "Std"]

def allowedAxioms : List Name := [``propext, ``Classical.choice, ``Quot.sound]

def solutionName : Name := `OpenProblemsAttempt.solution

def importAllowed (m : Name) : Bool :=
  match m.components.head? with
  | some (.str .anonymous root) => allowedImportRoots.contains root
  | _ => false

def axiomReason (ax : Name) : String :=
  if ax == ``sorryAx then "uses sorry"
  -- Lean 4.33's native_decide adds a per-use axiom `<decl>._native.native_decide.ax_<n>`; older
  -- toolchains went through Lean.ofReduceBool / Lean.trustCompiler.
  else if ax == ``Lean.ofReduceBool || ax == ``Lean.trustCompiler ||
      (ax.components.contains `_native && ax.components.contains `native_decide) then "uses native_decide"
  else s!"uses axiom {ax}"

/-- Parse a dotted name the way Lean prints it, honouring «guillemets» (e.g. `Foo.«1».bar`). -/
def parseName (s : String) : Name :=
  let rec go (cs : List Char) (cur : String) (inGuil : Bool) (acc : Name) : Name :=
    match cs with
    | [] => if cur.isEmpty then acc else .str acc cur
    | c :: rest =>
      if inGuil then
        if c == '»' then go rest cur false acc else go rest (cur.push c) true acc
      else if c == '«' then go rest cur true acc
      else if c == '.' then go rest "" false (if cur.isEmpty then acc else .str acc cur)
      else go rest (cur.push c) false acc
  go s.toList "" false .anonymous

structure Ctx where
  toolchain : String
  fcCommit : String
  target : String

def verdict (c : Ctx) (result summary : String) (axioms : Array Name) (reason? : Option String) : Json :=
  let lean := Json.mkObj <|
    [("toolchain", toJson c.toolchain), ("fc_commit", toJson c.fcCommit), ("target", toJson c.target),
     ("axioms", toJson (axioms.map toString))] ++
    (match reason? with | some r => [("reason", toJson r)] | none => [])
  Json.mkObj [("checker", "lean"), ("result", toJson result), ("summary", toJson summary), ("lean", lean)]

def reject (c : Ctx) (reason : String) (axioms : Array Name := #[]) : Json :=
  verdict c "rejected" s!"rejected: {reason}" axioms (some reason)

/-- `rev` of the formal_conjectures package from the lake-manifest.json in the working directory. -/
def readFcCommit : IO String := do
  let j ← IO.ofExcept <| Json.parse (← IO.FS.readFile "lake-manifest.json")
  let pkgs ← IO.ofExcept <| j.getObjValAs? (Array Json) "packages"
  for p in pkgs do
    if (p.getObjValAs? String "name").toOption == some "formal_conjectures" then
      return ← IO.ofExcept <| p.getObjValAs? String "rev"
  throw <| IO.userError "formal_conjectures is missing from lake-manifest.json"

def runCore (env : Environment) (x : CoreM α) : IO α := do
  let ctx : Core.Context := { fileName := "<frontier-check>", fileMap := default, maxHeartbeats := 0 }
  let (a, _) ← x.toIO ctx { env }
  return a

/-- A type for the mismatch message: pretty-printed in the first environment where that works, else the
raw term; whitespace collapsed and capped at 900 characters. -/
def showType (envs : List Environment) (e : Expr) : IO String := do
  let mut shown : Option String := none
  for env in envs do
    if shown.isNone then
      try
        let s ← runCore env <| MetaM.run' (do return toString (← ppExpr e))
        unless s.isEmpty || s.startsWith "failed to pretty print" do shown := some s
      catch _ => pure ()
  let s := " ".intercalate (((shown.getD (toString e)).splitOn "\n").map (·.trimAscii.toString))
  return if s.length > 900 then (s.take 900).toString ++ "…" else s

/-- For the mismatch message only: the environment of the attempt's (allow-listed, pristine) imports
with their environment extensions loaded, so that types print with their notation. Loading extensions runs
the imports' `initialize` code, which `lean --run` does not enable by default; the attempt module is never
part of this import state, so none of its code runs. -/
unsafe def displayEnvImpl (s : ImportState) (imports : Array Import) : IO Environment := do
  enableInitializersExecution
  withImporting <| finalizeImport s imports {} 0 false true (isModule := true)

@[implemented_by displayEnvImpl]
opaque displayEnv (s : ImportState) (imports : Array Import) : IO Environment

def judge (c : Ctx) (module problem : Name) (disproof : Bool) : IO Json := do
  -- Read every part of the module (exported, server, private) like leanchecker does.
  let mFile ← findOLean module
  unless (← mFile.pathExists) do
    throw <| IO.userError s!"object file '{mFile}' of module {module} does not exist"
  let mut fnames := #[mFile]
  let sFile := OLeanLevel.server.adjustFileName mFile
  if (← sFile.pathExists) then
    fnames := fnames.push sFile
    let pFile := OLeanLevel.private.adjustFileName mFile
    if (← pFile.pathExists) then fnames := fnames.push pFile
  let parts ← readModuleDataParts fnames
  let some (mod, _) := parts[0]? | throw <| IO.userError "failed to read module data"
  let some (last, _) := parts.back? | throw <| IO.userError "failed to read module data"

  -- 1. imports
  for imp in mod.imports do
    unless importAllowed imp.module do
      return reject c s!"imports {imp.module}, which is not on the allow-list"

  -- Environment of the imports only: pristine packages, no attempt data.
  let (_, s) ← importModulesCore mod.imports |>.run
  let env ← finalizeImport s mod.imports {} 0 false false (isModule := true)

  -- The most private part subsumes the others.
  let mut newConstants : Std.HashMap Name ConstantInfo := {}
  for name in last.constNames, ci in last.constants do
    newConstants := newConstants.insert name ci

  -- 2. problem declaration
  if newConstants.contains problem then
    return reject c s!"the attempt module defines {problem} itself; it must prove the imported statement"
  let some probInfo := env.find? problem
    | return reject c s!"problem declaration {problem} is not in the attempt's imports"

  -- 3. unsafe / partial constants are skipped by replay, so refuse them outright.
  for (n, ci) in newConstants.toList do
    if ci.isUnsafe then return reject c s!"declares unsafe constant {n}"
    if ci.isPartial then return reject c s!"declares partial constant {n}"

  -- 4. kernel replay
  try discard <| env.replay newConstants
    catch e => return reject c s!"kernel replay failed: {e}"

  -- The replayed environment only exposes the kernel's view, which `Environment.find?` and MetaM
  -- cannot see for the newly added constants. So, for the Meta-level checks below, import the module
  -- itself on top of the same import state (extensions not loaded, so none of the module's own
  -- environment-extension data is used) and confirm its constants are exactly the ones just replayed.
  let (_, sFull) ← importModulesCore #[{ module }] |>.run s
  let fullEnv ← finalizeImport sFull #[{ module }] {} 0 false false (isModule := true)
  for (n, ci) in newConstants.toList do
    let some ci' := fullEnv.find? n
      | throw <| IO.userError s!"{n} disappeared between replay and import"
    unless ci'.levelParams == ci.levelParams && ci'.type == ci.type && ci'.value? == ci.value? do
      throw <| IO.userError s!"{n} differs between replay and import"

  -- 5. the solution theorem
  unless newConstants.contains solutionName do
    return reject c s!"{solutionName} is not declared in the attempt module"
  let some solInfo := fullEnv.find? solutionName
    | return reject c s!"{solutionName} is not declared in the attempt module"
  unless solInfo matches .thmInfo _ do
    return reject c s!"{solutionName} must be a theorem"

  -- 6. statement match
  if solInfo.levelParams != probInfo.levelParams then
    return reject c s!"universe parameters differ: solution has {solInfo.levelParams}, \
      problem has {probInfo.levelParams}"
  let target := if disproof then mkNot probInfo.type else probInfo.type
  let ok ← runCore fullEnv <| MetaM.run' (isDefEq solInfo.type target)
  unless ok do
    -- For display only: an environment of the (pristine) imports with their extensions loaded, so the
    -- types print with notation. The attempt module is not part of it, and nothing here affects the verdict.
    let displayEnv? ← try some <$> displayEnv s mod.imports catch _ => pure none
    let envs := displayEnv?.toList ++ [fullEnv]
    let want ← showType envs target
    let got ← showType envs solInfo.type
    return reject c s!"type mismatch: {solutionName} must have type\n  {want}\nbut has type\n  {got}"

  -- 7. axioms, collected by walking bodies in the replayed environment
  let axioms := (← runCore fullEnv (collectAxioms solutionName)).qsort (·.toString < ·.toString)
  let bad := axioms.filter (!allowedAxioms.contains ·)
  unless bad.isEmpty do
    return reject c (", ".intercalate (bad.toList.map axiomReason)) axioms
  let what := if disproof then "disproves" else "proves"
  let axs := if axioms.isEmpty then "none" else ", ".intercalate (axioms.toList.map toString)
  return verdict c "verified" s!"proof checked: {solutionName} {what} {problem} (axioms: {axs})" axioms none

end FrontierCheck

open FrontierCheck in
def main (args : List String) : IO UInt32 := do
  match args with
  | [moduleStr, problemStr, kind] =>
    unless kind == "proof" || kind == "disproof" do
      IO.eprintln s!"kind must be proof or disproof, got {kind}"
      return 2
    initSearchPath (← findSysroot)
    let c : Ctx := {
      toolchain := (← IO.FS.readFile "lean-toolchain").trimAscii.toString
      fcCommit := ← readFcCommit
      target := if kind == "disproof" then "negation" else "statement" }
    let j ← judge c (parseName moduleStr) (parseName problemStr) (kind == "disproof")
    IO.println j.compress
    return 0
  | _ =>
    IO.eprintln "usage: lake env lean --run Check.lean <module> <problemDecl> <proof|disproof>"
    return 2
