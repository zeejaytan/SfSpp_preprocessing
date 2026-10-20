# 208 worker Comments draft (2026-10-20, second dispatch) -- FOR LEAD TO PASTE into ticket Comments; seating section PENDING stage job

## Gate-clear (lead, laptop, before dispatch)

Lead shelved the 2 live Spartan-main edits (stash@{0} T24/T27 vendored +22 lines, stash@{1} root sphere-calibration; both named pre-E2E shelf 2026-10-20), verified main@e2e-pristine-base == origin/main, `git pull --ff-only` OK, and designated the fresh worktree /data/gpfs/projects/punim2657/sfs-e2e-pristine @ b1ed4d1 (branch e2e-pristine) as the build/run checkout. Worker was told NOT to pop the stashes.

## Build PASS (login node, worker-verified)

Toolchain: Spartan login-node cmake is 4.0.3-only (no PCL/CGAL); compute nodes lack /usr/bin/cmake and system PCL too (probe job 33504637). Build used the easybuild Apptainer 1.3.3 + pcl_191_nurbs.sif (cmake 3.26.5, PCL 1.9, CGAL) -- same container class as every prior pipeline build. `cmake` configure PASS, `cmake --build -j4` (nohup build-e2e-pristine.log, 116 lines) PASS: mesh 22:27 + edge 22:28, zero errors (grep -c -i error = 0). Binaries: sfs-e2e-pristine/build-e2e/{MeshPreprocessingHeadless (22:27), EdgeLineExtractionHeadless (22:28)}. No source touched (STOP rule held; zero behaviour change). First sbatch attempt 33504601 FAILED at configure (login cmake picked, no PCL) -- superseded by the container build, do not retry.

Proof the binaries came from the pristine tree (all re-verified 22:51, saved .scratch/pota208_repro/pota208_pipe_guards_reverified.txt; the pipe slurm .out was lost by a worker rm+symlink mistake -- guards re-run against unchanged sources, HEAD still b1ed4d1):

- worktree HEAD b1ed4d1ff7630ded7019375460c262ff8cf32447, tracked tree clean (only ?? build-e2e/ + sbatches)
- `grep -c SFS-T` = 0 in both headless cpps; cure-hunk grep (ticket14_append_patch_rims|T24|T27) = 0; SFS-B/SFS-M = 0/0
- edge binary strings: SFS-T24|T27 = 0

## Pipe PASS (job 33504975, COMPLETED 0:0 in 2:43)

First attempt 33504936 FAILED 1:0 in 3s on a worker guard that was over-broad (edge-markers=1: the lone hit is the pristine AUTHOR definition `void getPointsOnFracturedSurface` at line 2554 -- spec 0da8891 carries the identical def at line 2564, zero call sites in the live file: keep-class dead definition, no behaviour). Guard refined to subtract the `^void getPointsOnFracturedSurface` definition line, resubmitted. Recipe: pota28 pipe mechanics (fresh TREE pota208_pipe/, meshes copied from LIVE Dataset/Mesh/Pot_A (8 objs), ORIG Axes/GT/Mesh copied into bundle per 28/06 precedent -- see Axes note below).

- meshes=8; 16/16 surfaces (p01 64k/56k down to p08 6k/5k pts; per-piece counts in mesh_stage.log)
- 16/16 breaklines, ALL Bl1 non-empty (59-165 pts) -- carried risk 207#1 NOT materialised, no new ticket
- segment headers all `# <n> <m> 0` valid; edge log carries 64 benign PCL `Failed to find match for field normal_*` warnings only (XYZ->PointNormal defaults, expected)
- Bundle v0: /data/gpfs/projects/punim2657/pota208_bundle_v0/SfS_pp (16 breaklines + 16 surfaces + 8 axes + 8 mesh + Ground Truth); md5 .scratch/pota208_repro/pota208_bun_v0_md5.txt (regenerated in place after a second worker symlink mistake deleted the first copy -- bundle itself untouched, values re-recorded from the intact bundle)

## D0-D3 chain (diagnosis-gated pass-through; job p208diag 33505417 COMPLETED 0:0)

Per-piece fresh-Bl0 vs ORIG-Bl0 (file-order arc, median step, big-jump count, S0-face-mix), .scratch/pota208_repro/p208_diagnosis_bl0.txt:

| piece | fresh n | ORIG n | fresh arc/med/big | ORIG arc | ratio | S0mix |
| 01 | 207 | 208 | 370.1/1.80/0 | 373.3 | 0.99 | 0.00 |
| 02 | 172 | 169 | 306.2/1.80/0 | 301.7 | 1.02 | 0.01 |
| 03 | 160 | 156 | 284.9/1.80/0 | 278.4 | 1.02 | 0.01 |
| 04 | 154 | 151 | 275.9/1.80/0 | 269.5 | 1.02 | 0.00 |
| 05 | 152 | 147 | 270.2/1.80/0 | 262.2 | 1.03 | 0.00 |
| 06 | 153 | 150 | 272.1/1.80/0 | 268.0 | 1.02 | 0.01 |
| 07 | 68 | 65 | 119.4/1.80/0 | 115.9 | 1.03 | 0.00 |
| 08 | 64 | 60 | 112.2/1.80/0 | 106.0 | 1.06 | 0.00 |

Decision (worker, lead-overturnable): the D0-D3 chain RAN as characterisation and its gates do NOT fire anywhere, so the honest composition is PASS-THROUGH -- bundle v0 IS the D-composed bundle. D2 doubling gate (C01 fired at 1.82x + 34 stray tokens) fires nowhere (max ratio 1.06); D1 split has nothing to split (S0mix <= 0.01, clean singles); D3 recovery has no stuck walk to fix (big-jumps 0, med 1.80mm uniform = author parity). NO blanket densify: density already matches ORIG (med 1.80 both arms); densifying would deviate from every proven bundle format without a diagnosed need, and the 194/195/196 regression precedent (force-applied thin-then-walk collapses clean-single seating: B 6/9-level to 2/9, D 21-22/27 to 10-11/27, all x3, controls green) says forcing the recipe onto clean rims DAMAGES seating. Restore-to-clean precedent (185v3: 79.3% cut only where tokens diagnosed) agrees.

## Axes note (standing decision applied)

Bundle carries ORIG Axes per the 28/06 precedent (06 lead revision: the E2E runs on the authors' NURBS/ORIG axes; MATLAB axes as-is = do not port/replace/re-tune -- the axis computation was not re-run, the author axes were staged). No MATLAB job was submitted in this run.

## Fresh-layout notes (carried risk 207#3)

- worktree: /data/gpfs/projects/punim2657/sfs-e2e-pristine @ b1ed4d1 (branch e2e-pristine), build dir build-e2e/ (binaries), build log build-e2e-pristine.log
- pipe tree: /data/gpfs/projects/punim2657/pota208_pipe (mesh/edge stage logs, Segments/, Temp/, Dataset/ residue)
- bundle: /data/gpfs/projects/punim2657/pota208_bundle_v0/SfS_pp + md5
- assembly: /data/gpfs/projects/punim2657/pota208_e2e (src @ b56bc80 detached, sbatches, run dirs)
- Do NOT follow guide .mds / patches/SOURCE_ANCHOR.md (deleted vendored layout). Do NOT use build_new/ residue in the worktree (not this run's).

## Seating stage-1 (job 33505533, CANCELLED 0:15 at 11:13 -- fresh arm too slow for 12h, see below)

- ORIG arm DONE: Sherd 8/8 + Edge 15/15 (control VALID, not void), container exit 0, pruned 124/70 (identical to restore job 33502035), snapshot L_orig_Result_snapshot captured, all shim proofs green (LINK-SHIM-OK / LINK-FORKMAIN-ABSENT-OK / DRIVER-SHIM-OK / GTSTUB-SKIPPED-OK). sacct: CANCELLED (worker scancel after ORIG arm done).
- Fresh arm (Total 253 vs ORIG 124 -- denser forest): reached beam Step 4 of 7+ (ORIG needed 7 steps / 290 lines) at ~1.2h/step vs ORIG ~0.45h/step; projected ~3.6h more with only ~47 min of allocation left (scontrol TimeLimit-extension denied). Worker cancelled rather than burn allocation on a doomed arm. Partial log preserved: pota208_run_33505533/L_fresh_binary.log (216 lines, Step 4 merges).
- Fresh-only rerun SUBMITTED as job 33505947 (run_pota208_freshonly.sbatch: same recipe, fresh arm only, 24:00 limit; sapphire MaxTime 30 days). Build ~45 min + seating ~8-9h expected.

## Seating DONE (job 33505947, COMPLETED 0:0; fresh-only, 24h limit)

- Fresh-v0 tally: Sherd 7/8 (87.5%) + Edge 9/15 (60%). Total 253, pruned 70. Container exit 0; SNAPSHOT-T-COUNT=8 gate passed; L_fresh_Result_snapshot captured (T_0to_0..T_7to_7 + seated OBJs/edgelines + Acc.txt; T files + Acc filed .scratch/pota208_repro/seat_fresh_snapshot/). sacct: 33505947 COMPLETED 0:0.
- FRESH-VERDICT: diagnostic below bar (8/8+15/15 not met). The bar items not met: E2E 8/8+15/15 on the fresh arm (ORIG control in the same recipe reads 8/8+15/15, so the shortfall is in the fresh bundle/search, not the scorer).
- Strict diagnostic (5deg/10mm, robust Kabsch on pieces 2-8 excluding the p1 outlier; .scratch/pota208_repro/strict_fresh208.txt; script strict_render_208.py): 4/8 PASS (3,5,6,7). p1 is the assembly's single misplaced sherd (112.2deg/271mm off GT after robust alignment). Pieces 2-8 all within 3.4deg/13mm; pieces 2,4,8 miss only on translation (10.3/12.7/12.0mm vs 10mm line) -- the same borderline flavour as the restore proof (ORIG strict 6/8 with P5 10.5/P7 10.1mm over; restore-fresh strict 7/8 with P5 12.1mm over).
- Render: .scratch/pota208_repro/seat_fresh208_vs_gt.png (worker eye-check: coherent vessel, 7 coloured pieces hug the GT grey shell; p1/red scattered in the middle).
- Acc.txt records `Time : 591986 Sec` (unit unclear; wall seating was ~8h) -- recorded verbatim, not interpreted.
- Ledger comparison vs fork-era thin-default E2E (194 B / 195 D / 196 A, all x3, controls green; edge-level tallies): B 6/9->2/9, D 21-22/27->10-11/27, A 22/27->5-11/27 (thin-then-walk forced onto clean rims = collapse). Ours (sherd/edge level): fresh 7/8 + 9/15, strict 4/8 -- NO collapse (better than 06's fresh 4/8+3/15 on the same metric), but below the 8/8+15/15 bar. Pass-through composition does not damage seating; the remaining gap (p1 misplaced + 6 lost edges) is a search/selection matter on the fresh forest (253 hyps vs ORIG 124), not a rim-fidelity matter (rims verified within +0-4 pts / 6% arc of ORIG).
