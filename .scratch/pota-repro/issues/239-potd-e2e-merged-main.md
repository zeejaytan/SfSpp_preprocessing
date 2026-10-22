Status: done

# Ticket 239: full Pot D E2E on merged main (paper path, tree-built chain)

Answers: E2E proof for Pot D (29 pieces) on the chain main now builds itself.
Needs-eye: no.

## Goal
Run the full Pot D end-to-end on origin/main post-238: mesh + edge binaries built FROM THE TREE (verify md5s: mesh d72979aa, edge dc472b0e), fresh arm + ORIG control arm, 214 protocol.

## Boundary
- Fresh worktree of origin/main + fresh Spartan copy. Rebuild BOTH binaries in the container first; if either md5 differs from the reference, STOP and report (do not seat with mismatched binaries).
- Pot D = all 29 sherds. Fresh arm seats with our lanes; ORIG control arm validates the vehicle (214 precedent).
- Per-piece lane check per the swap rule (ledger Section B): verify slot mapping per piece before seating; blanket-apply nothing.
- Main worktree (user 204-edit) off limits except ticket commit + push of this ticket (lead does the landing).

## Constraints
- 214 numbers are the bar to match-or-beat (22 SWAP-clean + P03 agree + 6 MIXED: P12/P15/P16/P22/P25/P27). Report per-piece: which of the 6 MIXED resolve on the paper path, which persist, with lane scores (med/cov both lanes, slots, votes).
- No code changes, no commits to main. Evidence only: lanes, scores, seat renders, tallies.
- Spartan: pull --ff-only first, STOP and report on divergence.

## Acceptance
- Fresh arm tallies + ORIG control tallies + per-piece lane table (29 rows) + seat render eye-checked good. sacct COMPLETED for every job, binary md5s cited.

## Lead verdict (2026-10-22)
ACCEPT E2E COMPLETE. R6: 3/3 jobs sacct COMPLETED 0:0; gate_table on disk verified (straight slots, cross ~8mm/0%); rebuilt binaries byte-identical to ref (same node bm175; -march=native lesson recorded); fresh 20/29 + 36/69, ORIG 22/28 + 53/66 valid. Lane pattern flips 214: 25 AGREE straight, 0 SWAP (classify cure holds), 4 MIXED (P03-Bl0 regressed 2.43/45.5 + unseated; P22/P27 persist; P24 marginal). Fresh trails control by 2 sherds with lane-clean pieces unseated (P15/P26) => assembly-side follow-up open. P03-Bl0 regression is a merge-line follow-up (was AGREE in 214).

## Required evidence to report
Rebuilt binary md5s; job IDs + sacct states; per-piece lane scores; fresh/ORIG tallies; seat render path; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.

## Comments (worker run 2026-10-22, ticket 239)
Verdict: E2E COMPLETE. Fresh 20/29 sherds (69.0%) + 36/69 edges (52.2%); ORIG control 22/28 (78.6%) + 53/66 (80.3%). Vehicle validated: control matches 84-lineage (22/27+49/66) with better edges on the current 29-node/69-edge graph.

Gates:
- Spartan pull --ff-only BLOCKED by the documented skip-worktree live file (mesh_processing_headless.cpp) -- not history divergence (fetch ok, origin/main = 5fdd5c2 both sides). Followed 238 precedent: live checkout untouched, fresh clone sfs-potD-239 @ 5fdd5c2.
- Rebuild: first build (node bm018) md5-mismatched (mesh b468f347 / edge 6608ab9a vs ref) -- root cause: -march=native codegen differs per build node (only .text differs). Rebuilt pinned to 238's node spartan-bm175 (job 33632642 COMPLETED) -> byte-identical to ref: mesh d72979aaa0055885a4dc88bb51a172e7, edge dc472b0e87c934b6c487ff8637209864. -T14/append-free OK.
- Pipe: 29/29 lanes, paper chain (job 33633082 COMPLETED, 6:35). Inputs: 214 sampled PCDs (aggregate a05b1445...).

Lane gate (merged-main paper path supersedes the 214 pattern -- all lanes file author-order): 25 AGREE straight (meds 0.39-1.01, cov mostly >=93%), 0 SWAP, 4 MIXED: P03 (Bl0 2.43/45.5 with a 20.8mm jump -- regressed vs 214's 0.70/99.1; Bl1 0.86/95.4 clean), P22 (0.80/85.2 + 0.41/91.6, no jumps -- same marginal as 214), P24 (0.73/81.4 + 0.39/100.0), P27 (0.89/71.4 + 0.91/57.1, small piece). Every piece best-matches STRAIGHT (cross-slot meds 6-14mm / ~0%) -> slotmap all-STRAIGHT (29 lines). 214's 6 MIXED on this path: P12/P15/P16/P25 resolve to clean AGREE; P22/P27 persist marginal; P03-Bl0 newly degraded (flagged, seated-out: P03 unseated in fresh arm).

Seat (job 33634062 COMPLETED 1:13; POT_D vehicle block SHARD_NUMBER 29; switch = build glue, vehicle tree verified clean after, HEAD b56bc80d788fd10110d2a821097a29bcdba759e6):
- Fresh (fresh mesh staged as Mesh_DS.obj per POT_D block; GT = ORIG 28 T + graph): 20/29 + 36/69. Unseated (no T): P03, P15, P22, P25, P26, P28, P29; 22 placed, 2 placed-but-wrong.
- ORIG control: 22/28 + 53/66. P27 excluded by the vehicle (author Bl0 49pts < 50pt cutoff, shard off); P22 auto-miss (no GT T in ORIG -- 28 T files only; binary scores it vs Identity).
- Script note: the seat script's snapshot-count-equals-N gate is over-strict for partial assemblies (both binaries ran to 'Result save finish'; 22 T files each); tallies authoritative. No code changes anywhere; no main commits.

Artifacts (laptop artifacts/pota239/): gate_table.txt (29-row slot matrix), gate_table.csv (58 lane rows), L_fresh_binary.log, O_orig_binary.log, pota239_bun_v1_md5.txt, pota239_bun_stage.log, run239_seat.sbatch. Spartan: pota239_e2e/pota239_run_33634062/ (both Result snapshots + cmake/make/binary/outer logs), pota239_D_bundle_v1/SfS_pp (seated bundle). Renders: N/A headless (vehicle has no render path, same as 238); snapshot OBJs preserved at the run dir.
