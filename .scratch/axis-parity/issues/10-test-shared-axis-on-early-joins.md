# 10: Can the first joined sherds give Pot J a better shared axis?

**What to build:** A bounded Spartan experiment that distinguishes a missing sound initial join from drift after a sound join is available. Establish whether shared-axis refinement deserves a live assembler trial.

**Answers:** E1
**Blocked by:** None. Use frozen Ticket 03 inputs. Ticket 09 owns the writer and its eventual regeneration is a separate experiment.
**Status:** in-progress
**Working in:** DSH: SfS++ axis-parity Ticket 10 (2026-11-21)
**Branch:** 10-test-shared-axis-on-early-joins, in /c/PR/worktrees/sfs/10
**Worker:** DeepSeek
**Budget:** medium 5
**Hand-over:** DeepSeek. Lead holds the independent acceptance check.

## Why this experiment

Ticket 07 found plausible seeds for all 11 scored Pot J sherds. Ticket 08 found that a nearly flat patch can score better than the vessel's true profile and that its shortlist ablations failed to recover J01, J08 and J12. The 141-sherd deduplication experiment measured sensitivity to sample weighting. Ticket 09 tests the writer itself.

Ticket 03's Pot J control held the breaklines fixed and changed the input axes. Use both its own-axis and released-axis arms to locate where the joins first diverge. Willis and Cooper's [multi-sherd alignment study](https://citeseerx.ist.psu.edu/document?doi=d3d9b4929be6812e3cd8c15fd729b249ff96b822&repid=rep1&type=pdf) uses shared break curves to constrain the same global axis. The relevant insertion point in the local assembler is `GraphAxisRefinement` (baseline checkout `a79ee4f`, `class/ranking_system.cpp:1781,2554` and `class/axis_estimation.cpp:259–321`). Ticket 04 owns any production implementation.

## Experiment

1. Pin the actual Ticket 03 assembler SHA, scorer, flags, seeds where available, axes, breaklines, wall clouds and pose references from run records. Record file hashes and native units per arm. Use `20261121-1319_2e951d9_t03-ship` and `20261121-1600_2e951d9_t03-jctl` for provenance. Reproduce the pinned configuration in fresh outputs if instrumentation is needed. Record missing inputs explicitly. Do not substitute assets across arms. Read SfSpp_preprocessing/AGENTS.md corpus caveats before scoring.
2. For Pot J, replay two own-axis and two released-axis attempts on the same own breaklines. For each, trace the first accepted multi-sherd graph and the earliest accepted graph containing a reference-good join, if present. Record stage, candidate and accepted seam IDs, membership, relative pose errors and whether a good join existed among candidates before refinement. Use existing scorer tolerances. If traces are missing, instrument an isolated ephemeral Spartan job build, leaving the normal binary and checked-out source unchanged. Export the patch into the run record. Use Pot A as a known assembly control and native `def_3x` Juglet as a transfer probe, one attempt per object. Label absent states and unstable replays explicitly.
3. Freeze the earliest accepted two- or three-sherd state with a sound join in each attempt where available. Also keep the first accepted state if it contains a wrong join, as a negative control. For those same memberships, use reference poses as an oracle control, and compare input line, current pooled Cao, and exactly one scale-free pooled residual from Ticket 04. Freeze starts, samples, wall selection, solver budget and robust weighting before scoring. Set the normalized denominator floor relative to the cluster size and record it. Keep sherd poses fixed within each fit. Repeat the normalized fit from each member's available rank-0 line, and report every start. Use reference axes and poses only for scoring and the explicitly labelled oracle. If no eligible own-axis state exists, use the first two eligible reference joins in stable seam-ID order for the oracle-only ceiling.
4. Report sign-free angle error (degrees), distance from the reference vessel origin to each line (mm), and position shift at the cluster centroid (mm). Convert native 3x Juglet distances to physical mm once, at reporting. Record the full per-state TSV with object, arm, repeat, state, membership, seam IDs, pose errors, start, method, angle, offset, shift and failure reason. Render input/reference/current/normalized lines in the same frame and scale with two fixed views, and close views of the traced seams. Keep geometry on Spartan and fetch small tables, logs and renders to `C:/PR/artifacts/axis-parity-10/`.

## Decision for the lead

- Consider a live Ticket 04 trial for Pot J only if both own-axis attempts reach a sound fit state and at least two distinct accepted Pot J memberships show a normalized line within 10°, improving angle versus current Cao with no increase in reference-origin offset. Each membership must meet this with the frozen input start and at least one member start. Pot A must stay within 10° with no increased offset versus Cao within the scorer's recorded numerical tolerance. Report all other starts and negative controls, including any attractive fit on a wrong join.
- If only reference-posed states show the benefit, prioritise getting a sound early join into the search. If even those fail, revisit the shared-axis objective before changing the live assembler. Juglet is a transfer probe and cannot satisfy the Pot J bar. These are research decision thresholds. This experiment measures axis recovery and access to sound joins.

## Acceptance

- [ ] Report input manifest, all prescribed attempts and states or documented absences, current-vs-normalized matched rows, physical-unit conversion and paired renders. Lead inspects renders and recomputes the gate before recording a result.
- [ ] Record run IDs, `runs/index.tsv` rows, every final `sacct` State/ExitCode after polling, and before/after corpus manifest equality. Heavy checks and builds run on compute nodes.
- [ ] Put factual write-back under Comments on the ticket branch, with the evidence paths and the required End state. Changes in git are limited to this ticket's write-back. Do not edit the writer, production estimator, other tickets, intent, or main. No whole-corpus rerun in this ticket.

## Comments

One-shot research ticket. Existing writer and assembler implementation lanes already have separate ownership.

### Worker write-back (DeepSeek, 2026-11-21/22)

**Runs.** Commit `34a00c6` on `10-test-shared-axis-on-early-joins` (basis `241dbaa`).

| run | job | what | final sacct | elapsed |
|---|---|---|---|---|
| `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-2306_34a00c6_t10-trace` | 35477168 `t10-trace` | 4 Pot J replay arms + Pot A + Juglet, traced build | COMPLETED 0:0 | 01:44:52 |
| same | 35477573 `t10-analyze` | offline fits + renders | COMPLETED 0:0 | 00:03:05 |
| `/data/gpfs/projects/punim2657/SfSpp/runs/20261122-0025_34a00c6_t10-ctl` | 35478427 `t10-ctl` | Pot A control (Juglet phase failed, see below) | COMPLETED 0:0 | 00:04:18 |
| same | 35478685 `t10-jug` | Juglet probe rerun | COMPLETED 0:0 | 00:08:18 |
| same | 35479439 `t10-anaA` | Pot A fits | COMPLETED 0:0 | 00:00:18 |
| same | 35479495 `t10-anajug` | Juglet fits | COMPLETED 0:0 | 00:00:58 |
| run A | 35479997 `t10-oracle` | oracle-only ceiling fits | COMPLETED 0:0 | 00:00:43 |

Failed attempts, recorded: 35478427's Juglet phase exited **127** (`bash: /panel/t10_arm.sh: No such file or directory` — the arm script was not copied into the run-local `jpanel`); replaced by 35478685. The first oracle job **35479914** exited **2** on all three phases (`unrecognized arguments: --oracle-pairs` — it read a stale analyser); replaced by 35479997. `runs/index.tsv` has **no** rows for either run: `verdict`/`human_note` are the lead's to write, so the rows (`20261121-2306_34a00c6_t10-trace 35477168 34a00c6 t10-trace`, `20261122-0025_34a00c6_t10-ctl 35478427 34a00c6 t10-ctl`) are left unset.

**Inputs pinned.** Frozen Ticket 03 trees, same 12 Pot J pieces, same own breaklines and own wall clouds; Pot J `NP=19 FLOOR=50`, Pot A `NP=8 FLOOR=50`, Juglet `def_3x` bundle `NP=9 FLOOR=10`. Provenance: `20261121-1319_2e951d9_t03-ship` and `20261121-1600_2e951d9_t03-jctl`; the replayed trees come from `20261121-1319_2e951d9_t03-potJ/trees`, `..._t03-potA/trees`, `..._t03-juglet/bundle`. **Hashes:** 386 run-local input files hashed before and after the run — identical (job printed `INPUTS-UNCHANGED`); the 71 Pot J corpus files listed in the t03 record's `corpus_inputs_before.md5` re-hashed now — identical (`CORPUS-UNCHANGED-SINCE-T03 71 files`, e.g. `Axes/Pot_J_Piece_01_Axis.xyz 5035e44c1c94c2bc4665fb6b5fc0f5ba`). Nothing wrote the corpus; the arms read run-local copies. **Units:** pots as released (mm, degrees); the Juglet is native 3x, so every Juglet length below is divided by 3 once, here. **Missing input:** Pot J piece 9 has no `Ground Truth` pose, so it cannot be scored — the same 11 scored sherds as the scorer.

**Instrumentation was ephemeral.** The SIF's pristine source carries no trace switches, so `/opt/sfs-pristine` was lifted to `work/psrc` and `class/ranking_system.cpp` patched insert-only by `work/t10_patch.py` (1926 → 2058 lines; patch `prov/t10_trace.patch`, 162 lines, md5 `fdc0ae76adb1c11542b11e66628dec71`); the Juglet 362 source was patched the same way (2814 → 2946, `prov/t10_trace_362.patch`, md5 `c7b89401c66542f6ce9bc00ff9bc1777`). It emits one `IN`, one `OUT` and one `VER` record per attempted build, and `POSE` lines for accepted 2–3 member graphs, only when `SFS_T10_TRACE=1`. Container, corpus and the checked-out source are unmodified; the built binary is `work/build/Hierarchy-Clear`, md5 `1cb78ff1ba130976bb849ed76e61c3d1`.

**Replay against the t03 record** (same tree, same recipe, trace on — sherds / strict edges):

| arm | axes | t03 | this replay | wall |
|---|---|---|---|---|
| J_K3R1 | own-surface | 8/11, 5/21 | **5/11, 3/21** | 5670 s |
| J_K3R2 | own-surface | 7/11, 4/21 | **5/11, 3/21** | 5632 s |
| J_MOR1 | released | 8/11, 16/21 | 8/11, 16/21 | 4768 s |
| J_MOR2 | released | 8/11, 16/21 | 8/11, 16/21 | 4835 s |
| A_K3R1 | own-surface | 8/8, 15/15 | 8/8, 15/15 | 111 s |
| Juglet | own-surface | 8/18 edges | 9/9 sherds, 8/18 edges | 445 s |

**The own-axis pair is unstable; the released-axis pair and both controls are stable.** The two K3 replays agree with each other and with nothing else: the same tree, re-executed, moves 3 sherds and 2 edges. Trace volume (IN/OUT/VER/POSE): K3R1 132/132/132/123, K3R2 132/132/132/143, MOR1 134/134/134/182, MOR2 137/137/137/183, A 93/93/93/64, Juglet 104/104/104/106.

**The measurement that decides the ticket: no early accepted join is sound, in any arm.** "Sound" here means every accepted edge is on a reference-correct seam **and** inside the scorer's own tolerances (20.05°, 50 mm) — a reference-correct seam alone is not enough, which is the finding that reshaped this analysis.

| arm | accepted 2–3 member graphs scored | sound | accepted edges | on a reference-correct seam | within tolerance | good-seam rotation error min/median/max (°) | translation (mm) |
|---|---|---|---|---|---|---|---|
| J_K3R1 | 52 | **0** | 79 | 60 | 0 | 43.2 / 110.2 / 165.2 | 110–961 |
| J_K3R2 | 58 | **0** | 95 | 65 | 0 | 43.2 / 110.1 / 178.6 | 110–961 |
| J_MOR1 | 75 | **0** | 116 | 90 | 0 | 22.2 / 93.5 / 177.9 | 230–950 |
| J_MOR2 | 75 | **0** | 115 | 87 | 0 | 22.2 / 89.2 / 173.2 | 230–950 |
| A_K3R1 | 25 | **0** | — | — | — | — | — |
| Juglet | 46 | **0** | — | — | — | — | — |

Every early merge lands **on the right seam** and places it tens to hundreds of degrees wrong (median ≈ 90–110°). `GraphAxisRefinement` at the first joins is therefore fitting a shared axis through geometry that is already mis-placed. There is no sound state in the own-axis arms from which drift after a sound join could be measured — the "state" column of the prescribed step 3 has no eligible member to freeze, and the earliest accepted state is reported instead, as the ticket allows. The negative control is the first accepted state carrying a reference-wrong seam.

**Frozen states, matched rows** (same state, same membership, same poses; angle in degrees, `lat` = offset measured in the plane through the reference origin normal to the reference axis, offset/shift in mm; Juglet divided by 3):

| arm | state | members / seams | GT spread (°) | current pooled Cao | T04 normalized from frozen input | T04 normalized from best member start | Cao refit, best start |
|---|---|---|---|---|---|---|---|
| J_K3R1 = J_K3R2 | s0_e0_o0_g1 | 5,7 / 5-7 | 41.86 | 53.7°, lat 164.4 | 86.3°, lat 432.8 | 26.7° (piece5), lat 13.2 | 26.4° |
| J_MOR1 = J_MOR2 | s0_e0_o0_g0 | 1,3 / 1-3 | 79.55 | 37.6°, lat 248.2 | 35.2°, lat 19.7 | 76.3° (piece3), 88.7° (piece1) | 14.0° (piece1) |
| A_K3R1 | s0_e0_o0_g0 | 1,4 / 1-4 | 41.51 | 24.6°, lat 29.4 | 15.8°, lat 48.1 | 5.4° (piece1), lat 3.2 | 1.4° (piece1) |
| Juglet | s0_e0_o0_g1 | 1,8 / 1-8 | 58.56 | 29.5°, lat 51.4 | 40.8°, lat 64.8 | 2.7° (piece1), lat 60.1 | 0.6° (piece1) |

Negative controls: J_K3R1 s0_e3_o1_g1 (7,10 / 7-10, GT spread 78.0°) current Cao 76.8° while the normalized fit from piece10 reaches **10.6°** — an attractive fit on a wrong join; A_K3R1 s5_e4_o2_g1 (3,8 / 3-8, spread 85.1°) Cao 73.6° but a Cao refit from piece3 reaches **1.4° at 0.2 mm**; J_MOR2 s0_e2_o1_g0 (1,2 / 1-2, spread 57.3°) Cao 74.4°, normalized 79.3–85.8°; Juglet s0_e1_o1_g1 (3,8 / 3-8, spread 10.8°) Cao 38.4°, normalized 37.1°. Every one of these is a two-sherd cluster, where the pooled axis is dominated by a single sherd: the sub-10° fits above come from *one* member's start, not from a shared constraint. That is the honest reading of the table, and it is why the gate asks for two distinct memberships.

**Oracle-only ceiling** (reference poses, prescribed reference joins 1-3 and 1-4 for Pot J, 1-2/1-3 for Pot A, 1-2/1-4 for Juglet; reference axes and poses used only here):

| object / join | Cao from pot-axis start | T04 normalized from pot-axis start | member starts |
|---|---|---|---|
| Pot J 1-3 | 1.52°, 2.23 mm | 1.90°, 2.34 mm | piece3 1.90°; piece1 11.5° (K3) / 87.6° (MOR), normalized 88.7° on both |
| Pot J 1-4 | 7.55°, 3.03 mm | 4.22°, 2.22 mm | piece4 same as pot-axis; piece1 78.7°/75.5°, normalized 60.3°/74.1° |
| Pot A 1-2 | 1.35–1.41° | 1.13°, 0.64 mm | all starts 1.1–1.5° |
| Pot A 1-3 | 1.16–1.35° | 1.32°, 0.53 mm | all starts 1.2–1.4° |
| Juglet 1-2 | 3.28° | 73.6° (local minimum) | piece1/2 0.78°, normalized 1.30° |
| Juglet 1-4 | 1.23° | 86.1° (local minimum) | piece1/4 1.23°, normalized 1.89° |

So with reference poses **both** objectives recover the shared axis to 1.1–1.9° on the pots, and the normalized objective does not inflate the offset on Pot A — but neither objective is globally safe from a bad start (the piece1 rows, and the Juglet pot-axis rows, land in a distant local minimum at 60–88°). On 2-sherd clusters the reference poses leave little to constrain, which the spread column measures directly.

**Gate, clause by clause.**
- "both own-axis attempts reach a sound fit state": **no** — 0 of 52 and 0 of 58 accepted own-axis Pot J graphs are sound.
- "at least two distinct accepted Pot J memberships show a normalized line within 10°, improving angle vs current Cao with no offset increase, from the frozen input start and at least one member start": **no** — the best own-axis earliest-state member-start fit is 26.7° (53.7° Cao) and the best frozen-input fit is 86.3°.
- "Pot A stays within 10° with no increased offset vs Cao": **yes in the oracle condition and in its final assembly** (1.1–1.4°; the 8/8 assembly's GT-mapped axis agreement is 0.82–2.62° across all eight pieces), **no as an in-state claim** — Pot A's own earliest state is 41.5° off in its reference spread, i.e. the same defect, just smaller.
- Juglet is a transfer probe and cannot satisfy the Pot J bar: 8/18 edges, earliest state 58.6° spread, 29.5° Cao.

Read against the ticket's own branch: the evidence does **not** support "only reference-posed states show the benefit" *and* it does not show the objective failing either — it shows the objective being handed geometry that is already mis-placed, so the objective is neither exonerated nor convicted. The branch selected is the one the ticket names first: **get a sound early join into the search before changing the live assembler.** A live Ticket 04 trial is not justified by this run.

**Evidence paths** (geometry stays on Spartan; small tables and renders fetched):
- `C:/PR/artifacts/axis-parity-10/results/trace/{J,A,juglet}/t10_states.tsv` — full per-state table (object, arm, kind, state, nodes, edges, gt_agree, membership, seam IDs, pose errors, start, method, pose, angle, offset, lat, shift, cost, diameter, eps, fit points, reference spread, candidates, note).
- `.../t10_seams_<arm>.tsv` — every accepted edge with its reference-good flag, rotation error, translation and tolerance verdict.
- `.../oracle/t10_states.tsv` — oracle-only ceiling rows.
- Renders (two fixed views + along-axis + close views of the traced seams, same frame and scale, input/reference/current/normalized in one frame): `.../J/t10_J_MOR1_earliest.png`, `.../J/t10_J_K3R1_earliest.png` (+ `*_negative.png`, `*_seams.png` per state), `.../A/t10_A_K3R1_earliest.png`, `.../juglet/t10_juglet_own_xy_r1_earliest.png`.
- Run records: `run.json`, `submit_t10.sbatch`, `submit_analyze.sbatch`, `submit_oracle.sbatch`, `logs/panel.tsv`, `score/acc.tsv`, `score/trace_lines.tsv`, `logs/trace_<arm>.log`, `prov/` (patches, flags, link line, binary and source md5), `analysis/*.log`.

**Verified by the worker:** `sacct` for all seven jobs (above); `INPUTS-UNCHANGED` over 386 files; `CORPUS-UNCHANGED-SINCE-T03` over 71 files; the relative-pose formula reproduces t03's recorded 16/21 on its final Pot J poses; the reference axis mapping gives 0.0°/0.0 mm agreement on Pot J pieces 1–4, 8, 11, 12 and 0.82–2.62° on the 8/8 Pot A assembly; the offline Cao refit from the assembler's own line lands within 0.7° of it on the J_MOR1 earliest state (38.34° vs 37.64°).

**Claim:** this is a measurement result about the assembler's early joins, not about broken measurement or a wrong reference — the reference and the scorer are the ones already in use, and the identical recipe reproduces the stable arms exactly.

**End state:** waiting: lead verification of this write-back and the live-Ticket-04 go/no-go — the gate as written is not met (0 of 52 and 0 of 58 accepted own-axis Pot J states are sound), so the next step is a sound early join, not a change to the shared-axis objective.

