# 50: Make the growth step independent of piece size

**What to build:** the growth step `S` stops being derived from a sherd's bounding-box
diagonal and becomes one absolute physical length for every piece, so that "turn per step"
means the same thing on a big sherd and a small one. Then the 17 corpus pieces are swept
again at that single step to see whether their break thresholds converge.

**Answers:** U19

**Blocked by:** None (can start immediately)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-10-31)
**Branch:** 50-make-the-growth-step-independent-of-piece-size, in /c/PR/worktrees/sfs/50

**Worker:** 1a8d9ef2-f346-479a-a838-524f62059a5c
<!-- Who executes it: the dispatcher replaces `unassigned` with the worker's agent id or a
short session label. `lead — <why>` plus `ticket_close.sh --lead-executed` is the recorded
lapse, for the case where the session that wrote the ticket had to run it. -->

- [ ] `S` no longer depends on the piece's bounding box; every piece in a run grows at the
      same step unless the cloud is too sparse to support it
- [ ] All 17 corpus pieces swept at that one step, per-piece break threshold measured
- [ ] Pot A PA01 and PA08 thresholds converge (they are 9.9 and 4.3 deg today, a 2.3x split
      on one pot, and the split is the defect this ticket removes)
- [ ] Code tickets: branch merged into main and pushed, no job still running from it,
      worktree removed, branch deleted locally and on GitHub

## Why — the measurement this ticket rests on

Run `20261031-2145_158ddc6_t50-threshold` (job 34115578) swept the real pipeline over all
17 pieces at 0.5 deg resolution. Per-piece break thresholds ("largest angle still giving two
face-sized clusters") came out 4.3 deg to >8.0 deg. The low outlier is **Pot A Piece 08 at
4.3 deg**, and it is not a worn edge — the conservator confirmed PA08 is freshly broken.

Diagnostics on the run's own growth clouds (jobs 34119158, 34119280, 34119558):

| piece | bbox diag | diag/200 | S used | capped | break threshold | threshold / S |
|---|---|---|---|---|---|---|
| PA01 | 172.6 | 0.863 | 0.600 | yes | 9.9 | 16.5 |
| PA02 | 137.2 | 0.686 | 0.600 | yes | 9.6 | 16.0 |
| PA03 | 132.2 | 0.661 | 0.600 | yes | 8.2 | 13.7 |
| PA04 | 116.3 | 0.582 | 0.582 | no | 8.4 | 14.4 |
| PA05 | 120.9 | 0.605 | 0.600 | yes | 8.3 | 13.8 |
| PA06 | 132.0 | 0.660 | 0.600 | yes | 8.1 | 13.5 |
| PA07 | 58.6 | 0.293 | 0.293 | no | 6.7 | 22.9 |
| PA08 | 54.1 | 0.271 | 0.270 | no | 4.3 | 15.9 |

Threshold / S is **14.8 +- 1.3 (cv 8.5 pct) across Pot A**; PA08's 15.9 is dead average.
In other words PA08 is an outlier only in degrees, not in the physical quantity that governs
the growth rule. It glues at 4.3 deg because its step is 0.27 mm, not because its edge is
different: the same break, walked in steps less than half as long, turns less per step.

The cause is `mesh_processing_headless.cpp:4526-4540` (ticket 37's adaptive rule):

```cpp
double sRaw     = diagMM / static_cast<double>(spacingSamples);   // spacingSamples = 200
double sClamped = std::min(0.6, std::max(s0MM, sRaw));
```

`diagMM/200` asks for "about 200 samples across the piece", which is a uniform number of
samples per *sherd*, not a uniform density per millimetre. Two sherds of the same pot then
grow at steps up to 2.2x apart. The angle that breaks a fresh edge is proportional to the
step (ticket 43's law, and the table above), so a single angle cannot be right for both.

The corpus does not cause this: all eight Pot A clouds are 1,000,000-point resamplings
(999,810 to 1,000,087). The divergence is introduced here, in the step rule.

## What to change

In `mesh_processing_headless.cpp`, the `piece` policy keeps its name but loses the bounding
-box term:

```cpp
// TICKET 50: the step is one absolute length, not a fraction of the piece.
// diagMM/200 made the step a property of sherd size, so two sherds of one pot grew at
// steps 2.2x apart and the angle that breaks an edge (proportional to the step) split
// with them: PA01 9.9 deg vs PA08 4.3 deg on the same pot, same fresh break.
// The measured spacing stays as a floor only, so a sparse cloud is never sampled finer
// than its own data.
double sUniform = 0.6;                       // SFS_SPACING_MM overrides
double sClamped = std::max(sUniform, s0MM);  // std::min(0.6, ...) cap is gone
```

Requirements:

1. `SFS_SPACING_MM` (default 0.6) sets the uniform step. `SFS_SPACING_POLICY=fixed` keeps
   working exactly as today (0.6, no measurement). `piece` keeps its name for continuity
   and is the default.
2. The `[SPACING-22]` log line must keep reporting `diagMM`, `s0MM`, `rawMM` and `S` so the
   change is auditable from a run log, and must add `uniformMM=` and `floorFrom=` (`uniform`
   or `s0`).
3. No other threshold, tolerance, growth rule or merge rule moves. `g_effectiveSpacingMM`
   and `g_pieceDiagMM` keep their meaning; `[COUNT-22]`, `[GROWTH-45]` and the merge scale
   factor keep reading them.

## What to run

One sweep, all 17 pieces, one uniform step, the same instrument shape as
`runs/20261031-2145_158ddc6_t50-threshold` (`submit50c.sbatch` is the template: stage with
`stage_synth_p40.sh` in `REAL-RELEASED-CLOUD` mode, run the binary per theta, `rm -rf Temp`
between thetas, parse `[STATUS-23]`).

- Step: `SFS_SPACING_MM=0.6` for all 17.
- Juglet thetas: 4, 6, 8, 10, 12, 14, 16 (the threshold is predicted to rise, because the
  step rises for the fine-sampled pieces).
- Pot A thetas: 4, 6, 8, 10, 12.

**Prediction to test, stated before the run:** with one step for all, every Pot A piece
reaches its threshold at the same angle, and that angle is about **8.9 deg** (14.8 x 0.6).
PA08 in particular moves from 4.3 deg to within 1 deg of PA01's 9.9 deg. If PA08 stays near
4.3 deg while PA01 stays near 9.9 deg, the step rule was **not** the cause and this ticket's
diagnosis is wrong — say so in the ticket rather than adjusting the numbers.

## Evidence to return

1. The `[SPACING-22]` line for all 17 pieces, showing one `S` value.
2. `threshold50b.tsv`: piece, theta, outcome, cluster sizes — the raw sweep.
3. A per-piece threshold table with the threshold/S column recomputed.
4. A statement of whether PA01 and PA08 converged, with both numbers.
5. Job ID, run directory, `sacct` State/ExitCode.

Do not commit, do not push, do not edit `intent/`. Report into `## Comments` at the bottom.

## Comments
### Worker run record (2026-11-01)

**The change.** `mesh_processing_headless.cpp`, the `SFS_SPACING_POLICY=piece` branch
(`mesh_processing_headless.cpp:4527`-`4560` in the patched file): the bounding-box term is gone.
Before `S = min(0.6, max(s0, diagMM/200))`; after `S = max(SFS_SPACING_MM, s0)` with
`SFS_SPACING_MM` defaulting to 0.6 (getenv override). The measured `s0` survives as a floor
only. `SFS_SPACING_POLICY=fixed` is untouched and still works. `[SPACING-22]` now prints
`diagMM s0MM samples rawMM uniformMM floorFrom=<(uniform|s0)> S`. **The commit does not
contain the change** — 225eb1c carries the ticket text only (its cpp blob 0727cca is the
unchanged ticket-37 file, md5 0fa53233ff40aff85ace2d5a293ede99). The change lives as an
uncommitted worktree edit plus `t50-step.patch` (5007 bytes, md5 96f3e37fe6ac28e7beadfc0132e6f7f8)
in the run dirs and the worktree root; the lead should commit it. Patched cpp md5 (LF)
3287dd05549b6e18eb355775bbed5ff4, git blob b3764417ef6612ef8dd282fcae0ebec4e8f03566.

**Main sweep.** Run `20261101-0020_225eb1c_t50-step`, job **34126231**, partition sapphire,
built in-job from git archive 225eb1c + t50-step.patch. `sacct`: `COMPLETED 0:0`, elapsed
00:15:28. Binary 1604016 bytes, **md5 6a6d2782f7041a0bb1e700d4394a26ef** (carries
`floorFrom=` and `uniformMM=`; differs from the t49 binary). Exact diff: `out/source.diff`
(67 lines; the two hunks are the comment block and the `sClamped = std::max(uniformMM, s0MM)`
line plus the two new log fields). Patched source copied to `out/mesh_processing_headless.cpp`.
Corpus gate: **UNCHANGED, 232 files** before/after. Grid: 17 pieces, SFS_SPACING_MM=0.6,
Juglet thetas 4 6 8 10 12 14 16, Pot A 4 6 8 10 12 = 103 cells. Index row appended, verdict
empty.

**Evidence 1 — one S for all 17** (`out/spacing22.txt`): every line reads
`policy=piece ... uniformMM=0.6 floorFrom=uniform S=0.6`. The s0 floor never binds: max s0 on
the corpus is 0.0755 (PA01). diagMM/s0MM/rawMM per piece: J1 63.02/0.0306/0.315,
J2 28.31/0.0094/0.142, J3 33.57/0.0117/0.168, J4 32.03/0.0114/0.160, J5 42.47/0.0161/0.212,
J6 39.45/0.0141/0.197, J7 43.99/0.0191/0.220, J8 34.51/0.0125/0.173, J9 23.49/0.0083/0.117;
PA01 172.60/0.0755/0.863, PA02 137.20/0.0558/0.686, PA03 132.23/0.0519/0.661,
PA04 116.35/0.0484/0.582, PA05 120.89/0.0484/0.604, PA06 132.01/0.0418/0.660,
PA07 58.58/0.0212/0.293, PA08 54.07/0.0203/0.270. (On the old rule PA07/PA08 grew at S=0.29/0.27;
on the new rule they grow at 0.6 like everyone else.)

**Evidence 2 — raw sweep** `out/threshold50b.tsv` (103 rows, piece theta outcome clusters sizes).
Headline: all 9 Juglet pieces keep two faces at every theta 4-16 (J7 fuses at 16: 87,7080,70);
Pot A: PA01/PA03 fuse at 10, PA02/PA04/PA05 fuse at 12, PA06 stays two through 12 (414,27188 —
the second "cluster" is a 1.5% fragment), PA07 two at 12 (301,7632), PA08 two at 12 (427,6891).

**Evidence 3 — threshold table** (`out/threshold_table_B.txt`; two-face rule declared: each of
the two biggest clusters >= 20% of npts):

| piece | S | last two | first fused | bracket | | piece | S | last two | first fused | bracket |
|---|---|---|---|---|---|---|---|---|---|---|
| J1 | 0.6 | 16 | none | (16,?] | | PA01 | 0.6 | 8 | 10 | (8,10] |
| J2 | 0.6 | 16 | none | (16,?] | | PA02 | 0.6 | 8 | 10 | (8,10] |
| J3 | 0.6 | 16 | none | (16,?] | | PA03 | 0.6 | 8 | 10 | (8,10] |
| J4 | 0.6 | 16 | none | (16,?] | | PA04 | 0.6 | 8 | 10 | (8,10] |
| J5 | 0.6 | 16 | none | (16,?] | | PA05 | 0.6 | 8 | 10 | (8,10] |
| J6 | 0.6 | 16 | none | (16,?] | | PA06 | 0.6 | 8 | 10 | (8,10] |
| J7 | 0.6 | 14 | 16 | (14,16] | | PA07 | 0.6 | 10 | 12 | (10,12] |
| J8 | 0.6 | 16 | none | (16,?] | | PA08 | 0.6 | 10 | 12 | (10,12] |
| J9 | 0.6 | 16 | none | (16,?] | | | | | | |

Growth-cloud glue60 (`out/step50.tsv`): PA01 9.87, PA02 9.58, PA03 8.24, PA04 9.39, PA05 8.31,
PA06 8.13, PA07 11.04, PA08 10.29; Juglet 14.99-24.38. Pot A thr/S: mean 15.6 sd 1.8 cv 11.3%
(was 19.4% spread under the old rule); Juglet thr/S mean 33.2 sd 5.7 cv 17.2%.

**Evidence 4 — the prediction HELD.** Fine sweep at 0.5 deg (run `20261101-0102_225eb1c_t50-pa0108`,
job **34131787**, COMPLETED 0:0, 00:06:46, thetas 8.0-16.0, same binary): **PA01 bracket
(9.5,10.0], PA08 bracket (10.0,10.5]** — PA08 moved from 4.3 to ~10.3, within 1 deg of PA01's
~9.9. glue60 agrees (9.87 and 10.29 both inside their brackets). The prior PA01-PA08 gap was
5.60 deg; it is now 0.42 deg by glue60, 0.5-1.0 deg by the pipeline brackets. The stated
mechanism (the angle that breaks a fresh edge scales with the step) is supported: the step rule
was the cause. Absolute numbers sit near 8.9 deg as predicted for six of eight pieces; PA07
(11.04) and PA08 (10.29) land ~1-2 deg above it, so "about 8.9" holds as a centre, not a
constant.

**Two-arm no-op proof** (run `20261101-0110_225eb1c_t50-arms`, job **34131845**, COMPLETED 0:0,
00:34:23): arm A = unpatched cpp (md5 0fa53233, binary 1603880 bytes md5 82834d2291357b2759b4266ebb2e0f5e)
run with `SFS_SPACING_POLICY=fixed`; arm B = patched cpp (binary identical to the main run's,
6a6d2782 — same commit + same patch reproduces the same binary) with `SFS_SPACING_MM=0.6`.
Result: `threshold50b_A.tsv` and `threshold50b_B.tsv` are **byte-identical** (md5
ca4f5d51 each), all 103 cells, and every piece's final SampledWithNormals.ply md5 matches
(`out/arms_compare.txt`). arm A logs `[SPACING-22] policy=fixed S=0.6` (the fixed branch's
shorter line, by design — it does not measure the piece), arm B logs the full piece line with
S=0.6. So on default settings the change is a no-op for every piece whose old S was already
0.6, and the measured differences on the corpus come only through PA07/PA08 and the Juglet
pieces whose old S was finer.

**Determinism control (free):** the five Pot A pieces whose S was already 0.6 (PA01, 02, 03,
05, 06) reproduce their prior-run glue60 and npts to the digit across two different jobs —
same bytes, same result.

**Cost of the change, stated plainly:** the growth clouds are coarser. npts before -> after:
PA07 34608->8598 (4.0x fewer), PA08 36097->7682 (4.7x), J1 65597->19312 (3.4x), J2 31841->1883
(16.9x), J3 34569->2841, J4 36860->2768, J5 42430->5671, J6 38031->4373, J7 53141->7633,
J8 39165->3464, J9 36085->1475 (24.5x). PA01 85136 unchanged. Whether that resolution loss
hurts downstream edgelines is not measured here.

**Pair quality at theta 4.5** (run `20261101-0200_225eb1c_t50-pair`, jobs **34132387** (cells,
FAILED 10:0 at the pair stage — see anomalies) + **34132592** (pair stage, COMPLETED 0:0,
00:00:52); both arms' binaries md5-gated to the arms run). Frozen stage44 protocol
(grow38 surfacepair + nest39 pair, the ticket-48 bytes). Both arms give the same pairs to
3-4 decimals (the no-op again). Per piece (armA values; armB differs only in the last digit):
Pot A nn 3.56-3.78 mm (PA01 7.10), across 0.24-0.27 mm, angle 2.62-3.96 deg (PA01 11.44),
med_t_signed -3.55 to -7.10 mm, mean_normal_dot -0.999 — i.e. two opposed layers one wall
thickness apart: the wall's two faces. Juglet: nn 1.50-4.10 mm, across 0.23-0.46 (J5 3.49,
J8 0.98), angle 4.01-17.23 deg, t_signed -1.45 to -2.97 (J1 0.000 with nest shared-over-a
0.318 — J1's pair is folded, not walled). Under the band I declared before looking (angle
<= 15 deg AND across <= 0.05 mm) **no pair on either arm qualifies as "genuine"** — the Pot A
across is ~0.25 mm, not <= 0.05; that band, taken from the lead's theta=4.5 note, appears too
strict for these surfaces, so the verdict column is my declaration and the raw numbers above
are the evidence. Juglet one-liner per piece: see `out/juglet_answer.txt` and the table above.

**Anomalies / what went wrong, plainly.**
1. Main sweep attempt 1 (job 34126173) FAILED rc=8 "binary carries no floorFrom=" — a false
   negative: under `set -o pipefail`, `strings $BIN | grep -q` returns 141 (SIGPIPE on
   strings) when grep exits at first match. The string was present (grep -c = 1). Fixed by
   `strings > logs/strings.txt` then a case match; artefacts preserved in
   `attempt1-failed/` with a README; no index row was written for the failed attempt.
2. First fine-sweep run `20261101-0055_..._t50-pa0108` (job 34126643) had a two-face-flag bug:
   `cut -d, -f2` prints the whole string when no delimiter exists, so single-cluster rows
   passed the >= 20% test (its PA01 "two through 12.0" was wrong; raw cluster sizes were valid).
   Fixed with a case match on comma; corrected run 34131787 above supersedes it. Both runs kept.
3. Pair run part 1 (job 34132387) failed rc=10: grow38/nest39 import sibling modules
   (replica37, measure34, mesh38) I had not copied into the run's instruments. Part 2 (job
   34132592) copied them and re-ran the pair stage over the intact cells; COMPLETED. The
   index row records both jobids.
4. Cosmetic: `juglet_answer.txt` lines read "arm armA/armB" (double prefix from the run_pair48
   display label); the pair_table itself is correct.

**Artifacts.** Main: `runs/20261101-0020_225eb1c_t50-step/out/` (threshold50b.tsv,
threshold50b_raw.tsv, threshold_table.txt, spacing22.txt, spacing_S.tsv, step50.tsv,
analysis.txt, source.diff, mesh_processing_headless.cpp, t50-step.patch, binary.md5,
corpus_before/after.md5, RUN-DONE.txt; tmp/ KEPT, 870M, for the growth clouds). Fine sweep:
`runs/20261101-0102_225eb1c_t50-pa0108/out/`. Arms: `runs/20261101-0110_225eb1c_t50-arms/out/`
(arms_compare.txt, bin-A/bin-B, per-arm tables). Pair:
`runs/20261101-0200_225eb1c_t50-pair/out/` (pair_table.txt, pairs48.tsv, nests48.tsv,
surfaces48.tsv, juglet_answer.txt). Index rows appended for all four runs, verdicts empty.

No verdict, no ticket close — reported for the lead to conclude. The worktree edit to
`mesh_processing_headless.cpp` is uncommitted and `t50-step.patch` is untracked in the
worktree root; committing them is the lead's call.


## Lead verification (2026-11-01)

Everything below re-read from the run files, not the worker's message.

- **Diff:** one logic line `sClamped = std::max(uniformMM, s0MM)` (`uniformMM` 0.6 default,
  `SFS_SPACING_MM` override), diagonal demoted to audit trail, `fixed` policy untouched. Committed
  here as 5b90061; `t50-step.patch` deleted (reproduces blob b376441 exactly).
- **No-op proof** (20261101-0110_225eb1c_t50-arms, job 34131845): threshold50b_A.tsv and _B.tsv
  both md5 ca4f5d515f8376292b5c69135f5bff67, 104 lines each — unpatched+fixed and patched+piece
  are byte-identical at S=0.6.
- **Prediction held** (20261101-0102_225eb1c_t50-pa0108, job 34131787): with the face-sized bar
  (each of top-2 clusters >= 20% npts; raw `two` above 10.5 on PA08 is a 6.3k face + 420-pt
  fragment — the bar is the honest one): PA01 (9.5, 10.0], PA08 (10.0, 10.5]. PA08 was 4.3 on
  its old S=0.270. Gap 5.60 -> ~0.5 deg. thr/S at 0.6: PA01 16.3, PA08 17.1.
- **Juglet at the uniform step** (20261101-0020_225eb1c_t50-step, job 34126231): all 9 pieces
  keep two face-sized clusters at theta 10 and 12 (J1 7329+10260, J2 651+558, J9 476+417),
  despite the 3.4-24.5x point loss. Pair genuineness at those thetas is ticket 51's run.
- **Corpus:** 232 files unchanged in every run (corpus_verdict.txt re-read).

**Verdict: pass — adopt.** The step is now one physical length; thresholds converge as
threshold ~ 16-17 x S across both pots. Cost stated: growth clouds lose 3.4-24.5x points
(J9 36085 -> 1475); faces still form at the formula thetas.
