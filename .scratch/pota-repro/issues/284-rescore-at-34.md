# 284 — Re-score every rollout lane at theta 3.4 on the shipped binary

Answers: E1
Status: ready-for-agent
Working in: C:/PR/worktrees/sfs/284 (Phase 0 is read-only inventory; Phases 1-3 run on Spartan)
Needs-eye: yes -- a per-pot overlay picture for any lane that moves across the bar

## Why

Every rollout score in this repo (tickets 250-259, 214 lanes across ten pots) was collected at
**SFS_PAPER_THETA = 4.0** and on the **pre-strip** binary. Main now ships theta 3.4 plus the
no-discard full walk, the 12 mm stop rule, the vote-order host and the ticket 274 clamp, with the
five rejected arms removed (538357c, 67ff3d7). Ticket 271 showed 3.4 is not free — Pot H 10 Bl1
went 96.59% -> 79.55% kept-% — so the rollout numbers in the ledger are no longer a statement
about the program we ship. This ticket replaces them.

## Phase 0 — inventory first, no compute (this is the gate on everything else)

For each piece scored in tickets 250-259, report:

1. the pot, the piece id, the lanes scored, and each lane's score at 4.0 from the ticket;
2. whether the author breakline files for those lanes are still present (path + md5);
3. whether the piece's mesh still exists in the authors' sample tree, and **whether it is the
   plain mesh or a downsampled one** — most survivors are _Mesh_DS.obj, and a cloud sampled from
   a DS mesh is coarser and not byte-identical;
4. whether any surface pair or edge output from the original 4.0 run survives on Spartan
   (pota2xx trees were pruned; check before assuming);
5. the lane count that can be reproduced honestly, and the lane count that cannot, with the
   reason for each refusal.

**Phase 0 output is a table plus a go/no-go.** If a piece can only be reproduced from a coarse
cloud, say so and score it in a separate column — never mix it into the number that replaces the
ledger.

## Phase 1 — mesh and edge at the shipped settings

For the reproducible set: mesh at theta 3.4 with SFS_AXIS_FILE set (verify the classify line; a
missing axis file silently keeps size order — ticket 277), then edge with **defaults only**, no
overrides. Record the binary md5 and the source md5 in every run.json, and prove the binary
contains the three shipped markers ([STOP-267], [FULL-263], [VOTE-247]).

## Phase 2 — score

Score every lane against its own author lane with the standing definition (one-way precision:
each of our resampled dots to the nearest author dot; med = median; cov = share within 2 mm;
jumps = consecutive step > 10 mm) **and** the author-side coverage, which is mandatory — a short
line lying on the author's line scores 100 one-way.

Report per lane: 4.0 baseline, 3.4 result, and the delta in all three numbers. Then per pot.

## Pre-registered rules

- A lane "at bar" means cov >= 90 and med <= 2.0 mm, as in the rollout tickets.
- Every lane that leaves the bar and every lane that enters it gets named with its numbers; no
  pot-level average may hide a lane. Report the count in each direction first, then the detail.
- Quote medians to one decimal: the mesh stage draws 30 random ray-cast points from an unseeded
  generator (mesh_processing_headless.cpp:1526-1527), which moves P03's median by ~0.1 mm run to
  run. Coverage and jumps survive that noise; a 0.05 mm delta does not.
- No retuning. If a lane fails, it is reported as a failure with its numbers.

## Phase 3 — write it back

Append a ledger section (K.2 or L) replacing the stale 4.0 scores, state plainly whether the
shipped program is better or worse than the numbers it replaces, and list the lanes that still
fail with their family from the ledger (growth / dropped cluster / partition / unresolved).

## Acceptance

- Phase 0 table with an explicit go/no-go and the honest lane count.
- Every reproducible lane scored at 3.4 with both directions of coverage.
- Counts: lanes at bar before, at bar after, entered, left.
- The ledger updated and the stale 4.0 claim marked superseded.
- One overlay PNG per pot containing a lane that crossed the bar in either direction.

## Evidence to report

- the Phase 0 table and the lane arithmetic
- the per-lane score table with both coverage directions
- the entered/left lists with numbers
- binary and source md5s, and the marker check output

## Phase 0 result (lead-recorded 2026-10-24 from the worker's report; source run dir
/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1851_ee5f4dc_p284-rescore/ — REPORT.md and
phase0-table.tsv hold the full tables)

**NO-GO, for a provenance reason that no amount of compute can repair.** The mesh stage never
sees the authors' mesh: it consumes a CloudCompare-sampled cloud made by cc_mesh_to_pcd.sh with
-SAMPLE_MESH POINTS 1000000, and **that sampling is unseeded**. Proven on one author mesh
(Pot_A_Piece_01_Mesh.obj, sha256 63f248c5...): three draws give 843,433 / 843,282 / 843,252
points, all different bytes. So the 4.0-era input clouds cannot be regenerated, and a fresh draw
would confound "3.4 versus 4.0" with "a different point set".

Of 148 scored pieces, **exactly two input clouds survive** — Pot C 01 (844035fe..., 82,505,766 B)
and Pot C 03 (1d01ad63..., 42,013,121 B), both md5-matching what ticket 251 recorded. No 4.0-era
surface or lane output survives: the pruned pota* trees became attic tarballs that exclude
*.pcd / *.obj / *.xyz by suffix.

**Corpus arithmetic — this ticket's own line was wrong.** The scored corpus is **296 lanes over
148 pieces**, and **265 were at bar at 4.0**: A 16/16, B 17/18, C 4/8, D 51/58, E 60/62, F 12/14,
G 12/14, H 18/22, I 55/60, J 20/24. The figure 214 is the seven-pot subtotal B+E+F+G+H+I+J, not
the corpus. Meshes: 17 plain (all of Pot A and B), 131 downsampled (_Mesh_DS, confined to C-J).
Every scored piece still has both author breaklines, an axis and a mesh.

**The four reproducible lanes at the shipped defaults** (job 33744771; mesh env POT_NAME +
SFS_AXIS_FILE, edge env POT_NAME only; paper=PAPER-CHAIN theta=3.40000; classify lines confirm the
axis was used):

| lane | pts ours/auth | med | cov | rev cov | 4.0 baseline (med / cov) |
|---|---|---|---|---|---|
| C01 Bl0 | 25/211 | 51.62 | 0.0 | 0.0 | 0.76 / 67.2 |
| C01 Bl1 | 81/230 | 41.06 | 0.0 | 0.0 | 0.71 / 64.3 |
| C03 Bl0 | 187/191 | 0.42 | 99.5 | 100.0 | 0.55 / 93.1 |
| C03 Bl1 | 124/120 | 2.02 | 49.2 | 50.0 | 12.21 / 13.6 |

At bar before 1/4, after 1/4; entered 0, left 0. C03 improves markedly (Bl1 med 12.21 -> 2.02,
cov 13.6 -> 49.2) but still misses on coverage. **C01 collapses to a 52.6 mm stub**: the edge log
reads [LOOP-SELECT] bag=975 comps=4 -> "no ring found -> whole-bag walk" -> [VOTE-247]
resampled=28 (L=52.6 mm) against a 378 mm reference rim.

**The C01 collapse is NOT a theta effect.** Job 33744872 re-ran the same bytes at
SFS_PAPER_THETA=4.0 on the same binaries: 11/82 points, med 54.9/41.1, cov 0.0/0.0. Theta moved
the mesh split only marginally (100,224/115,444 -> 100,471/115,652 points), and
SFS_PAPER_THETA is read by mesh_processing_headless.cpp:2559-2561 only — the edge stage never
reads it. So the 4.0 baseline is not a like-for-like comparison for C01: the difference belongs to
the merged edge code, not to the growth angle.

**Lead note — this is not a new unknown.** Ticket 273's matrix already measured the same collapse
in shipped code (C01 Bl0 11 dots / 54.922 / cov 0.0; stop rule off 309 / 0.785 / 67.64; full walk
off 208 / 0.537 / 100) and ticket 275 diagnosed it: the full walk seeds at the dot nearest the
cloud centroid, which on these bags lands in a debris lump 26-54 mm from the rim, walks the lump,
and the 12 mm stop rule then ends the walk correctly on the wrong structure.

**Corrections accepted:** (1) the corpus is 296/265, not 214 — corrected in the ledger; (2)
scripts/run_from_commit.sh does not exist at any commit (verified: zero hits in git log --all),
so the AGENTS.md reference to it is wrong and the build recipe used here (archive + cmake + sbatch,
recorded in run.json) is the real one; (3) the three-marker proof can only be satisfied by the edge
binary — the mesh binary (fb3fd055d30fb08ccce48dba7d49a879) carries none of them, and asking for it
there was my error; (4) Phase 2's at-bar counts can only be produced over the four surviving lanes.

**Ledger deliberately left untouched**, as the worker insisted: a supersession resting on four
lanes would be worse than the stale number it replaced. Correct.
