# 313: Distance-invariant axis optimization — eliminate centroid lever-arm bias and seat Pot E's failing pieces

**What to build:** Implement distance-invariant (radial-normalized) normal alignment optimization and ranking in `sfs_axes` to eliminate the Cao/Mumford centroid lever-arm bias proven in ticket 312. In ticket 312, the unnormalized error $e_i = (p_i - p_0) \cdot (n_i \times a)$ was shown to mechanically favor false axes passing through sherd centroids (collapsing lever arms from 75 mm to 16–41 mm and dropping costs up to 7×), while normalizing by distance ($\hat{e}_i = \frac{e_i}{\|(p_i - p_0) \times a\|}$) restored the true vessel axis on 9 of the 10 failing pieces. This ticket implements the distance-invariant objective in `sfs_axes` (candidacy scoring, refinement, and worst-wall ranking), runs the new axis set through the Spartan C++ assembler harness on Pot E to break past the 23/31 sherds (33/62 joins) ceiling toward the 31/31 (62/62) reference, and verifies whole-corpus non-regression across Pots A, B, D, G, and I.

**Answers:** E1

**Blocked by:** none (ticket 312 landed; root cause proven to be Cao/Mumford distance lever-arm bias)

**Status:** ready-for-agent

**Worker:** unassigned

**Budget:** large 8

**Hand-over:** worker with Spartan access; needs `sfs_axes` Python package, Spartan Slurm access, and C++ SIF assembler harness. Judgement stays with the lead.

<!-- When work starts: **Status:** in-progress, plus
**Working in:** <project thread title / laptop chat / Spartan job ID> (<date>)
**Branch:** 313-distance-invariant-axis-fit, in C:/PR/worktrees/SfSpp_preprocessing/313 (code tickets only; scripts/ticket_start.sh writes all three lines) -->

## Context & The Problem to Solve

In tickets 310–312, the axis selection and generation pipeline was systematically dissected:
1. **Ticket 310:** Proved that on Pot A, ranking candidate basins by the worse wall's Huber cost seats 8/8 sherds and 15/15 joins (up from 6/8 and 7/15). However, Pot E regressed from 21/31 sherds (36/62 joins) in BASE down to 17–18/31 (25/62) in MM.
2. **Ticket 311:** Proved that Pot E's regression had two components: (a) K=6 emitted decoy perpendicular lines on 6 pieces, recoverable by capping K at 2 or 3 (reaching 23/31 sherds, 33/62 joins); (b) 10 pieces (`03, 09, 23, 24, 25, 26, 27, 28, 29, 31`) failed across all K because their Huber minima sat 17°–59° away from the true axis.
3. **Ticket 312:** Proved the mathematical root cause: the Cao/Mumford metric $e_i = (p_i - p_0) \cdot (n_i \times a)$ has physical dimensions of length (mm). Shifting the axis from the true rotation axis (~75 mm away) into the sherd centroid reduces $\|p_i - p_0\|$ by 50% to 75%, shrinking the Huber cost by up to 7×. When normalized by distance ($\hat{e}_i = \frac{e_i}{\|(p_i - p_0) \times a\|}$), the normal alignment error is strictly lower at the true vessel axis on 9 of the 10 failing pieces (up to 4.04× lower error).

This ticket implements the normalized formulation as an active pipeline in `sfs_axes` and tests whether it seats Pot E's failing pieces without regressing the rest of the corpus.

---

## Stages of Execution

### Stage A: Distance-Invariant Objective Implementation in `sfs_axes`
1. **Residual Function:**
   In `sfs_axes/cao.py` (or a dedicated `sfs_axes/normalized.py`), implement:
   $$\hat{e}_i = \frac{(p_i - p_0) \cdot (n_i \times a)}{\|(p_i - p_0) \times a\|}$$
   with sign-agnostic biaxial handling (taking the minimum of forward and reverse normal orientations with softmin / log-sum-exp) and Huber robustification.
2. **Refinement & Scoring:**
   - Implement refinement of $(a, p_0)$ under $\hat{e}_i$ using Levenberg–Marquardt or manifold least-squares (`scipy.optimize.least_squares`).
   - Implement ranking by the worse wall's normalized error:
     $$\hat{E}_{\text{worst}}(a, p_0) = \max\left( \frac{1}{|S_0|} \sum_{p \in S_0} \rho(\hat{e}_i), \frac{1}{|S_1|} \sum_{p \in S_1} \rho(\hat{e}_i) \right)$$
3. **Physical Centroid Clearance Constraint / Prior:**
   - In archaeological ceramics, a sherd of radius $R \approx 70\text{--}120$ mm cannot physically have its axis passing within $d(C, L) < 25$ mm of its centroid unless it is a base fragment. Incorporate a clearance penalty or minimum radius threshold to reject centroid-cutting decoys during clustering.
4. **Verification on the 10 Failing Pieces:**
   - Prove that running the normalized MLESAC + refinement on the 10 failing Pot E pieces directly produces candidate axes within 10° of Ground Truth / authors' released axes, without rolling into the centroid.

### Stage B: Pot E Assembly Evaluation (The K Ladder)
1. Generate `axes313` for all 34 Pot E pieces under the normalized pipeline.
2. Run the Spartan C++ assembler harness across the $K$ ladder:
   - `E_K1` (top line only)
   - `E_K2` (top 2 lines)
   - `E_K3` (top 3 lines)
   - `E_K6` (top 6 lines)
   - Controls in the same job: `E_MO` (authors' axes, must reproduce 31/31 sherds, 62/62 joins) and `E_BASE` (308 baseline, 21/31, 36/62).
3. Score each arm with `acc.tsv` and recomputed `CountResult` at 0.35 rad / 50 mm against Ground Truth poses.
4. Measure whether the 10 previously failing pieces now find valid joins and whether total seating beats ticket 311's 23/31 sherds and 33/62 joins ceiling.

### Stage C: Corpus Non-Regression Gate (Pots A, B, D, G, I)
1. Run the normalized pipeline across the whole 163-piece benchmark.
2. Run the C++ assembler grid on:
   - **Pot A:** Must retain 8/8 sherds and 15/15 joins (ticket 310's milestone).
   - **Pot B, Pot D, Pot I:** Must retain or improve on ticket 310 seating numbers.
   - **Pot G:** Must retain baseline seating.
3. Any regression on Pot A, B, D, or I must be reported explicitly; the fix must be universal and blind.

### Stage D: Visual Proofs & Documentation
1. Render reconstructed assemblies and axis alignments before/after for Pot E and any altered pots.
2. Stage all renders into `artifacts/pota313/renders/` and link as clickable workspace-relative links.
3. Record all Slurm jobs, sacct lines, and append-only entry in `runs/index.tsv`.

---

## Acceptance Criteria

- [ ] A1: Implementation of distance-invariant normal alignment loss $\hat{e}_i = \frac{(p_i - p_0) \cdot (n_i \times a)}{\|(p_i - p_0) \times a\|}$ and ranking in `sfs_axes`, unit-tested with clean gradients/residuals.
- [ ] A2: Single-piece verification table on the 10 failing Pot E pieces showing that normalized MLESAC + refinement finds candidate axes within 10° of Ground Truth without rolling into the centroid basin.
- [ ] A3: Generation of `axes313` for all 34 Pot E pieces and execution of the full K-ladder (`E_K1`, `E_K2`, `E_K3`, `E_K6`) along with `E_MO` and `E_BASE` controls on Spartan compute nodes.
- [ ] A4: Pot E seating results: report sherd accuracy and edge accuracy, demonstrating recovered joins on the 10 failing pieces and breaking past the 23/31 sherds / 33/62 joins ceiling.
- [ ] A5: Corpus non-regression verification across Pots A, B, D, G, and I, proving zero regression on Pot A (8/8 sherds, 15/15 joins) and maintaining gains on B, D, and I.
- [ ] A6: All visual claims accompanied by clickable workspace-relative renders staged in `artifacts/pota313/renders/`; all Slurm runs recorded with `sacct` State/ExitCode; run logged in `runs/index.tsv`; corpus md5 untouched.

## Instruments to reuse

- `sfs_axes` module: `sfs_axes/cao.py`, `sfs_axes/potsac.py`, `sfs_axes/refine.py`.
- Diagnostic harnesses: `.scratch/pota-repro/312-stage/stage312.py` (`distance_invariant_normal_loss`).
- Grid + substitution harness: `.scratch/pota-repro/310-stage/submit310c.sbatch`, `corpus310.py`, `stage310b2.py`.
- Scoring: C++ assembler `CountResult` against `original_samples/SfS_pp/Ground Truth/` at 0.35 rad / 50 mm.

## Rules that apply to this ticket

- Comments-only edits to this ticket during execution; worker reports, lead concludes and lands.
- Heavy jobs run on Spartan compute nodes via Slurm; every `sbatch` gets a poll and its final `sacct` recorded.
- Visualizations required for all geometry claims; clickable workspace-relative links in comments.
- Never modify corpus files in `original_samples/SfS_pp`.

## Comments
