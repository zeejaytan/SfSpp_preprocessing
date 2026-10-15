# 05: sfs_axes Python port

**What to build:** a cross-platform pure-Python `sfs_axes/` package replacing the MATLAB axis chain, emitting 8 ORIG-compatible Pot A axis files that the untouched `ReadAxis` loop loads.

**Answers:** E1

**Blocked by:** 04-surface-interior-first (fresh-surface axes reported separately; proof order ORIG-surfaces first).

**Status:** results-in — port≡MATLAB proven, anchor-parity refuted; production uses NURBS axes; E1 write-back still to do

- [ ] Spike: confirm per-file gaps G1–G8 from task-3 plan against root `AxisExtraction/` pins (extract_axis cc4fa5af, read_surfaces 443e6355, run_potsac 7822954e); stale vendored copies out of scope
- [ ] Package `sfs_axes/` (io_surfaces, plucker, pottmann, cao, robust, potsac, refine, io_axes, cli) + regression test; output `Pot_A_Piece_0i_Axis.xyz` position-first, byte-compatible with `data_path.h:1391-1426`
- [ ] Acceptance on ORIG surfaces first: direction ≤5°, radial/axial ≤2.0mm, 8/8 load, rim agreement ≥7/8, ORIG 15/15 strict-gate held; then fresh surfaces reported separately with shift disclosed
- [ ] Zero MATLAB licence consumed; laptop-only (numpy/scipy), no sbatch

## Comments (pota-axes-builder, 2026-10-15)

**Built:** `sfs_axes/` (plucker, robust, pottmann, cao, refine, potsac,
io_surfaces, io_axes, cli, `__init__`) + `tests/test_regression_pota.py`
(8/8 PASS) + acceptance script `.scratch/pota-repro/notes/accept_axes_orig.py`.
Working-tree fidelity (pins cc4fa5af/443e6355/7822954e are not valid git
objects; built from working tree incl. ff40fc9 fixes): literal ports incl.
MATLAB quirks (degenerate 0/1 inlier count, cost[0]*1.1 prune, F-order
flattens, block damping kron(diag([1 1]),outer)); seeded RNG; paper step=10
default with --adaptive flag.

**Acceptance on ORIG surfaces: FAIL on axis match (decisive), rest noted.**
8/8 files load, format ReadAxis-compatible (round-trip test). Best-cost
across 3 seeds per R3, both step regimes:
- paper-10%: best angles 10-86deg off NURBS anchors, radial errs 100s of mm
  (e.g. p01 10.1deg/76mm; p03 79.7deg/328mm).
- MATLAB-adaptive: best angles 35-81deg off (e.g. p01 45deg/266mm).
- Winners' raw Cao costs run 5-70x LOWER than anchors' -> the chain's cost
  optimum on these inputs is far from the NURBS anchors. Bar unreachable by
  the reference algorithm itself, not (only) by the port.
- Rim proxy inconclusive by construction (only 2/8 coherent segments even
  under anchor axes -> proxy stricter than checker; acceptance UNDECIDED).
- Gate-(b) frames disagree (consequence of axis mismatch). ORIG-vs-ORIG
  15/15 control re-run verbatim: 15/15, min/med/max 0.09/0.77/1.30mm (inputs
  intact).

**Provenance findings for session:** (1) pins not valid git objects;
working blobs 6cc1737b/ea68b4f9/146483b6. (2) Method-2 LM refine is a silent
no-op in MATLAB too (scalar biaxial R vs per-point J rows: grad=J'*err throws
at optimize_using_lm.m:36, caught -> initial returned); shipped axes =
MLESAC+Pottmann+dedup. Port reproduces identically. (3) GM robustifier on the
whole-cloud scalar saturates at 2.0 for every candidate (MATLAB same
formula); ranking is coarse (differs only past ~1% raw gaps). (4) Triggs
scaling subtlety: J *= sqrt(rho'), err *= sqrt(rho')/D (not the same
factor). (5) Assembly Pot_A_Piece_0i_Axis.xyz are pointer files naming
NURBS axes -> PotSAC outputs never shipped; anchors come from the NURBS
pipeline. (6) Wall normals already consistent (means dot -0.913); layout
[x y z nx ny nz] verified, normals unit.
