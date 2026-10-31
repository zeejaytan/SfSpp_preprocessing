# 48 — the method: curvature angle on corpus clouds, no densify

## What to build

The shipped method becomes: read the corpus-conforming input cloud, measure the sherd's own fold radius
on it, set the growth angle by the ticket-43 formula (theta = 3.3573 x S / R_fold), grow, and let the
growth split the cloud so the fracture boundary can be extracted — with **no densify, resample or
covering step anywhere in the path**. Ticket 46's even covering was a diagnostic instrument that stood
in for a working input; once ticket 47 installs real corpus clouds, the covering is retired and the
paper-compliance story simplifies with it.

**Answers:** U19

**Blocked by:** 47 (needs the corpus-conforming Juglet clouds installed).

**Status:** done
**Working in:** chat on Thinkbook16 (2026-10-31)
**Branch:** 48-grow-by-the-curvature-formula-on-corpus-clouds, in /c/PR/worktrees/sfs/48

**Worker:** 5c312d24-cbe9-4678-acc8-68b0a1043c5e (DSH subagent; rate-limited mid-build at the sbatch template, resumed, finished part 1; the lead verified its return and wrote this record)

## Three parts

1. **Verify arm (source unchanged).** Nine Juglet cells on the ticket-47 clouds with
   `SFS_GROWTH_FORMULA=1` and no other `SFS_*` set; eight Pot A cells on their released clouds in the
   same configuration as control. The prediction under test: the pipeline's own voxel downsample of a
   ~1 000 000-point corpus cloud produces an even layout — the mechanism the ticket-46 covering proved —
   so theta lands within ~2 % of the k43 predictions (J1 10.29, J2 12.40, J3 9.35, J4 10.25, J5 8.74,
   J6 8.16, J7 8.65, J8 10.05, J9 12.68 deg) and every piece grows two surfaces. If it does not,
   report where it lands and stop — that is the measurement speaking, not a tuning invitation.
2. **Default flip (source change, only if the verify arm holds).** No-env growth becomes the formula —
   ticket 45's intent, gated off since `2263532`. `SFS_PAPER_THETA=3.4` remains the paper-repro
   override. A default-check run proves no-env cells reproduce the verify arm exactly
   (`SampledWithNormals` md5 equality), the mirror of run `20261031-0200_2263532_t46-default-check`.
3. **Retire the covering.** `cover_cloud46.py` and the stage46 instruments get a DIAGNOSTIC-ONLY banner
   in their headers and a line in `COPIES.md`; confirm no pipeline source references them (none ever
   did — state the check). Ticket 16 (paper-compliance audit) is told in writing: the method's only
   deviation from the paper is the angle rule itself (the paper ships a flat 3.4 measured on Pot A;
   ours derives per sherd); the input side now follows README step 1 exactly, and the paper's IV-B1
   breakline resample at 1.9 mm (ticket 06) is a different, untouched step.

## Honesty lines this ticket carries

- The grown pair on Juglet sherds sits ~0.2-0.3 mm apart (tickets 44 and 46) — two layers of ONE face,
  not the wall's two faces (wall 2.4-3.3 mm). The fracture boundary comes from the breakline step on
  Surface_0; seating itself is judged in ticket 07, not here.
- Pot A thetas read 1.09-1.38x over the k43 predictions on its own released clouds — recorded beside
  the Juglet numbers, not hidden and not re-calibrated away.

## Acceptance

- [x] Verify arm: 9 of 9 Juglet cells on ticket-47 clouds (corpus md5 equals ticket 47's MANIFEST),
      zero covering artifacts in any input; Pot A corpus unchanged. — ran, corpus gate 9/9 ok.
- [x] `theta_check` vs k43 at the 2 % band with per-piece deltas; outcome class and surface counts per
      piece; pair table for every two-surface cell. — produced; the band was **missed on 17 of 17**.
- [x] Pot A control: same config as t45 arm F expectations, counts within 2 %. — exact to 5 dp.
- [x] Default flip: **NOT EXECUTED** — the ticket makes it conditional on the verify arm holding, and
      it did not (0 of 17 in band). The default stays 3.4 with the formula behind `SFS_GROWTH_FORMULA`.
      The re-derivation that would earn the flip is ticket 49.
- [x] Covering retired: **NOT EXECUTED** — the same condition gates it. The covering remains a
      diagnostic instrument; retiring it and telling ticket 16 ride with ticket 49, which replaces
      the measurement the covering was standing in for.
- [ ] `run.json` and index rows for every job (verdicts left empty), poll + final `sacct` recorded.
- [ ] Worker reports numbers and paths; the lead runs its own hidden acceptance check before close.

**Needs-eye:** the 3x3 grown-surface panel on the new clouds, beside ticket 46's.

## Comments
### Part 1 verify arm — run record (worker, 2026-10-31)

**Run** `20261031-1428_93b3c07_t48-t48-verify`, job `34096804`, branch commit `93b3c07`,
partition sapphire, walltime requested 00:30:00, `sacct`: `COMPLETED 0:0`, elapsed `00:15:44`.
Source unchanged (no `mesh_processing_headless.cpp` edit); the formula path is selected by
`SFS_GROWTH_FORMULA=1` alone, verified per cell in `env_proof.tsv` (17/17 read exactly that env,
`SFS_GROWTH_MODE` unset). Binary built in-job from `93b3c07`, md5 `82834d2291357b2759b4266ebb2e0f5e`.
Instruments md5 commit == rundir (14/14 files).

**Corpus gate passed.** 9/9 Juglet clouds on `$DS/Point/Juglet` match `MANIFEST_JUGLET_CC.tsv` on
both `pcd_md5` and `kept_points` (840666, 841310, 840837, 840973, 841282, 841413, 840783, 841399,
841086); `corpus_covering_sweep.txt` is 0 lines (no `*_covering.pcd` under either corpus Point tree);
8/8 Pot A released clouds recorded, not gated. `corpus.diff` and `inputs.diff` are both 0 bytes
(before/after identical), so no input was written to.

**theta vs k43, 2% band: 0 of 17 in band.** Computed / reference / delta:

| piece | computed | k43 | d% | | piece | computed | k43 | d% |
|---|---|---|---|---|---|---|---|---|
| J1 | 10.83673 | 10.29 | +5.31 | | Pot_A_01 | 5.70709 | 4.36 | +30.90 |
| J2 | 11.04426 | 12.40 | −10.93 | | Pot_A_02 | 4.57863 | 3.30 | +38.75 |
| J3 | 8.95950 | 9.35 | −4.18 | | Pot_A_03 | 4.43321 | 3.76 | +17.91 |
| J4 | 9.74587 | 10.25 | −4.92 | | Pot_A_04 | 3.57188 | 2.92 | +22.33 |
| J5 | 9.31229 | 8.74 | +6.55 | | Pot_A_05 | 4.22457 | 3.50 | +20.70 |
| J6 | 8.86226 | 8.16 | +8.61 | | Pot_A_06 | 4.08171 | 3.17 | +28.76 |
| J7 | 9.78652 | 8.65 | +13.14 | | Pot_A_07 | 2.88049 | 2.66 | +8.29 |
| J8 | 9.47194 | 10.05 | −5.75 | | Pot_A_08 | 3.92527 | 3.61 | +8.73 |
| J9 | 9.49636 | 12.68 | −25.11 | | | | | |

Juglet computed/reference ratio: mean 0.981, range 0.749 (J9) to 1.131 (J7); mean |delta| 9.4%,
largest 25.1% (J9). Pot A ratio: mean 1.220, range 1.083–1.387, mean |delta| 22.0% — i.e. Pot A
reproduces the 1.09–1.38x the honesty line already records, digit for digit against t45 arm F.

**The formula's two inputs per cell** (`[SPACING-22]` and `[GROWTH-45]`): on the corpus clouds
S is the pipeline's own voxel spacing, 0.117–0.315 mm (J1 0.31512, J2 0.14153, J3 0.16783,
J4 0.16015, J5 0.21234, J6 0.19726, J7 0.21996, J8 0.17255, J9 0.11744), never reaching the 0.6 mm
clamp; on Pot A 6 of 8 hit the clamp (S=0.60000) and the other two read 0.58174 / 0.29288 / 0.27037.
R_med on Juglet runs 2.38–5.59 mm.

**Surfaces: 12 of 17 pieces grew two; 4 of 9 Juglet.** Two: J1 (420 / 80 775), J3 (540 / 42 040),
J5 (1 269 / 48 068), J6 (1 736 / 40 476), and all 8 Pot A. One cluster, no surface: J2, J4, J7, J8, J9
— each logged `pass 1 done: 1 clusters`, `final clusters=1` after retry (`status_outcome none`).

**Pair table** (`pairs48.tsv`, 12 rows, stage44 protocol). Pot A, all 8: `med_angle_deg` 2.62–4.19,
`coin` 0.000, `med_t_signed` −3.55 to −8.39 mm (a consistent signed offset, one face from the other).
Juglet, the 4 that grew: `med_angle_deg` 42.05 (J3), 43.98 (J6), 65.15 (J5), 65.69 (J1);
`med_nn` 7.07 / 10.07 / 14.59 / 25.89 mm; `coin` 0.0018–0.0072. `nests48.tsv` shared-over-smaller
0.084 (J1), 0.466 (J3), 0.118 (J5), 0.274 (J6).

**Pot A control vs t45 arm F:** thetas identical to 5 decimals on 8/8 (delta 0.00%); clusters 8/8
equal; surface point counts within 0.08% (largest −0.08% on Pot_A_08 surf0). The control arm is
bit-deterministic across runs.

**Anomalies / notes.** (1) `/opt/sfs-pristine` is ABSENT on spartan-bm197, so `pristine.txt` records
absence rather than a baseline — the same as previous stage runs, not new. (2) The run directory tag
reads `t48-t48-verify` because the submitter prefixes `t48-` to the tag I passed (`t48-verify`);
cosmetic, the measurement is unaffected. (3) One earlier submit attempt at commit `79e3925` died in
the renderer (a split newline literal in `submit48.sh`, fixed in `93b3c07`); it never reached sbatch,
left no jobid and no geometry, and its directory was recorded in
`20261031-1427_79e3925_t48-t48-verify-INDEX.txt` before removal.

Artifacts copied to `SfSpp_preprocessing/artifacts/t48-verify/`: `pipeline_cells.tsv`,
`theta_check48.tsv`, `corpus_gate.tsv`, `pairs48.tsv`, `nests48.tsv`, `surfaces48.tsv`,
`control48.tsv`, `corpus.diff`, `inputs.diff`, `corpus_covering_sweep.txt`, `run-meta.txt`,
`geometry_counts.tsv`, the three phase logs, and `juglet_panel48.png`.

Index row appended by the job with `verdict` and `human_note` empty. No verdict, no ticket close,
no parts 2–3 — reported for the lead to conclude.

### Part 1 — lead verification and the mechanism (lead, 2026-10-31)

**The lead's own acceptance check ran and passed** (`C:/PR/artifacts/dsh-handover/48-verify-arm/accept48b.py`,
run against the worktree and the fetched artifacts): source blob `0727cca9da9b` identical to
`origin/main` (blob hashes, not working-tree md5 — CRLF), diff confined to `stage48/**` + this
ticket file (19 files), 17/17 rows carry `theta_env = SFS_GROWTH_FORMULA=1` with `pipeline_rc = 0`,
corpus gate 9/9 `ok` against the ticket-47 manifest, `corpus_covering_sweep.txt` / `corpus.diff` /
`inputs.diff` all 0 bytes, control 8/8 thetas identical to 5 dp and counts within 0.08%.
Index verdict written by the lead: `pass` (the run is valid; the prediction it tested did not hold).

**Why the prediction failed — measured, not guessed.** The formula's two inputs per cell, from
`[SPACING-22]` and `[GROWTH-45]`, compared against the spacing the ticket-43 calibration was made at:

| piece | S_ref (t45) | S_now (corpus) | S ratio | R_cal | R_now | R ratio | theta_ref | theta_now |
|---|---|---|---|---|---|---|---|---|
| J1 | 0.3380 | 0.3151 | 0.932 | 6.319 | 5.594 | 0.885 | 10.29 | 10.837 |
| J2 | 0.2109 | 0.1415 | 0.671 | 3.272 | 2.465 | 0.753 | 12.40 | 11.044 |
| J3 | 0.2153 | 0.1678 | 0.780 | 4.429 | 3.603 | 0.814 | 9.35 | 8.960 |
| J4 | 0.2156 | 0.1601 | 0.743 | 4.046 | 3.161 | 0.781 | 10.25 | 9.746 |
| J5 | 0.2386 | 0.2123 | 0.890 | 5.251 | 4.386 | 0.835 | 8.74 | 9.312 |
| J6 | 0.2237 | 0.1973 | 0.882 | 5.273 | 4.282 | 0.812 | 8.16 | 8.862 |
| J7 | 0.2580 | 0.2200 | 0.853 | 5.737 | 4.323 | 0.754 | 8.65 | 9.787 |
| J8 | 0.2216 | 0.1726 | 0.779 | 4.242 | 3.504 | 0.826 | 10.05 | 9.472 |
| J9 | 0.2035 | 0.1174 | 0.577 | 3.087 | 2.379 | 0.771 | 12.68 | 9.497 |

A log-log regression of `R_now/R_cal` against `S_now/S_ref` gives **R ~ S^0.22**, so
**theta = k x S / R scales as S^0.78** — the fold radius is not spacing-invariant. The constant
`k = 3.3573` was calibrated at the ticket-45 spacing (~0.34 mm on the dumps); on the corpus clouds
the pipeline's own voxel spacing falls to 0.117-0.315 mm and the ratio k x S/R moves with it.
That single exponent explains both halves of the failure: the theta miss (0 of 17) and, downstream,
the five pieces whose growth collapsed to one cluster.

**What this does NOT say.** It does not say the ticket-43 law is wrong — the within-vessel correlation
(Pot A +0.9115, Juglet +0.9581) still holds and Pot A still reproduces its own 1.08-1.39x. It says the
**law as written is not scale-free**: `theta = k x S/R` is only valid at the sampling scale where k was
measured, and any change of input density moves the answer through R.

**Parts 2 and 3 were NOT executed** — the ticket's own instruction ("if it does not [hold], report where
it lands and stop"). No default flip; the covering is not retired; ticket 16 not yet told.
Next step is a decision for the conservator: either calibrate k against the corpus sampling scale
(re-derive it on the corpus clouds, keeping the law), or make R scale-free (fix the neighbourhood's
physical diameter rather than its point count, so R stops depending on S), or restore the density the
calibration assumed. The second is the one that makes the law portable across inputs.

### Close-out (lead, 2026-10-31)

Closed on the ticket's own conditional: the verify arm did not hold, so parts 2 and 3 do not run.
The conservator chose the third route from the list above — **make the fold radius scale-free** — and
it is written up as **ticket 49** (`49-make-the-fold-radius-scale-free.md`).

The measurement that makes ticket 49 well-posed, and that is worth keeping here: `k = 30` neighbours is
not a fixed physical patch. At each piece's spacing it spans

| | patch radius at calibration | patch radius on the corpus clouds | ratio |
|---|---|---|---|
| J1 | 1.044 mm | 0.974 mm | 0.93x |
| J2 | 0.652 mm | 0.437 mm | 0.67x |
| J9 | 0.629 mm | 0.363 mm | 0.58x |

so the estimator was comparing curvature over patches that shrink with the input, by up to 1.7x. That
is the mechanism behind `R ~ S^0.22` in the section above, and it is why a fixed neighbour count cannot
carry a constant between sampling scales. Ticket 49 replaces the count with a fixed physical diameter
and re-derives k on the corpus clouds.

Index verdict for the run: `pass` — the harness measured faithfully; the prediction it tested failed.
Verdict and note written by the lead, not the job.