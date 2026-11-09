# Ticket 323 — Which lines to hand the assembler: make the candidate set hold every pot

**Status:** ready-for-agent
**Answers:** E1
**Depends on:** 322 (the estimator and the Juglet key)
**Blocks:** none
**Worker:** cursor_code (dispatched 2026-11-10, this ticket is the brief)
**Budget:** large

## The ask

The axis estimator is now better than the one we ship — and it made the *end-to-end* result worse.
That sentence is the whole ticket.

Ticket 322 built a profile-thickness cost for an axis and showed it finds the right axis more often
than the shipped ranker: **135 of 163 pot pieces within 10 deg at its first line, against 107**.
It then handed the assembler the top three of those lines and **broke Pot G**, whose joins fell from
10 to 4-5; one line only and Pot G was fine again but A, E, H and J lost joins instead. Every
combination tried failed a pre-registered rule.

So the open question is no longer "can we find the axis". It is:

> **Given a ranked candidate set for each piece, what decides which lines the assembler gets — so that
> every pot keeps its joins at once, and the same rule works on a vessel we have not tuned for?**

Answer it with one formulation. A per-pot table of line counts is not an answer; it is the thing we
already know how to write and already know does not generalise.

## What is already known (do not re-derive; do check it)

**The estimator (ticket 322, `sfs_axes/profile.py`, landed but imported by nothing):** cost of an axis
on a wall = trimmed mean of the smallest principal std-dev of k=24 nearest neighbours in the (r, z)
plane; piece cost = mean over its two walls; Nelder-Mead on 4 dof about the start. Refined from the
reference axis it moves a median **1.5 deg** (>10 deg on 9/163), against **6.4 deg** (>10 deg on 70/163)
for the distance-invariant normal cost.

**Axis-level table (pieces within 10 deg; rank 0 / best-of-3 / best-of-6):**

| set | pots (163) | Juglet (9) |
|---|---|---|
| `axes320`, shipped today | 107 / 133 / 137 | 4 / 6 / 8 |
| `axes322`, profile ranker | **135 / 146 / 151** | **6 / 8 / 8** |

**End to end, and this is the failure to fix:**

| set | what happened |
|---|---|
| `axes322` top 3 per piece (K=3) | A 8/8 15/15, B, C, F, H, J at floor — **Pot G 7/7 4/10 and 6/7 5/10** (floor 10/10) |
| `axes322` line 1 only (K=1) | G 7/7 10/10, B, C, D, F, I at floor — **A 8/8 9/15, E 26-28/31 44-51/62, H 9/11 11/17, J 6/11 5-8/21** |
| hybrid: profile line 1 + `axes320` lines 2-3, 10 deg dedup | 144/163 pots at best-of-3 against a required 146; A 8->7, H 11->10, I 27->26; Juglet 7 |
| Pot G arms: `axes322` line 1 only, and line 1 + `axes320` lines 2-3 | both **7/7 10/10** |

**The mechanism, measured on Pot G (job 34620128):** the profile ranker's first line is right
(G03 2.0 -> 8.0 deg, others 0.9-10.1 deg, 6 of 7 closer); its **second and third lines sit 16.9-51.8 deg
off** and the assembler latches onto them, failing joins 2-3, 2-6, 4-5, 5-7 at 141-154 deg (repeat 1)
and 79-107 deg (repeat 2). Not a line cap, not a sign flip — a plausible-looking wrong line that the
assembler prefers.

**Why more lines help the others:** A, E, H and J lose joins at K=1, so on those pots the *right* line
is not always ranked first, or the assembler needs an alternative to the one it was given. That is the
tension: alternatives rescue A/E/H/J and destroy G.

## Questions you are being asked (answer them, do not merely report)

1. **What does the assembler actually do with a set of lines?** Read the code, not the docs: how many
   lines does it load per piece, in what order, how does it score a candidate pair, and what makes it
   choose a 141 deg join over a correct one? If a piece's bad line can only be excluded by not shipping
   it, say so; if the assembler's own scoring is the thing that can be fixed, say that too.
2. **Is "how many lines" the right question at all?** Consider that the set could be ordered, could
   carry per-line weights, could be pruned by agreement between lines (two independent methods agreeing
   within N deg), or could be chosen per *piece* by a scale-free confidence rather than per pot. Any of
   these is fair game; a per-pot constant is not.
3. **What kills the bad lines without killing the good ones?** The G failure is a line that is 17-52 deg
   off with a good cost. Find a signal that separates it from the lines A/E/H/J need. Candidate signals
   include (yours to test, not a list to work through): margin between the line's cost and the next
   basin's, basin support size, agreement between the profile cost and the normal cost, agreement
   between independent seeds, and whether the line's implied rim closes.
4. **Does the rule hold on the Juglet?** It is a different regime (33 mm across, near-spherical body) and
   we now have a real key for it — see below. A rule that is right on the ten pots and wrong there is
   not general.
5. **Say what you predict before you run it.** Write the prediction and the pass/fail rule into the
   ticket before submitting the jobs, then report against it. Ticket 322's two pre-registered rules both
   failed and that is the reason its result is trustworthy; keep the same discipline.

## Floors the ten pots must keep (two repeats; a pot counts as held if either repeat reaches it)

| pot | sherds | joins |
|---|---|---|
| A | 8/8 | 15/15 |
| B | 9/9 | 15/15 |
| C | 4/4 | 5/5 |
| D | 23-25/28 | 55-60/69 |
| E | 29-31/31 | 57-62/62 |
| F | 5/5 | 7/7 |
| G | 7/7 | 10/10 |
| H | 11/11 | 17/17 |
| I | 25/26 | 59/62 |
| J | 8/11 | 16/21 |

Juglet: report, do not gate — it has no floor yet. **Score it against
`Dataset/Juglet_GT/Juglet_Piece_N_Axis.xyz`, which now exists** (nine lines fitted to the assembled
vessel, README beside them), and remember that **8 of the 18 pairs in `Juglet_simple_graph.txt` do not
touch in the true pose**, so 18 joins is not attainable: the ten touching pairs are the ceiling.

## Constraints

- **One code path, no per-object constants.** The shipped default (`run_potsac`) and `--union` are one
  path. If a rule needs a threshold, it must be scale-free (a ratio, a quantile) or derived per piece
  from the piece's own numbers — and you must show why it is not a per-pot constant in disguise.
- **Fast loop first.** `t322/dump_basins.py` scores all 172 pieces' basins in 85 s on 8 CPUs and
  `t322/rank_rules.py` scores a ranking rule offline in seconds. Rank offline, prove the axis table, and
  only then spend end-to-end jobs. End-to-end runs are much slower than the axis table and are what
  actually decides.
- **Assembler nondeterminism is real.** The same staged inputs give different scores between repeats
  (Pot E returned 30/31 and 31/31 in one job; H's authors' arm 5/11 then 8/11). Two repeats per arm,
  and never call a one-repeat difference a result.
- **Everything runs on Spartan compute nodes**, never the login node: `ssh spartan`, project root
  `/data/gpfs/projects/punim2657/`, `sbatch` with polling via `sacct` (do not use
  `scripts/slurm_poll.sh`, it exits immediately). Record job IDs and final `sacct` State/ExitCode.
- **The corpus never changes.** Inputs are staged by symlink; compare corpus md5s before/after a run.
- **Renders for any geometry claim**, at a view that resolves the scale, into
  `C:/PR/SfSpp_preprocessing/artifacts/pota323/renders/`. A number about seating without a picture is not
  done.
- **No commits.** Leave the working tree for the lead; write your findings into this ticket.

## Where things are

- Estimator: `C:/PR/SfSpp_preprocessing/sfs_axes/profile.py` (landed, unwired). The ranker that uses it
  is `C:/PR/SfSpp_preprocessing/.scratch/pota-repro/t322/profile_ranker.patch` (`git apply` re-applies it;
  it was reverted after the Pot G diagnosis, deliberately).
- `axes322` (181 files): `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0415_d628fc0_t322-axes/out/axes322`
- `axes320` (the shipped set) = `.../runs/20261108-1350_e556fc8_t318a-axes/out/axes318` (181 files) with
  **one** file replaced: `Pot_A_Piece_01_Axis.xyz` from
  `.../runs/20261109-1928_97dad1e_t320-potA/work/axes_k3/Pot_A_Piece_01_Axis.xyz` (8 files there; only this
  one differs from `axes318`). Ticket 321 verified that as the whole of the 320 change.
- Ticket 322's end-to-end runs: `.../runs/20261110-0420_d628fc0_t322-pot<A..J>/score/acc.tsv` (K=3) and
  `.../runs/20261110-05*_d628fc0_t322k1-pot<A..J>/score/acc.tsv` (K=1). The Pot G diagnostic:
  `.../runs/20261110-0446_d628fc0_t322-potG-diag`.
- Assembler: `/data/gpfs/projects/punim2657/sfs_main/`, SIF `sfs_pristine_assembly.sif`, batch tool
  `sfspreproc-docker/hpc/tools/main_pristine_batch.cpp`. The paper chain is ticket 308's; the arms are
  built by the `make_e2e_*.sh` scripts in `t322/`.
- Juglet lanes: `.../runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom` (9 pieces x
  Bl0/Bl1/S0/S1); GT: `Dataset/Juglet_GT`.
- Read `C:/PR/AGENTS.md` and `C:/PR/SfSpp_preprocessing/AGENTS.md` first, and ticket 322 in full.

## Definition of done

1. A written answer to the five questions, in this ticket, with the numbers behind it.
2. A stated rule — "for each piece, ship these lines because ..." — in one paragraph, scale-free.
3. End-to-end evidence for the rule: **all ten pots at floor**, two repeats, job IDs and `sacct` states
   recorded; plus the Juglet scored against the real key and reported.
4. If the rule cannot hold all ten, say which pots it cannot hold and why, with the mechanism — a
   measured limit is a result; a table of per-pot exceptions is not.
5. Renders in `artifacts/pota323/renders/` for anything you claim about seating.
6. Working tree left uncommitted, ticket updated with a minimal set of artefacts, and a short
   `## Comments` trail a later reader can resume from cold.

If you conclude the failure is in the assembler's own pair scoring rather than in the axis set, that is
an acceptable answer — but you must show it with the assembler's code and a measured experiment, not
with an argument.
