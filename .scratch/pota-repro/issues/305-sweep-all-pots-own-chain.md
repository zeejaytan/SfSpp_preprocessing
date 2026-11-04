# 305: Sweep — every sample pot end to end on our own preprocessing output, plus the Juglet

**What to deliver:** one measurement: what the assembler actually seats when **everything** fed to it
comes out of this repository — our breaklines *and* our axes, produced by the code as it now stands
(tickets 302 + 304 landed) — on every sample pot that can be scored, each pot with the authors'
own inputs as the control arm in the same run. Plus the same for the Juglet.

No fixes. This ticket answers 'where does the reproduction stand, pot by pot, with our own chain',
and it must be read as best-of-N with N stated, because beam variance in this assembler is large.

**Answers:** E1

**Blocked by:** none. 302 (per-point cost) and 304 (under-5,000-point rule, now default ON) are
landed on main; the 304 merge is 71ac6d4 and the default flip is 646a387.

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-05)
**Branch:** 305-sweep-all-pots-own-chain, in /c/PR/worktrees/sfs/305

**Worker:** sfs305

**Budget:** large 12

**Hand-over:** Claude — Spartan compute, the corpus, the assembler SIF and the lane recipe; no MATLAB
needed (that was 304).

## Starting position (verified, do not re-derive)

- **Pot A reproduces the authors 8/8, 15/15 using our axes only** — but with the axis reader's
  truncation off and an explicit step, not with the CLI's own defaults. Run
  20261105-0217_3649473_t304-stageC, arms py_s1_best / ml_s1_final / ml_s1_stage1. The lead re-scored
  the transforms itself (inv(GT_i)GT_j vs inv(T_i)T_j, bar 0.35 rad / 50 mm,
  class/data_structure.cpp:966).
- **Which default is unanswered:** sfs_axes/read_surfaces defaults to truncate=True (equalises the
  two surfaces' point counts). On Piece 08 the truncated basin collapses to **88.15 deg** from the
  reference line where the untruncated one sits at **5.2280 deg** (out/stageC_analysis.txt). So the
  shipped CLI may still lose Pot A Piece 08. **Stage 0 settles this before anything else runs.**
- **Our lanes exist for three inputs only:** outU_jug, outU_pota, outU_potc in run
  20261103-1332_fab76f5_t66-admitsign-default (the t66 recipe, submit66.sbatch in that run dir;
  Arm U = SFS_ADMIT_SIGN at its new default ON). There is **no** lane for pots B, D, E, F, G, I, J.
- **The bar to beat, from ticket 39** (.scratch/pota-repro/issues/39-bj-e2e.md), authors' inputs (ORIG)
  vs our-then-chain: B 9/9+15/15 vs 4/9+2/15 · C 4/4+5/5 vs 0/3+0/3 · D 23/28+55/66 vs 16/27+16/66 ·
  E 31/31+62/62 vs 7/31+4/62 · F 6/6+9/9 vs 4/6+3/9 · G 7/7+10/10 vs 4/7+3/10 · I 25/27+59/65 vs
  9/27+4/65 · J 8/11+16/21 vs 0/10+0/18 · H none (all 11 refused at the admission gate).
  That run used a different assembly vehicle, so **its ORIG numbers are context, not a control** — the
  control is the OO arm inside this run.
- Corpus census (Surfaces/Pot_X_Piece_YY_Surface_0.xyz): A 8, B 9, C 6, D 32, E 34, F 7, G 7,
  H 11, I 30, J 19 = **163**. 44 pieces are under 5,000 points (they now take step 1).

## Stage 0 — does the shipped CLI still seat Pot A? (do this first, it is cheap)

Axes for Pot A 01-08 through the **CLI as shipped** (python -m sfs_axes, no environment override),
which now means the under-5,000 rule ON and truncation at its default. Then the same with the axis
reader's truncation off (the 304 proof path) as the comparator. E2E both ways, floor 50,
**at least 3 seeds each**, and score with the counter's own bar.

Record: seated/joins per seed, best-of-N with N, and for any lost piece the piece-level error in
degrees and millimetres. If the shipped default loses Piece 08 again, that is the headline result of
this ticket — **report it as found, do not fix it, and do not silently switch to the working setting
without saying so in the result**.

## Stage 1 — our lanes for every pot (the missing input)

Copy the t66 recipe from run 20261103-1332_fab76f5_t66-admitsign-default (submit66.sbatch and
instrsrc/) and run Arm U for the pots that have no lane: **B, D, E, F, G, I, J**. Reuse outU_pota,
outU_potc, outU_jug (record their md5s; do not rebuild them — if you must, say why). Binaries from
the current main of this repo, md5 recorded.

One Slurm job per pot. run.json + a runs/index.tsv row per job, verdict/human_note left empty.
Inputs and the corpus read-only: md5 of every corpus file before and after, must match.
Breaklines are the outU_<pot>/geom/*.Bl0 files.

## Stage 2 — axes for every piece, from the code as shipped

sfs_axes over all 163 pieces with the shipped defaults -> **new** output directory (out/axes305
inside your run dir; never overwrite out/axes302). Three seeds for all of Pot A and for the 44
pieces under 5,000 points; one seed elsewhere, and say so. For each piece record K, the angle to the
released axis (diagnostic only), and runtime. State in the log that the under-5,000 rule fired for the
pieces the census lists — the default is on, prove it, do not assume it.

## Stage 3 — the E2E grid

Four arms per pot, where **O** = the authors' released inputs and **M** = ours:

| arm | Breaklines | Axes |
|---|---|---|
| OO | released | released |
| MO | **ours** | released |
| OM | released | **ours** (axes305) |
| MM | **ours** | **ours** |

- **Full 4-arm grid on the five small pots: A, B, C, F, G.**
- **OO + MM only on the four large pots: D, E, I, J** (they are 30-34 pieces; a 4-arm grid there
  costs more than a day of wall-clock for one pot).
- **H: do not run.** All 11 pieces were refused at the admission gate in ticket 39 and there is no
  GT-bearing pipe; state that once, with 39-bj-e2e.md section 1 as the reference, and leave it out of
  the grid.
- **>=2 repeats per arm, and repeat the costly MM arms at least 3 times on the small pots.** Report
  **best-of-N with N** — never a lone median — and also report how many repeats reached the best.
- Floor 50 for pots, floor 20 for the Juglet; the 302/304 vehicle (sfs_pristine_assembly.sif +
  patch_guard67.py k=5/b=3 shim). Record the binary md5s so the vehicle is pinned.
- **Re-derive the E2E set from our own axle files** (an empty *_Axis.xyz auto-excludes its piece,
  BreakLine::ReadAxis -> shard_on_off=false): the set can differ from ticket 39's, because our
  axes now exist for pieces that had none. List the deltas against 39's sets explicitly.
- Score twice: the counter's binary (1. Acc.txt, per-sherd lenient rule) and the strict relative-edge
  table (5 deg / 10 mm) as a diagnostic. **The binary is the reported number**; say which is which.
- Each pot its own job; cap each E2E job at 4 h and record any arm that a cap truncated as truncated —
  do not report a capped arm as a measurement of that arm.

## Stage 4 — the Juglet

Floor 20, arms OO (Dataset axes + t66 jug lanes) and MM (our axes305 for the Juglet + the same
lanes), >=3 repeats. Report score58 (seated/9, candidates, mutual consistency), best-of-N with N,
against what is already known: t67 23 candidates / 0 seated, t68 hybrid 35 / 0, ticket 302 37 / 0,
and Dataset axes median mutual consistency 27.1 deg vs our port 12.35 deg (ticket 302, tail losses on
Juglet Pieces 3, 8, 9 named there).

## Stage 5 — the picture and the table

A seating render per pot for the MM arm at its best repeat, plus OO where it differs, into
artifacts/pota305/ (workspace-relative links in the ticket, gitignored). Then **one line per pot**
for the conservator: pot, pieces, our chain seated/joins, authors' arm seated/joins, N, and whether
our chain is behind, level or ahead — with the claim named as (1) method, (2) measurement or
(3) reference.

## Rules

- **Start with scripts/ticket_start.sh SfSpp_preprocessing .scratch/pota-repro/issues/305-*.md**
  (its own worktree; Status must still read ready-for-agent when you run it).
- SSH: **/c/Windows/System32/OpenSSH/ssh.exe spartan** (git-bash ssh cannot authenticate).
  Single-quote the whole remote command; inner $ escapes need care.
- Released axes and GT may be read **only** to score and to diagnose, **never inside a shipped rule**.
- Corpus read-only; nothing outside your run directories; nothing committed from the worker side.
- Every sbatch gets a sacct -j <id> --format=State,ExitCode recorded in Comments.
- Ticket edits in **Comments only**; Status/Worker lines belong to the lead.
- Budget: **12 failed acceptance checks**.
- If a stage cannot be completed, say which and why, with the job ids — a partial sweep honestly
  reported is worth more than a tidy summary.

## Acceptance

- [ ] **A1** Stage 0: Pot A through the shipped CLI, >=3 seeds, seated/joins and piece-level errors
      recorded, best-of-N stated; if the truncation default loses Piece 08, it is reported, not fixed.
- [ ] **A2** Stage 1: lanes for B, D, E, F, G, I, J from current main, one job each, md5 of binaries
      and of the arm-U output recorded; corpus md5 unchanged before/after; t66 lanes reused with md5s.
- [ ] **A3** Stage 2: out/axes305 for all 163 pieces, seeds per piece recorded, the under-5,000 rule
      shown to have fired on the 44 small pieces, angle-to-released table, runtime.
- [ ] **A4** Stage 3: 4-arm grid on A, B, C, F, G and OO+MM on D, E, I, J, >=2 repeats (>=3 for
      small-pot MM), best-of-N with N, binary + strict tables, E2E sets re-derived with deltas
      against ticket 39 named, H excluded with its reason.
- [ ] **A5** Stage 3: every arm's vehicle pinned by binary md5; 4 h caps declared and any truncated arm
      marked as truncated.
- [ ] **A6** Stage 4: Juglet OO vs MM, >=3 repeats, candidates + seated + mutual consistency,
      best-of-N with N, set beside t67 / t68 / ticket 302.
- [ ] **A7** Stage 5: one render per pot in artifacts/pota305/ (workspace-relative links), plus the
      one-line-per-pot table with the claim type named.
- [ ] **A8** Every job id with its sacct State/ExitCode in Comments; run.json + index.tsv row
      for every run; nothing committed beyond the ticket's own record.
