# c12 independent replay of the audited c11 window certificate

This directory records a fresh independent verification of the retained
`[49,60) -> 10` certificate from `../sort18-c11-recovery/`.  It did not rerun
CaDiCaL or alter the encoded formula.

## Inputs verified before replay

`sha256sum -c ../sort18-c11-recovery/MANIFEST.sha256` accepted every retained
object.  Concatenating the eight committed proof chunks in numeric order
reproduced compressed-proof SHA-256
`a345e63e01719fd6932e430662ba8888ea0a8122af02f38f63bdd12a30e0ed69`.
Decompression reproduced the CNF SHA-256
`b45d2ea1f3e34dd710d6044758590fbe9a87eece72ed08b3698fff5c943eb5aa`
and DRAT SHA-256
`052ad0f8701b637fe044b97a809dfebd81116ce2261d78f9699e71440a4734a8`.

## Independent check

The checker binary's recorded usage is in `checker-version-and-usage.log`.
The command in `checker.command` used `taskset -c 0` and a 1,350-second
external timeout.  It exited 0 after 384 wall-clock seconds and its final
output includes `s VERIFIED`; see `checker.log`, `checker.exit`, and
`checker.wall-seconds`.

The large decompressed CNF and DRAT are working files and are deliberately
not staged.  The replay derives them losslessly from the compact c11 bundle.
