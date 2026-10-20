# 193 - Thin-loop roll-out: Pot J

Status: landed (lead 2026-10-20: bar-HOLD verified -- 7/10+13/18 x3 exact bit-identical set; J03-seating hypothesis REFUTED, J03 placed-but-wrong -> unplaced; J needs no further rim work)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Apply the 185 thin-then-walk cure to every doubled rim edge of Pot J, bundle, and E2E x3 vs this pot's established bar (cite the prior ticket that set it).

## Method (worker runs FULL chain, SSH works -- Host spartan)
1. Census: for each rim piece, test for doubling with key-free signals (closure distance, arc vs plan perimeter, D-token count per the 179 recipe). Name which edges are doubled.
2. Cure: apply the 185 v3 recipe (thin TRUE strip to centreline, uniform 1.8mm resample, verbatim walk_m144) to each doubled edge. Gate each loop: closure <=2.0, single wrap, rim-truth med where an author key exists (check-only).
3. Bundle: rebuild this pot's bundle with ONLY the cured Bl_0 slots changed (byte-proofs, only-changed-diff, veto-absence record, same guards as 180/186).
4. E2E: upload, login-node build (expect BUILD DONE), sbatch x3 + laptop-side poll per AGENTS.md, sacct tallies. Own a falsifier in advance.

## Constraints
Laptop + Spartan both allowed. COMMIT NOTHING (worker). No repo sources touched, dataset read-only. Finish by writing the self-contained result to this ticket's Comments + final output -- never via send_message (child-to-parent messaging does not exist).

## Acceptance
Per-piece doubling census + per-loop gates + bundle byte-proofs + E2E tallies x3 (Total/pruned/sherd/edge) vs the pot's bar + honest verdict (pass / honest negative with the refusing numbers).

## Required evidence
Ticket Comments + final output: census numbers, loop gates, md5s, job IDs, per-run tallies, verdict.

## Comments (worker, 2026-10-20 -- J03 thin-loop cure, E2E x3 COMPLETE; COMMIT NOTHING)

**Verdict: HOLDS the 92 bar (7/10+13/18 x3 exact, bit-identical seated set) but the J03-seating hypothesis is REFUTED: J03 went from placed-but-wrong to unplaced. Rim doubling was NOT what kept J03 out (search-basin miss stands, as 92 suspected). No further input-side iteration for J03 without new evidence.**

**0. Boundary kept.** Dataset read-only; no repo sources touched (assembler never entered); tickets 39-192 read-only (numbers quoted from their Comments); bundle verified read-only before copy (`md5sum -c` vs 95 manifest, 24 files OK); vehicle HEAD `bffefb6` asserted in-job; nothing committed; only this Comments section added (plus Status flip).

**1. Doubling census (login-node numpy, key-free 179 signals: closure / arc-vs-plan-perimeter / D-tokens@0.15; plan perim = angle-sorted PCA-plane polygon; ORIG evidence-only check).** Assembler-facing Bl_0 slots of the bundle of record (`pota92_bundle_J_SXC` + 95 in-place resample):

| piece | slot Bl_0 | n | arc | closure | gaps>5 | D-tokens | ORIG arc | rim med | verdict |
|---|---|---|---|---|---|---|---|---|---|
| J01 | control, untouched | 201 | 408.4 | 1.90 | 1 | 3 | 315.0 | 1.15 | SINGLE (closed, 3 tokens; 1x29.9mm jump = pre-existing interior curl per 92; seats) |
| J02 | SXC (=fresh Bl_1) | 139 | 247.5 | 1.80 | 0 | 3 | - | 0.76 | SINGLE, clean |
| J03 | fresh, untouched | 371 | 842.1 | 25.36 | 11 | 34 | 339.6 | 0.89 | **DOUBLED** (arc 2.48x ORIG, open, 34 tokens; 179 signature) -> CURED |
| J04 | SXC resampled | 181 | 321.2 | 1.80 | 0 | 3 | 332.4 | 0.72 | SINGLE (arc 0.97x ORIG; ratio-0.48 anomaly is PCA-projection shape, all 179 primary signals single; seats) |
| J05 | SXC resampled | 144 | 255.7 | 1.80 | 0 | 2 | - | 0.68 | SINGLE, clean |
| J06 | SXC resampled | 130 | 230.6 | 1.80 | 0 | 2 | - | 0.65 | SINGLE, clean |
| J07 | SXC resampled | 113 | 198.9 | 1.79 | 0 | 3 | - | 0.39 | SINGLE, clean |
| J08 | control | 66 | 124.2 | 1.32 | 0 | 4 | - | 0.59 | SINGLE, clean |
| J09 | no-GT, untouched | 211 | 326.5 | 41.34 | 5 | 24 | (file) 131.9 | 3.16 | DOUBLED but EXCLUDED (no GT -> scoring-inert; thin-loop fallback closure 5.94/med 3.44/cov 9/74 fails the ticket's own <=2.0 gate; installing it would violate the gate for zero measurable gain) |
| J10/J11/J12 | SXC resampled | 72/54/55 | 125.7/95.3/96.6 | <=1.79 | 0 | 2-3 | - | 0.36/0.41/0.43 | SINGLE, clean |

Falsifier for the census (owned in advance, NOT triggered for J03): no Bl_0 besides J03/J09 shows closure>2 + tokens>=10 + gaps>0. Maxima among the ten singles: closure 1.92, tokens 4, gaps 1 (J01's pre-existing curl jump).

**2. Cure (185 v3 verbatim, laptop-side).** Input = J03 fresh doubled walk itself (371 dots) as the strip (no TRUE-strip bag exists for J; bin-averaging needs only a doubled covering). PCA-plane 360-bin average (209 non-empty) -> angle-sort -> 8x Laplacian smooth (poly 319.5mm -> N1=178 @1.8mm, cap 240) -> uniform resample -> verbatim `walk_m144` (`.scratch/pota176_repro/p176_lib.py`) over 6 v3 seeds. Pick = min-arc among gated (seed5): **n=178, arc 316.8 (ORIG 339.6, -7% smoothing shrink, same qualification class as 185's -5%), closure 1.78 (<=2 PASS), gaps>5 0, back=0 single wrap, D-tokens 3 (top 11:175, longest run 86), rim-truth med 0.96 (fresh doubled 0.89, HOLDS), cov 165/189, uniqSta 166/189, skip 15 (one jog at walk order ~123, bridged).** Eye-checked: `artifacts/pota193/p193_01_thin_J03.png` (green centreline rides the gray strip; kink-sector stray at right x~40 same class as 185/180 qualifications), `p193_02_order_trace_J03.png` (one clean circuit, markers 0/59/118 even), `p193_03_station_sweep_J03.png` (monotonic single wrap, wrap at start + jog at ~123). Key-free declaration holds (no author data in the rule; ORIG used CHECK-ONLY for rim-truth/station sweep). J09 cure attempted identically: centreline poly 129.2 ~= ORIG-file arc 131.9 in size but med 3.44/cov 9/74 (fresh loop tracks a different arc, no-GT-unverifiable) and best closure 5.94 -> NO gated loop exists -> NOT installed (ticket gate <=2.0 forbids the fallback).

**3. Bundle (`pota193_bundle_J_THIN` = SXC base + ONLY J03-Bl_0 replaced).** New Bl_0: walk xyz + nearest-fresh-donor normals (renormalized) + donor curvature (179 row-10: non-gating); segs rescaled 371->178 `[1-17][18-35][36-65][66-178]`, all flag 0 (veto-absence OK), header `(4,178,0)`, 178 rows (header math OK), LF-only, md5 `242bf342dc8616577bb7dba86361faa1`. Build `BUILD DONE`: base intact vs 95 manifest (24 files) before copy; walk md5 `95c7a6a7...` verified on arrival; only-changed-diff PROVEN (`Pot_J_Piece_03_Breakline_0.pcd` the sole change, 23 same); Spartan manifest `pota193_J_THIN_BL_md5.txt` (in-job guard target). Scripts: `.scratch/pota193_repro/p193_cure.py` (census+cure, rerunnable), `p193_make_pcd.py` (pure-numpy donor; scipy absent on login node), `p193_build.py`, `p193_J03_thin_walk.npy` (178x3), staged + Spartan `pota193_repro/`. One worker porting note (honest): first `p193_build` attempt died on missing scipy (fixed pure-numpy, byte-identical md5); first sbatch pointed at `prep/pota92_bundle_J_THIN` (sed kept 92's prefix) so 3 submitted jobs ran with a dead J_THIN mount (VOID batch 33484433/35/36 -- A/J_orig arms valid, J_THIN arm never ran; same `|| echo intact` guard trap as 92's void batch, now hardened with a fail-closed `[ -d ... ] || exit 1` line).

**4. E2E x3 (fixed sbatch `run_pota193_stage_AJ.sbatch`, cure-potA @ bffefb6 asserted in-job, k=5/b=3 shim, POT_J overlay, STEPS 12/8, LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK 4x per job, sacct-direct polling, all COMPLETED 0:0):**

| job (sacct COMPLETED 0:0) | A_orig | A_fresh | J_orig | J_THIN |
|---|---|---|---|---|
| 33486061 (~27min) | 124/70 8/8+15/15 | 420/119 8/8+15/15 | 731/196 8/11+16/21 | 885/146 7/10+13/18 |
| 33486065 | 124/70 8/8+15/15 | 420/119 8/8+15/15 | 731/197 8/11+16/21 | 885/143 7/10+13/18 |
| 33486064 | 124/70 8/8+15/15 | 420/119 8/8+15/15 | 731/196 8/11+16/21 | 885/145 7/10+13/18 |

Bar cited (tickets 92 + 95): J_SXC/J_RES 7/10+13/18 x3 exact; ORIG J 8/11+16/21 (731/196-200); A 8/8+15/15. Controls green all 3 runs (A exact, J_orig 8/11+16/21 in-vehicle).

**5. Identities (p92 logic verbatim, 0.35 rad/50mm, `pota193_fetch.tgz` x3 on laptop `artifacts/pota193/`).** J_THIN seated set = **[1,2,4,5,6,7,10] via the same 13 edges** (all <0.15 rad/<35mm) in ALL 3 runs -- bit-identical set AND edge family to 92's SXC (061 vs 065 edge angles bit-exact; 064 same set, sub-degree wobble). Piece 3 (J03): **unplaced -- no T_2to_2 file in any run** (was placed-but-wrong under the doubled rim). Pieces 8/11/12 missed both arms (small-rim frontier, n=66/54/55); piece 9 no GT (excluded). FALSIFIER TRIGGERED as owned: J03 still unseated -> thin loop is not the gate for J03.

**6. What it means (plain language).** Pot J's rims were already fixed by the earlier slot-swap except piece 3, whose edge was traced twice over itself (open loop, 34 direction-tokens vs the author's 3). Ironing it to a single clean ring (185 recipe) worked as geometry (closed, uniform, hugs the author ring) and the assembler noticed: it proposed 7x more candidate joins (Total 122->885, same flood as C01's 40->155). But piece 3 still does not join -- it went from a wrong join to no join. So the doubled edge was never what kept piece 3 out; the blocker is downstream in the search (where the assembler looks), exactly the contextual-miss 92 diagnosed. Nothing regressed (every previously seated piece still seats, x3); piece 3 needs assembly-lane work, not rim work. J needs no further rim roll-out: 10 of 12 edges are verified single, J09 is uncurable scoring-inert, J03 is exonerated.

**7. Evidence.** Spartan `pota193_repro/` (cure/build/sbatch/manifest/identity scripts, 3 slurm outs) + `pota92/prep/pota193_bundle_J_THIN/` (bundle) + `sfs_main/pota193_run_{33486061,33486064,33486065}/` (binaries, snapshots, `pota193_fetch.tgz`); void runs `pota193_run_{33484433,33484435}/` + cancelled `33484436` on record, excluded from x3. Laptop `.scratch/pota193_repro/` (census/cure/make/build scripts, walk npy, fresh+ORIG rims, logs) + `artifacts/pota193/` (3 thin/order/sweep renders for J03 + same 3 for J09's refused fallback + 3 fetch tgzs).

Status: results-in
