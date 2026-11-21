# 10: Can the first joined sherds give Pot J a better shared axis?

**What to build:** A bounded Spartan experiment that distinguishes a missing sound initial join from drift after a sound join is available. Establish whether shared-axis refinement deserves a live assembler trial.

**Answers:** E1
**Blocked by:** None. Use frozen Ticket 03 inputs. Ticket 09 owns the writer and its eventual regeneration is a separate experiment.
**Status:** ready-for-agent
**Worker:** unassigned
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
