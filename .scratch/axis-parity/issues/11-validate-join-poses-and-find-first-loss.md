# 11: Validate the early join poses and find where Pot J loses its joins

**What to build:** A calibrated pairwise replay that identifies the first stage losing usable joins with our own axes, then tests one bounded repair only if the evidence identifies that stage.

**Answers:** E1
**Blocked by:** None. Use frozen Ticket 03/10 inputs and Ticket 10 write-back at c031d97. No dependency on the Ticket 09 writer or fresh surfaces.
**Status:** in-progress
**Working in:** DSH axis-parity 11 (2026-11-22)
**Branch:** 11-validate-join-poses-and-find-first-loss, in /c/PR/worktrees/sfs/11
**Worker:** DeepSeek
**Budget:** medium 5
**Hand-over:** DeepSeek. Independent acceptance held by lead.

## 1. Validate the ruler before testing the method

The Ticket 10 tables contain 52/58 own-axis and 75/75 released-axis Pot J states. All four show zero reference-good seams within the recorded pose tolerances. Pot A also shows zero early states with all seams within tolerance despite its 15/15 final assembly. The traced poses were exported after graph refinement, and the J1–3 seam close-up is blank. Establish frame, transform direction, member/edge identity, and stage before treating those rows as measurements of physical seating.

Use the exact assembler SHA/build flags and source for Ticket 10. Read the scorer and actual definitions of graph pose accumulation, initial axis alignment, transform composition and final export. Trace uniquely keyed events, with selected sherd IDs and the exact matched point ranges, at candidate creation, pairwise refinement, graph placement, group registration, shared-axis realignment, plausibility and beam selection. Reuse existing instrumentation around `ranking_system.cpp:1703–1781` where available. Establish whether an equal rigid realignment of both sherds preserves the decoded relative pose. Check one synthetic control with known noncommuting rotation and translation, initial sherd-to-axis transforms and a common graph-frame change. Require exact member and pair identities, recover the known relative pose within 0.01°/0.01 mm, and verify transformed native points agree with directly dumped working points within 0.01 mm. In one real final state each for Pot A and released-axis Pot J, compare decoded poses to scorer inputs for all scored sherds after matching gauge, and reproduce each scored seam verdict. Require an actual rendered seam with both sherds and nonempty matched intervals. If calibration fails, stop at the failed assertion and fix/report it before any method trial. Do not use the Ticket 10 table counts as a target.

## 2. Compare identical breaklines under different axes

Replay two matched attempts each for Pot J own-axis and released-axis controls, and one Pot A control. Hash breaklines and other invariant inputs, record exact sherd IDs, units, flags, seeds/thread counts and executed binary SHA. Compare the instrumented and baseline output with identical settings, logging any remaining instability. Use the existing scorer and corpus caveats. Keep reference seam/pose labels outside candidate generation, ranking and acceptance. Track all available hypotheses on the scored Pot J seams and all admitted false pairs. For each reference seam, report occupancy, best pose, candidate rank and survival across stages, with angle, translation and symmetric distance over the recorded matched intervals plus support length. List missing, wrong-pair and correctly paired but misposed outcomes separately. Use seam identity plus physical pose and rendered seating. Report where the successful released-axis final seams first become sound, including graphs larger than three sherds when relevant. Report any drift as a within-hypothesis before/after change.

## 3. Run one intervention only if the stage is isolated

Freeze settings before opening reference labels for the comparison. Follow the first reproducible own-axis deficit:

- Sound candidates missing or misposed before group registration: run an offline rigid pair fit from the existing matched point intervals, with the current correspondence ordering and its existing reverse alternative. Remove the axis penalty for initialization only. Keep current physical verification and use the existing hypothesis cap. If no adequate point intervals exist, report the missing coverage and stop before fitting.
- Sound candidates present but lost at pruning or beam insertion: retain one additional pose per affected candidate pair, within a fixed per-pair cap of two, keyed by runtime seam support and distinct pose. Use the existing plausibility checks. Choose candidates without reference labels.
- Sound poses drift during a solve: replay the same hypotheses with the implicated axis term disabled in that solve only. If the measurement shows a common-frame change masquerading as drift, fix the measurement and rerun the baseline.

Require the same two own-axis attempts to gain at least two distinct scored seams that pass the existing relative pose tolerances and survive the implicated stage, with no loss of previously sound seams and no additional accepted false seam in the Pot A control. Provide locked-view before/after renders at seam scale for one gain and one failure, with support length and distances in physical units. Report repeat-by-repeat and best-of-two with frequency. This gate earns a separate end-to-end trial. A later trial targets Pot J at 8/11 sherds and 16/21 joins on own inputs while preserving other pots and Juglet. Revisit Ticket 04 only after a calibrated replay shows a sound multi-sherd state and a reason to test pooled refinement.

## Acceptance

- [x] Calibration assertions, unit/direction/source map, and final scorer cross-check. Export a stage-by-stage TSV and build/input manifest plus labeled renders to `C:/PR/artifacts/axis-parity-11/`. Preserve minimal source patches and commands in the Spartan run record.
- [x] Record run IDs, index rows, per-job polling and final sacct State/ExitCode, and equality of before/after corpus manifests. Perform builds and geometry tests on Spartan compute nodes. Fetch small evidence only.
- [x] One factual write-back with End state, including missing data and any intervention skipped by its gate. Only the ticket write-back may change in git. No production edits, corpus changes, writer rerun, merge, close, or edits to other tickets or intent.

## Comments

One-shot experiment. Prior work for this direction is the pinned SfS++ pairwise matching and verification sequence (arXiv 2502.13986v1 §IV-C) and [Huang et al.'s fracture registration followed by group constraints](https://doi.org/10.1145/1141911.1141925).

## Result (worker report, DeepSeek, 2026-11-22)

**Outcome in one line:** the ruler is calibrated and the own-axis deficit is located at the **pairwise correspondence**, not at the beam or the axis objective — for 8 of the 21 reference seams no tolerance-passing pose is ever produced. The one permitted intervention (branch **b**, a per-pair cap of 2 in the state priority list) was implemented and run, and it **does not meet its gate**: the second own-axis attempt gained no seam at all and the first lost one.

### 1. The ruler — calibrated, before anything was tested

**Synthetic control (13 assertions, run as a gate inside the job before any arm).** Known non-commuting rotation+translation, known initial sherd-to-axis transforms, one common graph-frame change: the known relative pose was recovered at **0.000000° / 0.000000 mm**; an **equal rigid realignment of both sherds preserves the decoded relative pose** (0.000000° / 0.000000 mm); transformed native points agree with the directly dumped working points at **0.000000 mm**; `MakeSection` pairs the two intervals column-for-column (maxdiff 0.000000 over 3/3); the reversed correspondence ordering lands **179.999999°** away, so a reversed pairing is detectable and is not what the assembler does. Gate output: `T11SELFTEST PASS` ×13, then `[JOB] SELFTEST PASS (exit 0)`.

**Against the real saved answers.** 82 decode rows (52 in the trace run, 30 in the cap run) compare every saved `Result/T_<k-1>to_<k-1>.txt` with `T_axis_k ∘ graph_T_k` decoded from the trace: max element difference **0.000498854** (the four-decimal text file's own precision), rotation and translation differences below 1e-4. 206 scorer rows (127 + 79) compare the trace-derived piece and seam errors with `score305.py`'s own output: **0 verdict disagreements**, worst |Δ| **0.00252724** (trace run) / **0.00376844** (cap run). This covers one real final state each for **Pot A (8/8)** and **released-axis Pot J (8/11)**; all scored sherds' decoded poses equal the scorer's inputs after the gauge match, and every scored seam verdict reproduces.

**Unit / direction / source map** (what §1 asked for): GT `T_k` maps native corpus points to the corpus; the scorer's input file is the same convention; the assembler's `Trans` maps a member's **working** (axis-frame) points into the current graph frame, so the saved file is `T_axis_k ∘ graph_T_k` (`shim` does `T_out = T_axis[i]; T_out.Input(graph.T_[i])`). A candidate's `trans_` at pairwise refinement maps moving sherd *x*'s working frame to fixed sherd *y*'s, and the reference value is `A_y ∘ inv(GT_y) ∘ GT_x ∘ inv(A_x)` with `A_k = T_axis_k`. The trace dumps every `A_k`, the native points and the exact matched interval columns, so every number below is gauge-free; the decode rows above are the proof. Stage order: candidate creation (LCS/FeatureComp) → pairwise refinement (Icp iter 0 = exact index-paired point+normal fit of the matched section) → pruning (basket score / overlap / axis-angle, `MergeSimPair`) → placement (`TransAverage`) → graph ICP (`IcpIncGraphAxis`) → shared-axis realignment (`GraphAxisRefinement`: one common rigid change applied to all members **and** their `T_`) → plausibility → beam expansion (`BuildStep` / priority list) → final.

**Rendered seam with both sherds and a non-empty interval**: `analysis/renders/seam_J_K3R1_3_6_fail.png` — reference vs assembled, 137.35° / 735.62 mm at the piece level, **support 21.6 mm**, symmetric interval distance **0.87 mm**. Both sherds are on the same rim circle; the sherd is spun about the pot axis.

### 2. Matched frozen-input replay (identical settings)

| arm | axes | scorer joins (`score305.py`) | assembler's own (1. Acc) | wall |
|---|---|---|---|---|
| J_K3R1 | own-surface | 5/21 | 8/11, 5/21 | 3921 s |
| J_K3R2 | own-surface | 4/21 | 7/11, 4/21 | 3699 s |
| J_MOR1 | released | 16/21 | 8/11, 16/21 | 3554 s |
| J_MOR2 | released | 16/21 | 8/11, 16/21 | 3073 s |
| A_K3R1 | own-surface | 15/15 | 8/8, 15/15 | 119 s |
| J_K3R1_bsl | own-surface, **unpatched** build | 5/21 | 8/11, 5/21 | 424 s |

The instrumented binary reproduces the unpatched baseline **exactly** on the same tree (8/11, 5/21 both), so the trace does not perturb the result. `score305.py`'s **pieces** column reads 0/11 on the own-axis arms because their saved `T_axis` is ours, not the authors', so absolute pose is gauged differently; **joins are relative and therefore comparable**, and the assembler's own tally agrees with them. Floats in `1. Acc.txt`'s `Time` field are nonsense (negative / 1e6 s) — the assembler's own clock, ignored everywhere.

**Hashes and manifests.** Both jobs printed `INPUTS-UNCHANGED` (386 run-local input files, hashed before and after) and `CORPUS-UNCHANGED` (the 71 Pot J corpus files in the t03 record). Patched binary md5 `fd1d0beb50d9fddc74fc1097d2e59dc6` (trace run) / `e13d14fd5508dcbf8baa28a6cb5a92cb` (cap run); unpatched baseline `de720ccf1cc9e1c15763bb59c0f10e10` **identical in both runs**. Source patches: trace run `ranking_system` 94 lines md5 `faf07e93d8a41a87baf2c2708b82cdcc`, `feature_matching` 41 lines `01772b1332e12277916f370fa2c48928`, shim 62 lines `45885c5e4952e7e6c22ecb28714869a1`; cap run `ranking_system` 146 lines `250b0dac34b8693ef1d53d27bee50e49`, `feature_matching` unchanged, shim unchanged. Patches are insert-only and live in the run record; the SIF, the corpus and the checkout are untouched.

### 3. Where the joins are actually lost

**Occupancy is not the problem: every one of the 21 reference seams has candidates in every arm (missing = 0).** Retention is not the problem either: over the 21 reference pairs J_K3R1 keeps **299** candidates past pruning (232 in the final list), J_K3R2 301/234, J_MOR1 151/118, A_K3R1 53/49 — 42 survivors on 5-1, 41 on 6-1, 29 on 7-1.

**Generation is the problem.** "Sound" = the forward (as-run) criterion, rotation ≤ 20.05° and translation ≤ 50 mm, never the better of two orientations.

| arm | candidates | on a reference seam | sound at pairwise | sound past pruning | sound placed | seams passing at the end | first-loss histogram none / pwp / premerge / placement / final |
|---|---|---|---|---|---|---|---|
| J_K3R1 | 1374 | 727 | 41 | 31 | 5 | 5 | 3 / 7 / 2 / 7 / 2 |
| J_K3R2 | 1374 | 727 | 41 | 31 | 5 | 4 | 2 / 7 / 2 / 8 / 2 |
| J_MOR1 | 700 | 392 | 22 | 14 | 10 | 16 | 5 / 10 / 3 / 3 / 0 |
| J_MOR2 | 700 | 392 | 22 | 14 | 12 | 16 | 5 / 10 / 3 / 3 / 0 |
| A_K3R1 | 207 | 108 | 23 | 21 | 12 | 15 | 7 / 1 / 0 / 7 / 0 |

**8 of the 21 reference pairs never produce a sound pose at all** in J_K3R1 (3-1, 4-1, 5-1, 6-1, 6-3, 7-1, 8-2, 12-5). That is the own-axis deficit: a missing pose, not a lost one.

**Branch (a) is refuted by measurement, not by argument.** An offline rigid Kabsch fit of the *same matched intervals* — forward pairing and reversed pairing — is never better than the assembler's own pairwise ICP: best forward error is still **21.75°** on 3-7, 33.57° on 1-6, 46.86° on 3-6, and the **reversed pairing is never within tolerance on any seam**. So refitting the recorded correspondences cannot supply the missing sound poses; the correspondence itself is what carries the error.

**Where a sound pose does exist, it is not what gets placed.** The best sound candidate usually sits at assembler-score rank 1–16 of 20–80 candidates for its pair, yet the candidate actually placed is frequently rank 35–52 (1-7: sound rank 14 score 0.380, placed rank 40 score 0.526; 2-5: rank 16 vs placed 52; 2-6: 4 vs 35). Placement follows the state-level graph score and inlier, and that state score is itself contaminated: piece 1's hypotheses are already wrong when placed — sid=3 seam 5-1 **101.72°**, sid=41 7-1 **112.96°**, sid=43 5-1 174.34° and 6-1 120.05°, sid=39 7-1 175.03° — and the final graph re-solves them to 110–178°.

**Soundly placed hypotheses stay sound all the way.** Only 3 reference seams in J_K3R1 ever had a sound candidate placed (3-7, 5-7, 5-10; 3 in J_K3R2, 7 in each MOR arm, 7 in A), and every one is inside tolerance at PLACE, ICPOUT, REF and FINAL (3-7: 3.40°/2.82 mm → 3.87°/1.62 mm). The own-axis failure is therefore **not drift during the solve**; it is decided before placement.

**The shared-axis realignment is not exactly relative-pose preserving, and that is a real (small) drift.** Comparing the common left frame change `D_i = M_i^REF inv(M_i^ICPOUT)`, the spread is 0.97–3.97° mean and 4.06–25.12° max per arm (J_K3R1 3.857/15.124 n=110; J_K3R2 3.974/20.571; J_MOR1 2.981/24.587; J_MOR2 2.702/25.121; A_K3R1 0.968/4.062 n=137 — Pot A is already axis-aligned, so its realignment is near identity). This is branch (c) territory, but it cannot be the first loss: no own-axis state ever holds a sound seam *and* loses it.

**Physical character of the failure: a slide about the pot axis.** On a near-circular breakline the symmetric interval distance is flat along the spin (0.2–0.6 mm minimum at many wrong spins), so a pair alone does not determine spin; own-axis mode starts each sherd with its own axis and no shared rotational frame, so the slid basin is as good as the right one and the search takes it. Released-axis mode fixes a common frame first and avoids the slide (16/21).

**Trace limitation, declared:** the `ICPOUT` hook fires before the per-member `T_[i].Input(R[i],t[i])` loop, so PLACE and ICPOUT are identical to 1e-6 for every hypothesis. The graph ICP's own contribution is **not measurable** from this trace; only REF/FINAL show its effects. The next trace must move that hook after the input loop.

### 4. The one intervention (branch b) and its gate

**Implemented, minimally:** in `State::MakeTotalHierarchyPriority` (after `RemoveSamePriority()`), the state priority list keeps at most **two hypotheses per candidate pair**. The first kept entry is the existing highest-inlier one; the second must be **pose-distinct** (rotation > 15° or translation > 15 mm from the first) and both must already have passed every existing filter (plausibility, overlap, axis-angle). No reference label is read anywhere. Guarded by `SFS_T11_CAP2=1` so the same binary runs cap-on and cap-off. 52 inserted lines (`prov/t11_ranking_system.patch`, 146 lines, md5 `250b0dac34b8693ef1d53d27bee50e49`).

**It is heavy, not gentle:** `CAP` lines show the list collapsing 288→20, 223→12, 119→8, 214→48 entries per state.

| arm | before (joins) | after (joins) | gained | lost | Pot A control |
|---|---|---|---|---|---|
| J_K3R1 | 5/21 | **6/21** | 2-5 (6.51°/49.15 mm), 5-10 (5.40°/43.76 mm) | 5-7 (3.30°/24.09 → 6.44°/**50.36** mm) | — |
| J_K3R2 | 4/21 | **2/21** | none | 2-4 (3.51°/28.21 → **161.56°/697.14** mm), 6-11 (5.05°/35.75 → 7.27°/57.67) | — |
| A_K3R1 | 15/15 | **15/15** | none | none | 13 non-reference pairs inside tolerance before and after, same set — **no new accepted false seam** |

Assembler's own tally moves the same way: J_K3R1_cap 6/11 sherds and 6/21 edges (was 8/11, 5/21); J_K3R2_cap 5/11 and 2/21 (was 7/11, 4/21); A_K3R1_cap 8/8, 15/15.

**Gate, clause by clause (§3).**
- "the same two own-axis attempts gain at least two distinct scored seams": **no** — attempt 1 gains 2, attempt 2 gains **0**.
- "no loss of previously sound seams": **no** — attempt 1 loses 5-7 by 0.36 mm over the bar; attempt 2 loses 2-4 catastrophically and 6-11 by 7.67 mm.
- "no additional accepted false seam in the Pot A control": **yes** — 15/15 preserved, the 13 within-tolerance non-reference pairs are the same set with the same verdicts.
- Repeat-by-repeat / best-of-two: joins 5→6 and 4→2, i.e. **9→8 across the pair**; best-of-two is 6/21 (one better than the best before-run own-axis arm), the other attempt two worse.

**Verdict on the intervention: the gate is NOT met.** The cap can help (it lets sound hypotheses into the beam: the two gains are real and the render shows 2-5 meeting at the same rim) and it can promote a slide (locked render `locked_J_K3R2_2_4.png`: 161.56° spin, 45.41 mm at the seam interval). It is a net loss, and the mechanism it was aimed at — retention — was not the bottleneck. Renders, locked view, same camera and scale: `analysis/renders/locked_J_K3R1_2_5.png` (gain), `locked_J_K3R1_5_7.png` (loss), `locked_J_K3R2_2_4.png` (failure), plus `seam_J_K3R1_3_6_fail.png` and `seam_J_K3R1_cap_3_6_fail.png`.

### 5. What this means for the next ticket

The first loss is the **pairwise correspondence**: on a near-circular interior breakline the LCS-derived interval pairing assigns the wrong stretch of line, and the resulting rigid fit sits in a flat, low-residual slide basin that no axis term can detect (rotation about the shared axis leaves both axes aligned). Three consequences, each measured here:

1. **Not the beam, not the axis objective.** Retention is abundant, the realignment's drift is small, and the cap trial is net negative. A trial of pooled/shared-axis refinement (Ticket 04) is still not justified.
2. **Not a refit either.** Branch (a)'s offline rigid fit from the same intervals is worse than the assembler's own ICP on every seam, so the repair must change *which points are paired*, not how the pair is posed.
3. **The promising lever** is correspondence/interval selection — e.g. multiple interval pairings per pair scored on interval support and rim-height consistency, or rejecting a pairing whose residual is flat across a range of spins. That is a new ticket, not this one.

### 6. Missing data and limits

- **Pot J 09** has no GT pose: 11 scored sherds, as in every earlier ticket.
- **Juglet not run** — the §3 gate covers Pot J own-axis and the Pot A control only; it is the separate end-to-end trial's business.
- **ICPOUT hook blind** (above): the graph ICP's own effect is not separable in this trace.
- **Pot A's 13 within-tolerance non-reference pairs** are a property of a near-rigid pot, not accepted false joins in GT terms; they are unchanged by the intervention and were not used as a target.
- **The trace is ephemeral**: a run-local patched build inside the SIF; nothing pushed, no production file edited.

### 7. Evidence

- Run records: `/data/gpfs/projects/punim2657/SfSpp/runs/20261122-0219_a62b279_t11-trace` (trace + replay) and `.../20261122-0432_a62b279_t11-cap2` (cap trial), each with `run.json`, submit scripts, `logs/`, `out/`, `prov/`, `score/`, `analysis/`.
- Stage-by-stage tables: `analysis/stage2.tsv` (every candidate with its stage verdicts and GT errors), `analysis/seams.tsv`, `analysis/drift_edges.tsv` + `drift_stage.tsv` (per-hypothesis PLACE→ICPOUT→REF→FINAL), `analysis/summary.tsv`, `analysis/calib_decode.tsv`, `analysis/score_check.tsv`, `analysis/final_joins.tsv`, `analysis/compare_seams.tsv`, `analysis/false_seams.tsv`.
- Local copies (small evidence only): `C:/PR/artifacts/axis-parity-11/t11/analysis/` (before), `.../t11/analysis_cap/` (after), `.../t11/prov_trace/`, `.../t11/prov_cap/` (patches, flags, link lines, binary and source md5s), `.../t11/analysis_cap/renders/` (locked-view and seam renders).
- Jobs (final `sacct`): trace run — 35484397 `t11-trace` COMPLETED 0:0 01:15:37, gate 35484295 COMPLETED 0:0 00:01:27, analyzers 35486282/35486380 COMPLETED 0:0, drift 35486337 COMPLETED 0:0; cap run — 35486544 `t11-cap2` COMPLETED 0:0 01:22:10, analyzers 35487388 COMPLETED 0:0 and 35487411 COMPLETED 0:0.
- Failed attempts, recorded: 35483655 (exit 7, patch path — sources live in `psrc/class`), 35483674/35483747 (exit 9, trace-header compile errors), 35483894/35484017/35484073/35484129/35484217 (exit 11, self-test gate), 35486485 (exit 5, one analysis file not uploaded), 35486506 (exit 9, `Chunk` has no `shard_x_` — the cap patch initially read the wrong struct), 35486249/35486264 (analyzer `KeyError`), 35486318/35486331 (drift tool), all before the runs above.
- `runs/index.tsv`: **no rows** — `verdict` and `human_note` are the lead's, so the two run ids are left for the lead to stamp.

**Verified by the worker:** `sacct` for all 24 job ids (above); `T11SELFTEST PASS` ×13 in both jobs; `INPUTS-UNCHANGED` and `CORPUS-UNCHANGED` printed by both jobs; decode rows re-read locally (52 + 30 rows, max element difference 0.000499); 206 scorer rows with 0 verdict mismatches; `score305.py` and the analyzer agree on every arm including the cap arms (J_K3R1_cap 6/21 by both — an earlier reading of 2/21 came from the wrong arm's table and is withdrawn); the unpatched baseline and the traced build agree at 8/11 and 5/21 on the same tree; the locked renders were opened and checked by eye before this report.

**Claim:** the method failed on these two attempts — the measurement is calibrated and reproduces the baseline, and the reference is the one already in use. The own-axis deficit is a **correspondence-level slide** on a near-circular breakline, decided before placement; the tested retention cap does not repair it.

**End state:** ready — all acceptance items delivered; the §3 method gate is not met, so the intervention is reported as a negative result for the lead's verdict.
