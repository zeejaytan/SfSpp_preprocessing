# 52 — ship the capped curvature angle as the default growth angle

**What to build:** the growth angle the pipeline uses with **no `SFS_*` variable set at all** is the
one the conservator has approved — each sherd's own curvature angle, held under 0.9 × the cheapest
smooth crossing measured on that sherd's cloud — and the shipped change is recorded in the fixes
ledger. After this ticket, `env POT_NAME=... SFS_AXIS_FILE=... MeshPreprocessingHeadless` gives the
capped curvature angle; `SFS_PAPER_THETA` still wins over everything; `SFS_GROWTH_FORMULA=0` and
`SFS_GROWTH_CAP=0` still reproduce the old paths exactly.

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let SfS find joins)

**Blocked by:** None — tickets 50 (merged 40c93da) and 51 (merged 9862352) are both on main.

**Status:** in-progress (worker done 2026-11-01; runs complete, P6 failed — branch left UNMERGED for the lead)
**Working in:** DeepSeek worker session, child of the lead (2026-11-01)
**Branch:** 52-ship-the-capped-curvature-angle-by-default, in /c/PR/worktrees/sfs/52

**Worker:** DeepSeek ticket worker (child of lead session-120a72b0)

## Why

The conservator decided on 2026-11-01, in these words: *"alright, i decide to make this fix on by
default. and document it in the fixes ledger"*. Ticket 51 measured that capping the curvature angle by
the piece's own cheapest crossing gives two genuine wall surfaces on 17 of 17 pieces (9 of 9 Juglet,
where the uncapped formula fuses five outright and leaves a junk 421–1,706-point second face on the
other four), and it left `SFS_GROWTH_CAP` default **off**, saying "flipping it is a separate, one-line
change plus a confirming run, and is the conservator's decision". That decision is now taken.

## The code fact that shapes this ticket — the cap is nested, so the formula must flip too

`mesh_processing_headless.cpp:4864-4879` reads `SFS_GROWTH_CAP` **inside** the
`if (!thetaFromEnv45 && thetaFormula46)` block. So:

- with the formula off, theta is 3.4 for every piece, and 0.9 × the smallest crossing measured
  anywhere (PA08, 4.378°) is 3.94° — the cap can never fire. **"Cap on by default" is inert unless the
  formula is also the default.**
- with the formula on and the cap off, five Juglet pieces fuse (ticket 51 arm U).

Both defaults therefore flip together, in one commit, or not at all. This is not scope creep: shipping
the cap alone would ship a knob that does nothing.

## Change (do these in order; nothing else)

1. **Formula default-on.** `bool thetaFormula46 = true;` and the env read becomes an opt-**out**:
   `if (const char* e = std::getenv("SFS_GROWTH_FORMULA")) { if (*e && std::string(e) == "0") thetaFormula46 = false; }`.
   Note the semantics change for an *empty* value: `SFS_GROWTH_FORMULA=` no longer disables anything
   (empty is treated as "unset"); only the literal `0` disables. Say so in the comment.
2. **Cap default-on**, same shape: `bool growthCap51 = true;` with `if (*e51 && std::string(e51) == "0") growthCap51 = false;`.
3. **The shipped default must never die where 3.4 worked.** `medianFoldRadius45()` returns 0.0 when the
   cloud cannot supply a radius and the formula path then does `std::exit(2)`. Keep that hard exit for an
   explicit request (`SFS_GROWTH_FORMULA=1`) — that is evidence a cloud is unusable and the caller asked
   for it — but on the **default** path fall back to theta 3.4 and print one line:
   `[GROWTH-52] FALLBACK piece=<name> median fold radius is <v> (downsampled cloud unusable) - using 3.4`.
   Do not fall back silently and do not skip the cap on that path (the cap is 0.9 × crossing and 3.4 is
   already under it, so nothing fires). Acceptance asserts **zero** FALLBACK lines in both runs.
4. **Rewrite the stale comment** at `mesh_processing_headless.cpp:4828-4841`. Its stated reason for being
   off ("the rule needs a fold radius the corpus clouds cannot supply ... until the input side is
   answered") stopped being true when ticket 47 rebuilt the Juglet clouds with the corpus converter.
   The new comment must say, in its own words: the rule is the shipped default; theta = 3.3573·S/R;
   the 3.4 constant is what a piece falls back to when R cannot be measured or when
   `SFS_GROWTH_FORMULA=0`/`SFS_GROWTH_CAP=0`; `SFS_PAPER_THETA` is the top-level override; the cap
   (ticket 51) is now default on and why (ticket 51 run 20261101-0210_863d4f8_t51-cap: 17/17 two wall
   surfaces, cap fired 9 of 9 Juglet and 0 of 8 Pot A); and that the corpus regression that came with
   the flip is ticket 52's p292 run (name the run id it produced). No sentence may still read "OPT-IN,
   not the default".
5. **`.scratch/juglet-breaklines/stage52/instruments/`** — copy stage51's instrument set and change only:
   - `run_cell52.sh` arms: **D** = *no `SFS_*` variable at all* (the shipped default; this is the arm that
     proves what a user gets), **C** = `SFS_GROWTH_FORMULA=1 SFS_GROWTH_CAP=1` (explicit, ticket 51's
     cap arm), **X** = `SFS_PAPER_THETA=3.4` (the pre-flip shipped path, the escape hatch).
     Default arms per piece: `DCX`. Pass-2 env proof requires exactly those strings (D's proof line is
     empty, so assert the process saw no `SFS_GROWTH*`/`SFS_PAPER_THETA` variable rather than an empty match).
   - `submit52.sh`/`submit52.sbatch.tmpl`: same shape as 51 (PHASE, branch resolved from origin, CRLF gate,
     py_compile, refuse an existing run dir), tag `t52-confirm`, and the unset list must not contain the two
     knobs for arm D — unset them *before* each cell exactly as 51 does, with D exporting nothing.
   - `thetas52.py`/`pairquality52.py`: reuse 51's readers; the summary table must carry, per
     piece×arm: pipeline_rc, clusters, status_outcome, surf0/surf1 points, paper theta from the log,
     `[GROWTH-45]` theta, `[GROWTH-51]` crossing/capped, and the count of `[GROWTH-52] FALLBACK` lines.
6. **Run 1 — 17-piece confirmation** on the real corpus clouds (the ticket-47 Juglet clouds under
   `/data/gpfs/projects/punim2657/Dataset/Point/Juglet`, the released Pot A clouds under the corpus root),
   run dir `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t52-confirm/`, 51 cells
   (17 pieces × DCX), Pot A as the control. Corpus-manifest gate as in ticket 51 (md5 AND kept_points).
7. **Run 2 — the 292 corpus regression at the new default.** `.scratch/pota-repro/292/build292.sbatch:13`
   `COMMIT=` this branch's tip sha (pushed first, then `git -C /data/gpfs/projects/punim2657/sfs_preprocessing fetch origin --prune`
   inside the harness does the rest); then `array292.sbatch` (0-147%10) and `collect292.sbatch`. The array
   refuses any `SFS_*`, which is exactly right here: it can only run the **code** default. Run dir
   `runs/<YYYYMMDD-HHMM>_<git7>_p292-flipcap/`. Compare against the baseline run
   `runs/20261025-0134_787c149_p292-rescore` (281/292 sound at bar, theta 3.4).
8. **Attribution table** `out/attrib52.tsv` in the 292 run dir, one row per piece: `piece`,
   `S_base`, `S_new` (from each run's `[SPACING-22]` line), `theta_new` (`[GROWTH-45]` or the capped
   `[GROWTH-51]`), `capped`, `lane0_median_base/new`, `lane1_median_base/new`, `status_change`.
   Written by a script, never by hand, and quoted whole in the ticket.
9. Append one row to `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` for **each** run, verdict and
   human_note **left empty**.

## Predictions (falsifiable; write them into the ticket before submitting)

1. **D ≡ C exactly.** On every piece, arm D's `[GROWTH-45]` theta and `[GROWTH-51]` crossing must equal
   arm C's to full printed precision (5 dp), and the surface point counts must match exactly. If they do
   not, the flip is not a flip and the ticket is void.
2. **Arm D gives two face-sized surfaces on 17 of 17**, with pair quality in ticket 51's band
   (median nearest-neighbour 78–96 % of each piece's own wall thickness, median across-the-gap
   < 0.05 mm). Not "at least 15 of 17" — 17 of 17 is the claim under test.
3. **The cap fires on 9 of 9 Juglet pieces. Under the uniform 0.6 mm step it now also fires on at least
   one Pot A piece** — PA07 and PA08 were previously sampled at 0.293 / 0.270 mm, so the uniform step
   multiplies their formula theta by ≈2.05, while PA08's measured crossing (~4.4°) caps it near 3.9°.
   Ticket 51 recorded "0 of 8 Pot A capped"; that was under the old spacing law. If the cap fires on 0
   Pot A pieces here, say so and explain why.
4. **No `[GROWTH-52] FALLBACK` line** in either run.
5. **Arm X is byte-exactly the old path**: theta 3.4 on every piece, no `[GROWTH-45]`/`[GROWTH-51]` line,
   and it still fragments/fuses as the shipped binary did before this ticket (record what it does; do not
   claim a prediction beyond "not 17 of 17 with genuine pairs").
6. **The 292 headline stays within 5 sound lanes of 281/292 (i.e. ≥ 276).** The reason to expect movement
   at all: theta rises wherever a piece's old S was below 0.6 mm (theta = k·S/R), which is the class
   section P of the fixes ledger warns about — "a gate loose enough to cross H 02's base-rim also crosses
   P03's flank". The cap is the answer to that objection (a per-piece measured ceiling, not a looser
   constant), and this run is the first test of it. **Decision rule, fixed now:** at bar ≥ 276 → merge and
   record; below 276 → do **not** merge, report the number and the mechanism to the conservator.

## Acceptance

- [ ] `git diff --name-only origin/main...HEAD` touches only `mesh_processing_headless.cpp`,
      `.scratch/juglet-breaklines/stage52/**`, `.scratch/pota-repro/292/build292.sbatch`, the ticket file,
      and (only if the run forced a fix) a named instrument line the ticket records.
- [ ] With no `SFS_*` set, the mesh stage prints `[GROWTH-45]` **and** `[GROWTH-51]` on every piece; with
      `SFS_GROWTH_FORMULA=0` it prints neither and uses 3.4; with `SFS_GROWTH_CAP=0` it prints
      `[GROWTH-45]` and no `[GROWTH-51]`; with `SFS_PAPER_THETA=3.4` it prints neither and uses 3.4.
      All four proved from logs, quoted into the ticket.
- [ ] Run 1: 51 cells, every `pipeline_rc = 0`, corpus gate 9/9 (md5 and kept_points), `corpus.diff` and
      `inputs.diff` 0 bytes, `thetas52.tsv` with 51 rows, predictions 1–5 each marked met or refuted
      with the number that decides it.
- [ ] Run 2: 148/148 elements, build.json naming the commit and both binary md5s, 296 measured /
      294 valid / 292 sound, the five headline numbers, the per-pot table, the below-bar list with
      medians and coverages, `attrib52.tsv`, corpus md5s unchanged 148/148, geometry assertion clean.
- [ ] Prediction 6 answered with the number, and the merge decision rule applied as written.
- [ ] `python C:/PR/scripts/check_intent_links.py` passes for the ticket file.
- [ ] Code tickets: branch merged into main and pushed, no job still running from it, worktree removed,
      branch deleted locally and on GitHub.

## Out of scope (the lead does these, not the worker)

- The `FIXES-LEDGER.md` row (section Q, row 12) and the superseding of row 5 — the lead writes it after
  run 2, because the "what it bought" cell must quote the measured corpus number.
- The `intent/U19-...` "Where it stands" update and the ticket `## Result` section with the verdict.
- Any change to `SFS_GAP_PLACE`, the assembler, or the end-to-end acceptance (ticket 07) — those wait
  until the growth step is settled (conservator, 2026-10-31).

## Facts already established — do not re-derive

- Block layout on main 9862352: formula env read at `mesh_processing_headless.cpp:4842-4844`, body
  `:4845-4857`, cap comment `:4858-4863`, cap body `:4864-4878`, block closes `:4879`;
  `thetaCross51()` at `:1103-1170`; `medianFoldRadius45()` at `:1175-1263`; the theta is consumed at
  `:3849` and `:4944`; `SFS_GROWTH_MODE` is read at `:4895-4915` and still outranks nothing (it rewrites
  paperTheta only in `outcome` mode, which this ticket does not touch).
- Nothing in the repo asserts theta == 3.4: a grep for `3\.4` over `tests/`, `scripts/` finds nothing, so
  the flip breaks no local gate.
- `[SPACING-22]` since ticket 50 gives `S = max(0.6, s0)`; Pot A PA01–PA06 were already at 0.600 under the
  old law, PA07 0.293 and PA08 0.270 were not. The 292 baseline (787c149) predates ticket 50, so a lane
  delta in run 2 can come from S as well as from theta — that is what `attrib52.tsv` is for.
- Ticket 51's run (job 34132847 at 863d4f8) predates the ticket-50 merge and ran the **old** spacing law;
  its theta table must not be used as the expected table here. Its outcome table (17/17 two surfaces,
  pair separation 78–96 % of wall) is the thing to reproduce.
- 17-piece harness mechanics to copy, not reinvent: `stage51/instruments/run_cell51.sh` (manifest gate,
  pass 2 env proof, pass 3 theta proof, MIN_LEFT_S/CELL_BUDGET_S), `submit51.sh` (CRLF gate, py_compile,
  run-dir refusal), `stage_synth_p40.sh` (stage a piece and produce the growth cloud),
  `pairquality51.py` (B→A cKDTree median), `wall40.py` (wall thickness per piece).
- 292 harness facts: `array292.sbatch:45-49` refuses any `SFS_*` and writes `out/errors/<piece>.tsv`
  instead; `build292.sbatch:43-51` cmake/make inside `pcl_191_nurbs.sif`; `collect292.sbatch` re-checks
  corpus md5s and asserts no file > 1 MiB outside `bin/`.
- Spartan: the DSH ssh plugin is the only route (`ssh_exec`, `ssh_download`, alias `spartan`);
  `scripts/slurm_poll.sh` does not run here; `ssh_exec` times out near 120 s, so poll with `sleep` inside
  one remote command and retry on empty output. Never recursive-find or `du` under `/data/gpfs`.
- Run index row format (tab-separated, header `runid jobid commit tag verdict human_note`) and
  `index_row.sh` in the 292 dir: verdict and human_note stay empty for a person.


## Worker answers (2026-11-01, ticket worker; no ## Result — that is the lead's)

**Branch tip:** 4997593 (pushed, NOT merged). Commits: ba9e425 (the flip + stage52 instruments),
6c50ad7 (build292.sbatch COMMIT=), 7a5fc12/3c573c0 (fixes to my own commit text), fc0a70e (env
probe greps only SFS_GROWTH_*/SFS_PAPER_*), e6f2d6a (F/K opt-out arms for the acceptance env
cases), 4997593 (commit C: backfills the p292 run id into the growth comment). Code commit both
runs built from: ba9e425345b92658d37a5e8bda732c6fd8efe43a.

### Run 1 — 20261101-0440_fc0a70e_t52-confirm, job 34149518, sacct COMPLETED 0:0 (12m49s)

(A first attempt 20261101-0426_6c50ad7, job 34134459, FAILED its env proof from an instrument bug
of mine — fixed in fc0a70e; its index row is left as the record.)

- 51/51 cells pipeline_rc=0; corpus gate 9/9 Juglet (md5 AND kept_points vs the ticket-47
  manifest); Pot A recorded-not-gated; corpus.diff and inputs.diff 0 bytes; thetas52.tsv 51 rows.
- **Env cases, quoted from real logs** (Juglet_Piece_1, out/cells-pipeline/Juglet_Piece_1_arm*/
  /logs/mesh.log; the F and K cells were run by job 34149757 into the same run dir, and
  env_cases52_env_proof.tsv records the probes):
  - no SFS_* (arm D): `[GROWTH-45] piece=Juglet_Piece_1 S=0.60000 R_med=6.06475 theta=19.03055`
    and `[GROWTH-51] piece=Juglet_Piece_1 crossing=9.178729 capped=1 theta=8.26086` — both present.
  - SFS_GROWTH_FORMULA=1 SFS_GROWTH_CAP=1 (arm C): lines identical to D.
  - SFS_GROWTH_FORMULA=0 (arm F): no GROWTH line at all; `[PAPER-234] paper grow: thetaDeg=3.40000`.
  - SFS_GROWTH_CAP=0 (arm K): `[GROWTH-45] ... theta=19.03055`, no [GROWTH-51];
    `[PAPER-234] paper grow: thetaDeg=19.03055` — the formula, uncapped.
  - SFS_PAPER_THETA=3.4 (arm X): no GROWTH line; `[PAPER-234] paper grow: thetaDeg=3.40000`.
- **P1 (D≡C): MET on theta and crossing 17/17** (equal to 5 dp; theta_check52.tsv). Surface point
  counts equal for the 11 Juglet pieces; **REFUTED in the strict count sense for 6 Pot A pieces**
  (deltas of 1-4 points, e.g. PA01 surf0 67101 vs 67102, PA05 31793 vs 31789) with identical env
  and identical theta — clustering nondeterminism, not env leakage (the probe proves D saw no
  SFS_* growth variable at all).
- **P2: 16/17 MET.** Arm D two face-sized surfaces 17/17; Juglet med_nn 81.9-95.6 % of own wall
  (inside the 78-96 band), med_across 0.017-0.036 mm. **Juglet_Piece_8 REFUTED**: surf1 = 145
  pts, med_nn 32.3 % of wall, med_across 0.306 mm. Context: t51 (old spacing law) had J8 healthy
  at 39428/33527, and today's paper-theta arm X gives J8 no surface file at all, so J8's collapse
  tracks the ticket-50 spacing change at least as much as this flip — D is the best of today's
  three arms on J8.
- **P3: REFUTED on both halves.** Cap fired 8/9 Juglet (all but Piece_6, crossing 24.03 uncapped)
  and 0/8 Pot A (crossings 8.1-11.0, capped=0 everywhere). On the released Pot A clouds the
  crossing never exceeds the formula theta (S=0.6 everywhere under the new spacing law, R_med
  large), so the cap is inert there; the PA07/PA08 mechanism the prediction assumed died with the
  old S values.
- **P4: MET.** Zero [GROWTH-52] FALLBACK lines in run 1 (job log and every cell) and run 2 (all
  148 piece logs).
- **P5: MET.** Arm X: thetaDeg=3.40000 from the log on every piece, no GROWTH-45/51, cluster
  counts recorded (J1 15 clusters, J4 1 with status none).

### Run 2 — 20261101-0428_ba9e425_p292-flipcap, jobs 34146541 (build) / 34146545 (array 0-147%10) / 34146550 (collect), all COMPLETED 0:0

- 148/148 elements; 296 measured / 294 valid / 292 sound as the harness expects; corpus md5s
  unchanged 148/148 (collect: corpus_unchanged=YES); no file > 1 MiB outside bin/.
- **Headline: 237/292 sound at bar (81.2 %)** vs baseline 20261025-0134_787c149_p292-rescore
  281/292. Also 239/296 measured at bar (80.7 %); 0 lanes with jumps; largest step 7.812 mm
  (Pot_E_Piece_18 lane 1).
- **P6: REFUTED — 237 < 276, so the branch is NOT merged** (rule applied as written). Mechanism
  (attrib52.tsv, 148 rows, in the run dir): **41 measured lanes lost at bar, 0 gained, all in
  pots C-J; Pot A untouched (0 lane changes)**. Lost lanes show coverage collapse (cov_ours
  typically 100 % to 55-80 %) with medians rising as the larger theta grows clusters across true
  edgelines — Pot_J_Piece_03 lane 1 0.365 to 14.184 mm (cov 100 to 4 %), Pot_E_Piece_15 lane 0
  0.357 to 12.380 mm (cov 100 to 0 %). The flip raises the default theta from 3.4 to 4.1-9.6 deg
  across the corpus; 16 pieces hit the cap. S_new = 0.6 everywhere; the baseline predates the
  spacing merge and its logs carry no S line, so S_base is recorded "na" — the Pot A vs C-J
  contrast (same theta change, no lane change on Pot A) is the attribution the lead should weigh.
- The 292 summary/potpng scripts were not in the extracted harness; copied unchanged from the
  baseline run dir and run (logs/summary292.log); out/summary.md is in the run dir.

### Deviations and worker errors (all recorded)

1. Env-probe bug, attempt 1 (job 34134459): the probe listed SFS_AXIS_FILE/SFS_STATUS_FILE, set
   in every arm by the stage51 protocol, so arm-only want-lists never matched. Fixed in fc0a70e.
2. Commit e6f2d6a's message names job 34152916 for the F/K env-case run; the real job is
   **34149757**. The pushed message is wrong; not force-corrected.
3. The F/K env-case job reused run 1's run dir and truncated out/cells-pipeline/pipeline_cells.tsv
   to its two rows; restored the 51-row table verbatim from out/phase5_cells.log. env_proof.tsv
   and theta_proof.tsv gained the F/K rows additively (54 rows).
4. Two run-2 chains were scrapped before the good one (34134467-9 wrong sha — my typo;
   34134471-3 commit absent on Spartan before the explicit branch fetch).
5. index.tsv: the p292-flipcap row (jobid 34146541+34146545+34146550, commit ba9e425) was
   appended by me with EMPTY verdict/human_note; this harness's collect does not write it.

### Acceptance checklist as it stands for the lead

- Diff scope, four env cases from real logs, run-1 and run-2 numbers, P6 + merge rule: done as
  above.
- check_intent_links.py: fails on this ticket only through the pre-existing U19 gap shared by
  every feature ticket 07-52 ("answers U19, which does not exist. Known: E1"); U19 is the lead's
  to create; ticket 52 adds no new breakage.
- Merge / worktree removal / branch deletion: NOT done — P6 failed; branch left unmerged at
  4997593 per the rule. Verdict, FIXES-LEDGER row, and intent/U19 stay with the lead.
