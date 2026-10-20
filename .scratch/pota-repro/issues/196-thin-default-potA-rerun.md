# 196 - Default chain on Pot A: control must hold

Status: landed (lead 2026-10-20: REGRESSION verified -- thinned A_196 5/8+3/15, 4/8+1/15 x2 vs 8/8+15/15 bar, controls green; GLOBAL scramble incl. untouched pieces)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Pot A is the lane control (8/8+15/15). Run the FULL default chain (densify -> split -> thin+walk -> bundle -> E2E x3) on Pot A's rims and prove the control still holds. The default cannot ship if it moves the control.

## Method (worker runs FULL chain, SSH works -- Host spartan)
0. Densify (143): measure spacing per A loop; true mesh-sampled densify only if coarser than ~1.8mm (midpoints FORBIDDEN per 111/146); else record + close vacuous.
1. Split (175 rule, read 175-two-walks-two-slots.md): mesh-observable only, no ORIG. Expect one face cloud per clean single; two faces = new evidence.
2. Thin: 185 v3 per face cloud. Gate: closure <=2.0, single wrap, rim-truth med check-only.
3. Falsifier (own in advance): any loop worsening rim-truth by >0.5mm vs input is REFUSED, not bundled.
4. Bundle: ONLY changed Bl_0 slots (byte-proofs, only-changed diff, veto-absence, 180/186 pattern).
5. E2E: same vehicle cure-potA @ bffefb6 (verify HEAD -- Pot A-diagnosis changes live here); same-binary ORIG control must reproduce 8/8+15/15 or VOID. sbatch x3 + laptop-side poll per AGENTS.md. Bar = 8/8+15/15 (cite owning ticket). Verdict MATCH or REGRESSION (name piece + numbers).

## Constraints
Laptop + Spartan both allowed. COMMIT NOTHING (worker). No repo sources touched, dataset read-only. Finish via ticket Comments + final output -- never via send_message.

## Acceptance
Per-loop gates + falsifier + byte-proofs + E2E x3 vs 8/8+15/15 + verdict.

## Required evidence
Ticket Comments + final output: loop gates, md5s, job IDs, per-run tallies, verdict.

## Comments (worker, 2026-10-20 -- REGRESSION, default must not ship as-is; COMMIT NOTHING)

**Verdict: REGRESSION -- the full default chain moves the Pot A lane control. Thinned A_196 scores 5/8+3/15, 4/8+1/15, 4/8+1/15 vs the 8/8+15/15 bar, with same-binary ORIG and P40-fresh controls green 8/8+15/15 in all 3 jobs. The failure is GLOBAL (wrong edges spread across all 8 pieces, no single culprit loop), matching the Pot B 194/198 global-collapse attribution. Second finding: the ticket falsifier (rim-truth med delta >0.5mm) did NOT catch this -- all loops passed it, yet E2E collapsed.**

**0. Boundary kept.** Dataset read-only; no repo sources touched; production checkouts untouched; vehicle SRC read-only (`git log`/`grep` only). Spartan work dir `/data/gpfs/projects/punim2657/pota196_repro/` (scripts + npys + build/bundle manifests + sbatch, all outside any repo). Laptop adds: this Comments section + `artifacts/pota196/p196_thin_vs_input.png` (gitignored render) ONLY -- tracked tree verified clean (`git status` no modifications). Nothing committed or pushed.

**1. Densify gate (Step 0 -- VACUOUS, numbers recorded).** Per-loop dot spacing on the P40 base Bl_0 loops: med 1.90-1.93mm on all 8 (max 1.92-4.90, closure 1.48-1.94). At-regime vs the ~1.8mm nominal (author 1.8mm uniform resample reads ~1.9 after smoothing+closure); true mesh-sampled densify NOT triggered, midpoint interpolation FORBIDDEN per 111/146 and not used. Script `p196_step01.py`, log `p196_step01.txt`.

**2. Split (Step 1 -- one face cloud per loop; A08 outer block owned as label noise).** 175 parent-surface rule verbatim (mesh-frame radial tri labels, exact Ericson nearest-tri, fold joins inner; zero ORIG). Face(inner+fold) share: A01 92.2% ... A07 95.2%, A06 99.3%; A08 67.9% (outer 18/56). Audit: A01-A06 outer dots same-face noise (interspersion overlap full); A07 3 contiguous loop-order dots (12-14, tiny sector); A08 outer = contiguous block idx 20-36 + 2 isolated. Doubling census (179 recipe) on all 8 inputs: ratio 0.99-1.03, closure <=1.94, gaps5=0, D-tokens 3-5 -- clean singles, doubling signature absent everywhere; A08 mesh resolves ZERO inner tris (degenerate wall test on that fragment), so the block is label noise, not a second face. Disposition: one face cloud per loop = the FULL loop (194 precedent for singles). Logs `p196_step01.txt`, `p196_audit*.txt`, census table in `p196_census.py` output.

**3. Thin+walk (Step 2 -- 8/8 gated, 0 refused).** 185 v3 verbatim per full loop (PCA-plane 360-bin centreline, 8x Laplacian, 1.8mm resample cap 240, verbatim walk_m144 6-seed best-of-N, pure numpy -- no scipy on login node):

| loop | in n/arc | N1 | closure | med/max step | Dtok/run | rim-med in->thin | falsifier delta |
|---|---|---|---|---|---|---|---|
| A01 | 193/365.9 | 199 | 1.79 | 1.79/3.65 | 2/120 | 0.64->0.63 | -0.011 keep |
| A02 | 155/293.0 | 160 | 1.79 | 1.79/3.69 | 2/120 | 0.64->0.68 | +0.036 keep |
| A03 | 146/275.9 | 149 | 1.79 | 1.79/3.69 | 2/116 | 0.64->0.66 | +0.029 keep |
| A04 | 140/265.1 | 143 | 1.79 | 1.79/3.67 | 2/115 | 0.68->0.69 | +0.013 keep |
| A05 | 135/255.7 | 138 | 1.78 | 1.79/3.63 | 2/102 | 0.69->0.83 | +0.139 keep |
| A06 | 137/260.3 | 140 | 1.79 | 1.79/3.51 | 2/87 | 0.64->0.69 | +0.049 keep |
| A07 | 63/116.1 | 61 | 1.75 | 1.75/3.63 | 2/37 | 0.45->0.35 | -0.103 keep |
| A08 | 56/106.2 | 55 | 1.77 | 1.77/3.67 | 2/39 | 0.81->0.56 | -0.242 keep |

All gated (closure <=2.0, gaps5=0, single wrap); rim-truth med vs ORIG Bl_0 check-only (evidence only, never inputs). REFUSED: none. Eye-check `p196_thin_vs_input.png`: 4 plotted loops ride inputs as single monotonic laps, no weave (smoothing shrink 2-3%, same class as 185's 5% qualification).

**4. Bundle (Step 4 -- ONLY 8 Bl_0 changed, proofs).** `p196_build.py` on P40 base `pota40_bundle` -> `prep/pota196_bundle_A_196`: vehicle HEAD `bffefb6a983403ac45b96aa84a5c52f4fa0a810e` logged, veto-grep ABSENT-OK; channels donor = SELF (unthinned P40 loop, zero ORIG xyz; self-donor med 0.52-0.59, max <=1.94, n>5mm 0); seg tables rescaled OLD->NNEW with 186 continuity logic; Bl_1 slots bit-identical (md5s match P40 manifest); P40 base re-verified ALL-OK (`md5sum -c pota40_bun_md5.txt`); recursive diff = exactly the 8 Bl_0 files. Manifests `pota196_A_196_BL_md5.txt` (16 lines) + `pota196_A_196_bun_md5.txt` (48 lines); log `p196_build.txt` ends BUILD DONE.

**5. E2E x3 (Step 5 -- REGRESSION, controls green).** `stage/run_pota196_stage_A.sbatch` (180/186 pattern: 3 arms A_orig/A_fresh/A_196, all POT_A STEPS=8, k=5/b=3 shim, asserts HEAD-bffefb6/clean-tree/P22FIX+P22FIX2/C2-0.436/veto-absent/shim-k5-b3; first submission 33486321-23 VOID on a worker RUNDIR bug -- in-container path pointed at pota186_run_, all arms exit-1 pre-build, scancelled, fixed, resubmitted; no tallies taken from void runs). Valid jobs **33486565/66/67, all COMPLETED 0:0**, LINK-SHIM-OK + DRIVER-SHIM-OK x3, container exit 0 all 9 arms:

| job | A_orig (ORIG DS) | A_fresh (P40 DS) | A_196 (thinned DS) |
|---|---|---|---|
| 33486565 | 124/70 8/8+15/15 | 420/119 8/8+15/15 | 460/99 5/8+3/15 |
| 33486566 | 124/70 8/8+15/15 | 420/119 8/8+15/15 | 460/98 4/8+1/15 |
| 33486567 | 124/70 8/8+15/15 | 420/119 8/8+15/15 | 460/99 4/8+1/15 |

(Total/Pruned + binary sherd/edge from `*_binary.log`; forest identical 460/98-99 = deterministic input effect, not beam noise; A_196 binary variance 4-5/8 across runs = beam chance on top.) Bar (8/8+15/15, owning tickets 27 CURE + 19 protocol) NOT met by A_196 in any run; ORIG control reproduces 8/8+15/15 x3 so no run is void.

**6. Attribution (strict relative-edge vs author GT, 5deg/10mm, script `p196_strict.py`).** A_orig 6/15 strict (rot <=3.8deg, trans 10-27mm -- binary-vs-strict tolerance gap, expected); A_fresh x3 12/15 strict (same 3 fails 1-5/2-5/3-5, all p5-touching, trans 13-27mm); A_196 **0/15, 1/15, 1/15** with wrong edges spread over ALL pieces (run1 e.g. 1-3 66deg/380mm, 4-7 133deg/502mm, 6-7 157deg/663mm; runs 2-3 nearly identical failing sets). No single culprit piece -- the whole solution is scrambled (global-frame T comparison shows 25-179deg whole-solution rotations, i.e. no meaningful seating at all). Same signature as 194/198 on Pot B (untouched-piece drops, surviving edge = beam chance). Mechanism hypothesis (not proven): centreline smoothing shifts every loop systematically (arc -2-5%, dots move <=~1.9mm) while preserving NN distances -- the falsifier's rim-truth med is blind to it, but pair-wise edge compatibility breaks on all 15 pairs at once. The 185 cure helps exactly one case (doubled C01 -> single); applied to clean singles it adds only error.

**7. Recommendation for lead.** (a) Do NOT ship thin-then-walk as the default on this evidence -- it regresses the lane control on Pot A and Pot B alike. (b) The ticket falsifier (rim-med delta) is insufficient as a ship-gate for thinning -- it passed 8/8 here; E2E on the control is the gate that caught it. (c) Open question: whether a SHRINK-FREE thin (no arc loss, dots projected back to input) is harmless -- needs its own ticket, not an assumption. Bar for any retry: E2E x3 MATCH on Pot A (8/8+15/15) with controls green.

**8. Evidence paths.** Spartan `/data/gpfs/projects/punim2657/pota196_repro/`: `p196_step01.py/.txt` (spacing+split), `p196_audit.py/.txt`-family + `p196_census.py` (one-face verdict), `p196_step2.py/.txt` (thin table), `p196_build.py/.txt` + `pota196_A_196_{BL,bun}_md5.txt` (bundle proofs), `stage/run_pota196_stage_A.sbatch` + `slurm-3348656*.out` (jobs), `p196_strict.py` + `p196_diag.py` (attribution), `p196_thin_vs_input.png` (eye-check). RUNDIRs `/data/gpfs/projects/punim2657/sfs_main/pota196_run_3348656{5,6,7}/` (`*_binary.log`, `*_Result_snapshot/T_*to_*.txt`). Laptop: `artifacts/pota196/p196_thin_vs_input.png` (render only). sacct: 33486565/66/67 COMPLETED 0:0 (polled via sacct directly throughout).
