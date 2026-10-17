# 65: Pot C rim-ordering repair — extend the ticket-27 cure

**What to deliver:** C Bl_0 outlines without teleports — gate recovery + E2E above zero.

**Answers:** E1

**Blocked by:** 64 (teleports on all 4 C pieces: C01 3/105mm, C02 3/113mm, C03 1/14mm, C04 2/48mm; ORIG 0; gates 0/1/4/0/16 vs 34–73; overlap kills 128/1714; C02 axle 59° miss; do NOT relax SingleOverlapTest@100/RP/CheckGraph-150) + 27 (T24-pattern walk repair cured A's 34 teleports → 0; same family) + 42 (T42 skip-appends precedent on B).

**Status:** results-in — Arm-S does NOT repair (teleports intact, E2E 0/3+0/3 ×3); mechanism measured below

**Starting position:** same disease as A-ticket-26 (mid-run teleports ≤113mm from the rim walk) — apply the 27-cure family to C's four Bl_0 files: walk repair that skips decorative appends / reorders teleported runs. Plus C02 axle-mode check (59° miss — finder-side per tickets 12–16, or walk-caused? measure first). Bundle reference: pota39 C bundle (read-only); work in scratch copies. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** land ONLY with teleport count → 0 (or measured floor) AND gate recovery toward ORIG per-edge AND E2E above 0 ×3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [ ] Walk-repair arms on C Bl_0, one variable each
- [ ] C02 axle-mode verdict (walk-caused vs finder-caused)
- [ ] Gate + E2E rerun ×3 or measured why-not
- [ ] Job IDs + sacct states

**Successor:** roll the walk-repair wherever teleports recur (E/I/J forests dwarf ORIG — same disease suspected).


**Handoff note:** `send_message` to parent session-7d9d268d-87e7-40f2-aa27-49f1843537fca was attempted once and returned "subagent unavailable" — parent session appears settled. Result lives in this Comments section + Status line; nothing committed.
## Comments (worker, 2026-10-17 — COMMIT NOTHING; lead to commit)

**Verdict: Arm-S re-segmentation is a no-op repair — the C null stands measured at 0/3+0/3 x3. Category 1 (method genuinely failed on these rims) per T64 still binds; the fix did not move any input the assembly reads.**

**0. Ship note (script bug fixed in-ticket).** Staged `run_pota65_stage_AC.sbatch` could never run: line 94 expanded `${GTSTUB}` (container-inner var) in outer-shell context under `set -u` -> `GTSTUB: unbound variable`. Prior workers' jobs 33276121/33276122/33276123 + my first submit 33276165 all FAILED 1:0 within seconds on this line. One-line fix in the pota65 file only (cp source `${GTSTUB}` -> `${GTSTUB_HOST}`; backup `.bak_GTSTUBfix`), `bash -n` clean, resubmitted. No other tickets' files touched.

**1. Bundle autopsy (Arm-S changed headers only).** Fixed Bl_0 vs p39-fresh Bl_0 (login-node probes): same point SET and same ORDER on all 4 pieces (sorted equality + order equality; C01 n=402 both). Only the `#` segment headers changed (C01: 13 segs -> 4 segs). The 3 teleports sit MID-segment (fixed seg 40-191, max jump 105.0mm inside it) — not isolated at boundaries. Axes carried over byte-identical from fresh (C01 2 lines, C02 2 lines, C03 EMPTY, C04 3 lines). Reader consequence (verified in `asm/class/data_structure.cpp` + `feature_matching.cpp`): header field 3 = 0 in both bundles -> `is_seg_rim_` false -> kd-tree takes ALL points in file order, matching uses full range — the regrouped headers are invisible to the binary. Teleport counts fixed vs ORIG: C01 3 (105.0/65.5/56.8), C02 3 (112.7/68.6/5.8), C03 1 (14.2), C04 2 (48.2/6.6) vs ORIG 0/0/0/0 — identical to T64 fresh. Deliverable "teleport count -> 0" NOT met (measured floor = fresh values, no reduction).

**2. C02 axle-mode verdict.** Fixed C02 axis file = fresh bytes: L1 61.0 deg off ORIG (undirected; T64 records 59.17 deg / run-42.52 deg), L2 42.5 deg off. Miss persists UNADDRESSED (axes predate any rim change). Walk-vs-finder not separable from this bundle (rim positions unchanged), so T64's recording stands: finder-side count/landscape-miss family, secondary defect — the two good-axle pieces (C01 0.06 deg, C04 1.28 deg per T64) seat 0 anyway. C03 axis EMPTY (still refused, still off).

**3. Gate recovery: none, by construction.** Gate inputs (rim positions at GT seating) are unchanged -> T64 fresh numbers stand without recompute: per-edge 0/34, 1/72, 4/40, 0/73, 16/55; SingleOverlapTest@100 kills 1-3 (128) and 1-4 (1714) stand. Do NOT relax SingleOverlapTest@100 / RP / CheckGraph-150 (unchanged from T64).

**4. E2E x3 same-binary (cure-potA @ bffefb6, k=5/b=3, LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK 4x per job, all jobs sacct COMPLETED 0:0, polled directly):**

| job | A_orig | A_fresh | C_orig | C_fixed (forest/pruned) |
|---|---|---|---|---|
| 33276193 | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 0/3+0/3 (307/7) |
| 33276355 | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 0/3+0/3 (307/7) |
| 33276356 | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 0/3+0/3 (307/10) |

Bit-identical tallies x3 (deterministic binary): vehicle + A-fresh + C ORIG controls all green in the same runs; C_fixed == fresh null to the digit (T64: 307/8; T39 unflagged 307/7, 307/9). C_fixed T holds T_0,T_1,T_3 only — P3 still unplaced (refusal path unchanged).

**5. Renders (eye-checked).** `artifacts/pota65/pota65_seating_C_fixed_R1.png` (script `artifacts/pota65/p65_render.py`, fetch `artifacts/pota65/R1/`): left = C_fixed E2E seating, scattered tangle, seated centroids 36-64mm off GT (C01 63.5, C02 37.2, C04 36.2); right = same rims at GT, coherent ring crossed by the long teleport chords (the defect seen directly). Render resolves the scale being tested (whole-rim seating, cm-scale fling).

**6. Jobs (sacct State/ExitCode, polled directly).** 33276121/33276122/33276123 FAILED 1:0 (pre-fix script, prior workers); 33276165 FAILED 1:0 (same line, mine pre-fix); 33276193 / 33276355 / 33276356 COMPLETED 0:0 (post-fix; 3/3 repeats). RUNDIRs: `/data/gpfs/projects/punim2657/sfs_main/pota65_run_{33276193,33276355,33276356}/`; fetch tgz `pota65_fetch.tgz` in each. Spartan leftovers otherwise: `.bak_GTSTUBfix` next to the sbatch (in-ticket dir only).

**Successor proposal for lead:** a real walk repair must REORDER points (T27-cure family: skip decorative appends / reorder teleported runs), not regroup headers — header-only changes are provably invisible to this binary (info_index 0 path). Until Bl_0 file-order teleports -> 0 AND axes recomputed (C02 mode + C03 refusal), ceiling stays 0. Zero ORIG points used anywhere (44-asterisk rule kept).