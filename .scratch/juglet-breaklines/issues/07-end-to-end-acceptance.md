# 07: End-to-end acceptance — does the Juglet now join, and is Pot_A unharmed

**What to build:** the falsifiable end state. A regenerated Juglet bundle
whose true mates pass the assembler's own join test at correct placement,
with the working sample unchanged — and a witnessed render, because a
passing number is not something to believe on its own.

**Answers:** U19 (the vessel-level claim, in the umbrella `intent/`) and E1 (its
preprocessing half)

**Blocked by:** none — 06 resolved 2026-09-30, so 01–06 are settled

**Status:** results-in
**Working in:** chat on Thinkbook16 (2026-10-27); stage 1 run `20261027-0055_d8af9d2_p07-juglet-stage1`, jobid 33834939
**Branch:** 07-end-to-end-acceptance, in /c/PR/worktrees/sfs/07
at the end). Pot_A half done by our own output (15/15,
`t14_patches` arm, re-verified identical under ticket-17 code); Juglet half
retracted-and-remeasured: old 0/10 rested on copied surfaces (ticket 17)
and is withdrawn, not compared. Clean state 2026-09-30: **0 of 5 scorable
touching pairs pass, 5 touching pairs unmeasurable** (pieces 3 and 9
produce no surfaces — single cluster after 30 loosened retries — and skip
loudly). Seven present breaklines md5-unique, zero copies.
## 2026-09-28 — Pot_A acceptance met, by our pipeline, not the sample

- [x] **Pot_A at 15/15 on our output.** The old criterion ("held at 15/15")
      measured the authors' sample twice over; it is now met genuinely by
      the `t14_patches` arm, per pair, with the two caveats on record in
      ticket 14 (1-2 passes thin on 2 inliers; 2-8 rides on piece 8's wall
      rim). No regressions: all pairs that passed at 11/15 still pass.
- [ ] Juglet true-mate pass rate materially non-zero at ground truth, per
      pair, honest denominator 10. **RETRACTED 2026-09-30 (ticket 17):**
      the 0/10 was scored on corrupted data — pieces 3 and 9 carried
      pieces 2 and 8's surfaces byte-identically, so 4 of 9 breaklines
      were copies. Clean re-measurement: 0/5 on scorable touching pairs
      (1-2, 1-4, 1-8, 2-5, 6-7 all fail); 5 touching pairs unmeasurable
      (pieces 3/9 absent). Its 8 non-touching pairs
      are a material limit no extraction can pass. (Corrected 2026-09-29:
      the "no axis files" clause is withdrawn — all 9 Juglet axes were found
      in the archive and staged at `Dataset/Axes/Juglet/`, so the vote CAN
      fire there now; the run has not happened yet.)
- [ ] Per-pair failure reasons for the Juglet (wear / wall / unresolved).
      **Scorable five diagnosed 2026-09-30** (`diagnose_scorable5.py`, full
      breaklines at GT; closest-pair dots and trace-to-seam measured, not
      the 20mm-window figures which overstated):

      | pair | trace min_d | closest normals | trace-to-seam | reason |
      |---|---|---|---|---|
      | 1-2 | 21.9mm | −0.14 (unrelated) | 25.4 / 8.2mm | **coverage**: piece 1's loop misses this seam entirely |
      | 1-4 | 2.9mm | −0.52 opposed | 2.3 / 5.2mm | **wall**: curves near, faces opposed |
      | 1-8 | 13.5mm | −0.52 opposed | 25.8 / 8.6mm | **coverage** (+faces): piece 1's loop misses this seam |
      | 2-5 | 2.7mm | −0.21 opposed | 3.3 / 1.8mm | **wall**: nearest miss, faces opposed at closest approach |
      | 6-7 | 3.5mm | +0.55 weak agree | 2.4 / 6.3mm | **coverage**: same-wall-ish, piece 7's rim 6mm off the seam |

      Piece 1's loop spans nearly full sherd extent (maxR 24 vs mesh 27mm)
      yet sits 25mm from the 1-2 and 1-8 seams while passing 2.3mm from the
      1-4 seam: a full-size loop on the wrong feature for part of its
      length — the E1 "trace misses the seam" candidate, confirmed on this
      sherd. Not an interior ring (extent is full), not truncation.
      The five unmeasurable pairs (touching 3 or 9) stay **absent, not
      zero** — no reason can be given where no surface exists.
- [x] One claimed join staged correct-versus-attempt and witnessed
      (`juglet_sfs29`, closed as weak — confirms the 11.45mm figure, decides
      nothing else; framing lesson recorded).
- [ ] Handoff clause (probe passes / assembler finds nothing) not yet triggered.

**Needs-eye:** a `visual-qa` pair per true mate that now passes —
correct placement beside the machine's — staged via `visual-qa-helper`
and judged by the conservator. **This ticket cannot close on numbers
alone.** A witnessed look saying "the edges meet" is required, and if the
eye disagrees with the gate, the eye is right and the ticket stays open.

- [ ] Juglet true-mate pass rate at ground truth is materially non-zero,
      reported **per pair**, with the honest denominator stated (10
      joinable edges, not the 18 of the answer key — eight are not
      physical contacts)
- [ ] **Pot_A held at 15/15.** A Juglet improvement with a Pot_A
      regression is labelled Juglet-only, in this ticket and in the intent
      question
- [ ] For every true mate that still fails, the reason is recorded
      (wear, wall thickness, both, or unresolved) — "fixed" is not
      available until the probe says so
- [ ] At least one claimed join is staged correct-versus-attempt and
      witnessed
- [x] If the probe passes and the assembler still finds nothing, that is
      recorded as a finding and handed to `structure-from-sherds-pp` with
      the numbers attached — not treated as a failure here.
      **TRIGGERED 2026-10-01:** probe 15/15 in, assembly 0/8 + 0/15 out
      (job 31835065); handed over as assembly ticket 09 with log cites.

## The three claims this must keep separate

1. **The method failed on this material** — what the Juglet arm now
   supports, with the cause located in our own preprocessing.
2. **The measurement was broken** — already excluded: the answer key has
   residuals ~1e-14 mm, and the scorer was repaired in the assembly repo.
3. **The reference answer was wrong** — not the case; the ground truth is
   the conservator's own.

Do not let a partial improvement blur into any of the others.

## CORRECTION (2026-09-27) — the denominators, now measured rather than asserted

This ticket's own acceptance criteria already ask for the honest
denominator. It is now measured, by placing each pair at ground truth and
measuring the **real surface-to-surface gap with no breakline involved**
(`artifacts/juglet_run1/real_gap_at_truth.py`):

| | true pairs | pairs that genuinely touch | median gap | our score | honest denominator |
|---|---|---|---|---|---|
| **Juglet** | 18 | **10** | 0.34 mm | 0/18 | **0/10** |
| **Pot_A** | 15 | **15** | 0.06 mm | 7/15 | **7/15** |

Two consequences, and the second is the more important:

1. **The Juglet's honest denominator is 10, not 18** — confirmed. Eight pairs
   are separated by **3.5–19 mm of empty space** (1-5, 1-6, 3-7, 4-5, 4-6,
   5-9, 7-8, 8-9). No extraction can pass a 2 mm gate on them, because there
   is nothing there to trace. This is a property of an eroded surface.

2. **The "Pot_A held at 15/15" criterion above is WRONG and must be replaced.**
   Pot_A has never scored 15/15 on **our** output — the 15/15 was always the
   SfS++ authors' released sample. Our own fresh run scores **7/15**, and
   since all 15 of Pot_A's pairs genuinely touch (0.02–0.12 mm), **every one
   of those 8 losses is ours.** There is no material excuse available on
   Pot_A, which makes it the clean target: a pot where the gate is fair for
   every pair.

**Replace the Pot_A criterion with:** *our Pot_A score is reported per pair
against its 15 genuinely-touching pairs, and any change is judged on
movement in that number — not on a 15/15 that was never ours to hold.* A
change that improves the Juglet's 0/10 while leaving Pot_A's 7/15 flat is
progress; one that improves the Juglet while degrading Pot_A is a
regression, and must be labelled.

## Where the remaining Pot_A losses come from

Located, and it is not the ordering walk and not the face selection:

- Six of eight of our curves sit **2.99–3.77 mm off the authors'** for the
  same sherd, displaced **tangentially** (not along the surface normal, so
  not the other wall), same loop size and length, and the offset runs the
  whole way round. Against a 2 mm gate that fails every comparison it
  touches, and a pair survives only when two sherds' offsets partly cancel.
- Rendered and inspected: piece 1 (offset 0.69 mm) shows the two curves
  overdrawing around the entire rim — that is what agreement looks like.
  Piece 3 shows two distinct parallel curves 3.5–5.6 mm apart.
- The ordering walk is implicated on **one** sherd of eight (piece 2, 46% of
  the reference's traced length). It is not the main damage.

So the target is **what puts the rim ~3.5 mm to one side of the reference**,
consistently, on six of eight sherds. That is a concrete, well-localised
question and it is where the next effort belongs.

## RESOLVED (2026-09-27) — the 3.5 mm offset is NOT the cause, and the remaining failures are mostly not ours

The offset was traced, measured and then **intervention-tested**, and it does
not cost us the joins. Swapping each sherd's rim to the other surface brings
pieces 3–8 from 3.5–3.8 mm off the reference to **0.53–0.80 mm** with 99–100%
of points inside the 2 mm gate (baseline drift 0.00 mm on all eight, so the
arms are comparable). **The gate score went the other way: 7/15 → 6/15.** No
failing pair was recovered; the pairs that passed passed more comfortably, and
piece 1 — in six pairs — was made worse.

So the offset is real and is **not** on the causal path. Ticket 04 stays live
as a paper-compliance fix, not as a remedy. Two errors are recorded in it: I
tested the mesh's normal instead of the wall's, and I nearly reported a 5×
proxy improvement as a fix.

**With the curves now within 0.8 mm of the reference, the per-pair diagnosis
is:**

| failing pairs | cause | ours? |
|---|---|---|
| 1-3, 1-4, 1-5, 1-6, 1-7 | piece 1's rim faces **outward** while its neighbours' face inward; normals −0.96 to −1.00 | **no — geometry** |
| 2-5 | piece 2's rim truncated to 46% of the reference (ticket 01's walk defect) | yes |
| 2-4 | curves 8.8 mm apart though normals agree at 0.99 | yes |

**Six of the eight are piece 1, and they are not ours.** Established by
measurement, each alternative excluded:

- piece 1's breakline normals agree with its own mesh at **+0.996** — nothing
  inverted;
- the sherd is outward-facing (**86.8%** away from its own centroid);
- the normals are genuine **surface** normals, perpendicular to the rim
  (|n·tangent| = 0.012), so the traversal direction is not the explanation and
  **ticket 03's normal vote cannot recover these pairs**;
- at the ground truth **all eight** sherds are outward-facing, piece 1 most
  strongly (0.0% inward vs 16.7% median), so this is not a face-convention
  artefact;
- piece 1 is **not misplaced** — 21.9 mm from the mean of the other seven,
  well inside their 63–95 mm spread.

Piece 1 is the largest sherd (119 mm, 100 064 vertices) and the most exposed,
so its fracture surface faces out of the vessel while its neighbours' face
inward. **Pot_A's honest ceiling is ~12–13 of 15, not 15/15.**

## Witnessed look: `juglet_sfs29` — DONE 2026-09-27, and weak

The one case where the machine's **own** output was a false merge rather than
a missed one: sherds 2 and 9 at GT gap 0.02 mm, machine placement 11.45 mm
apart and 110° rotated. Staged in `visual-qa/`; note on
`viewer/annotations_manifest_juglet_sfs29.jsonl`.

**Conservator's judgement (verbatim):** *"i don't know what is to verify. it
is very obvious left is correctly fit and right is nowhere close."*

Two things follow.

**One. The look is closed, and it is weak evidence.** The eye confirms a figure
the numbers already gave and nobody would have doubted. It removes a residual
doubt about the 11.45 mm and nothing more. It is **not** evidence for the
offset, the face choice, piece 1's orientation, or the Pot_A score — those rest
on measurement and intervention.

**Two. My framing of the ask was bad, and the conservator said so.** I asked
them to judge whether "11.45 mm and 110° read correctly on screen". That asks
a conservator to *measure*, which is my job, and the answer was obvious
without measuring — so the look cost their time and returned nothing. **The
correct ask for a correct-vs-attempt look is a judgement of plausibility as a
conservator** — "do these two sherds look like they belong together on this
vessel?" — never a reading of a figure.

## Witnessed look: `pota_12` — DONE 2026-10-01, both parts answered;
POSTSCRIPT 2026-10-02 (ticket 18 spike): the "straight lines" are true
2-8 seam traces (0.07–0.13mm), not defects — the look showed one pair
while piece 2's rim legitimately contains other seams' traces. LESSON:
single-pair looks hide other-seam content and invite false defect
readings; future looks either show all of a sherd's seams or state which
seams are out of frame. The agent's append-inference is retracted.

**Conservator's judgement (verbatim):** *"they seem to go well together.
the red run on seam, most of the time, however there is gaps. also on the
blue sherd: there are straight lines run across the sherds, these are not
the seam"*

**Same-round reply (measured, 2026-10-01):**

1. *"Go well together"* — CONFIRMED by the eye. The thinnest pass is
   genuine at sherd level; the 15/15 stands, witnessed on its most fragile
   member. This is the verdict the look was staged for, and it is positive.
2. *"Red on seam most of the time, with gaps"* — consistent with the
   coverage data; no action.
3. *"Straight lines across the blue sherd"* — CONFIRMED REAL and NEW.
   Piece 2's `Breakline_0` seg 24-44 (21 pts, 38mm) lies on the mesh face
   (≤0.93mm) up to 15.9mm from the wall rim; segs 0-4/5-23 hug the rim
   (≤2mm). Not a staging artifact (per-segment tubes). Most likely
   ticket-14 appended decorative/patch content (piece 2 owns 4+
   `Decorative` files in the run tree) — attribution is ticket 18's spike.
   The gate is blind to this class (passes on the wall portion; extra
   segments only add opportunities on all-true-mate Pot_A). On non-mate
   material it is false-positive surface — filed as ticket 18
   (`18-face-crossing-traces-in-breakline-0.md`), which owns attribution,
   separation/labeling, re-measurement, and re-staging if red changes.

Single look (no fake comparison): Pot_A pieces 1+2 meshes at conservator
GT (piece 1 tan, piece 2 teal) with OUR Breakline_0 rims as red tubes
(resample19 = current pipeline truth). Desc
`visual-qa/viewer/pairs/pota_12_single.json`, staged clean (copied as-is,
109k faces; gate via shared `load_single_preview`: finite, mm-scale, all
three colors present). Builder:
`structure-from-sherds-pp/artifacts/juglet_run1/build_pota12_look.py`
(per-segment tubes — never streaking across segment jumps; first-header
skipped; sherds decimated separately THEN colored since stage decimation
drops vertex colors).

**The ask (plausibility, never measurement):** "do these two sherds look
like they belong together on this vessel — and does the red run on the
seam?" Tubes are 0.7mm markers, not evidence width. If the eye says no,
the 15/15 has a false member and ticket 07 reopens on pair 1-2; if yes,
the thinnest pass is witnessed genuine. Either way the note gets a
same-round agent reply (Needs-eye rule).

## Superseded 2026-10-01: the two stale owed looks (struck, not staged)

An explicit decision, not neglect — see chat 2026-10-01. The offset render
(ticket 10 requires it) would only confirm an exonerated figure, and the
piece-1 rim question below was settled when its six pairs recovered at
0.16–1.24mm. Staging either repeats the juglet_sfs29 framing error (asking
the eye to measure). The original reasoning is kept for the record:

## The look that would actually be worth having (2026-09-27; stale as posed)

## Note

The gate probe runs on the **laptop**, never inside the extracting job.
Scoring a re-extract from within the process that produced it is how a
broken input gets certified by its own producer.

The segment-boundary non-determinism (piece 1 differs between runs) is
**not** fixed here. It is a separate ticket, deliberately unbundled so
that the effect of 02-06 remains attributable.

## 2026-10-26 — revived as the vehicle for U19

*(Rewritten 2026-10-26: the code spans in this section were eaten when it was first appended
through a shell heredoc. No claim changed; the missing backticked words are restored.)*

This ticket had been idle since 2026-10-02 with its blocker cleared, and the conservator asked
for the Juglet end-to-end run. A verifier check found that **this ticket already is that run**,
so it is revived rather than duplicated, and it now answers
[U19](C:/PR/intent/U19-does-the-pipeline-put-the-juglet-back-together.md) as well as E1.

**Why a new run is not a repeat.** Both arms on record — ours (S1, 0 of 10 touching joins) and
the authors' untouched binary (S3, 0 of 18 gate probes, 2 of 9 seated on a pair that does not
touch) — were fed a bundle written **2026-09-25**, three days BEFORE the per-sherd interior
classifier landed (ticket 04, 2026-09-28) and before 05, 06, 14, 17, 271 and 287. In that
bundle `Breakline_0` was filled by slot, not by face, and was the interior face on only 3 of 9
sherds (1, 5, 9 — ticket 01's census: 43.8 % outer dots, 21.5 % inner, 34.7 % ambiguous). So no
Juglet number on record was produced by the code we have now. The old bundle itself is gone:
the 2026-10-24 attic sweep carved the three `Juglet_Dataset_*` trees out whole and deleted
their geometry, and only `SfS_pp/Ground Truth/` survives inside
`attic/checkout-bucketc-20261024-record.tar.gz`.

**The two decisions, taken by the conservator 2026-10-26.**

1. *Settle it like-for-like, then stage it for the eye.* Same answer key and the same honest
   denominator as S1/S3 — 10 touching joins of 18, plus the raw 18-join count — so the only
   thing that differs from the old arms is the preprocessing. Then the reassembly is staged in
   `visual-qa/` beside the conservator's hand reassembly for his verdict.
2. *Rebuild the preprocessing first, then assemble.* Re-derive surfaces, breaklines and axes
   from the nine meshes with today's code; do not reuse the old bundle. It is gone anyway, so
   any comparison with S3 is number against number and must be described that way.

**Two stages, and only the first is in this ticket's hands.**

- *Stage 1 (this ticket):* rebuild the bundle for the Juglet — surfaces, `Breakline_0` and axes
  for all nine pieces — from `Dataset/Juglet/Piece01..09.obj` with today's code, into a new
  bundle directory under the run root, and:
  - record an md5 per output and **prove no byte-identical copies between pieces** (the
    corruption that withdrew the old 0/10, ticket 17);
  - record every piece's interior/exterior decision, and **prove the `Breakline_0` the
    assembler reads is the one the interior vote chose** — it reads only `Breakline_0`, and
    `Breakline_1` appears nowhere in `class/` or the build (ticket 296);
  - **rebuild Pot A in the same batch** at the same settings; it must still reach 15/15, per
    pair, or the batch is void and says so. A rebuild that also loses Pot A proves nothing
    about the Juglet.
- *Stage 2 (its own ticket, opened when stage 1 delivers a bundle):* assemble the rebuilt
  Juglet against the conservator's poses, report each touching join as pass / fail /
  unmeasurable with rotation in degrees and translation in mm, stage the pair in
  `visual-qa/`, and take the eye verdict.

**Pieces 3 and 9 — what that record said, and what it is worth.** The 2026-09-30 run reported that
pieces 3 and 9 "produce no surfaces — single cluster after 30 loosened retries". That is a **dated
observation from that run, not a target and not a standing fact**: it predates the per-sherd interior
classifier (ticket 04) and tickets 05, 06, 14, 17, 271, 287, and the run before it had already given
those two pieces pieces 2 and 8's surfaces byte-identically (ticket 17), so neither record speaks for
them. Stage 1 (2026-10-27) tried them like any other piece with up to three bounded tolerance retries
and found something else again: **five of nine pieces produce no surface today** — 2, 3, 5, 8, 9 — and
the two named here fail for two different reasons (piece 3 splits into two clusters that the
appendix-A merge fuses; piece 9 produces zero clusters). See the 2026-10-27 section for the counts.
Decision 2026-10-26 stands: report the partial result with the unmeasurable pairs stated as
unmeasurable, and let a separate ticket own the clustering diagnosis. Nothing here may turn an absent
pair into a failed one.

## 2026-10-27 — Stage 1 delivered: a rebuilt bundle, and five sherds that do not segment

**Run of record.** `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0055_d8af9d2_p07-juglet-stage1`,
jobid **33834939**, commit `d8af9d288214b1a72bfba69f8fb99a4ecf09d071` (branch
07-end-to-end-acceptance), tag `p07-juglet-stage1`, node spartan-bm169, sacct final
**State=COMPLETED ExitCode=0:0 Elapsed=00:05:18**. Shipped defaults throughout; the only
`SFS_*` overrides are `SFS_AXIS_FILE` (the classify vote needs an axis, ticket 277) and
`SFS_SMOOTHNESS_DEG` on the bounded retries below. Instrument (submit.sbatch + three helper
scripts) lives in the run directory, not in the commit; its md5s are in `out/source.md5`.
Index row appended to `runs/index.tsv` with `verdict` and `human_note` left **empty**.

**Inputs actually used, and the one deviation from the brief.** The brief named
`Dataset/Juglet/Piece01.obj..Piece09.obj`. The pipeline derives the mesh name from the cloud's
stem (`mesh_processing_headless.cpp:2519-2522`: baseName = pcd stem minus `_Point`, then
`baseName + "_Mesh.obj"`), and the only clouds that exist for the Juglet are the **unpadded**
`Dataset/Point/Juglet/Juglet_Piece_1..9_Point.pcd` (ascii, mesh vertices + estimated normals;
24294 / 2565 / 3493 / 3651 / 6211 / 5126 / 8421 / 4479 / 2094 points), whose vertex counts match
`Dataset/Mesh/Juglet/Juglet_Piece_N_Mesh.obj` **exactly** and whose header records the scan pose
the `Juglet_GT` poses are in. So the run used that family. `Dataset/Juglet/Piece0N.obj` is the
same nine pieces re-exported (vertex counts differ by up to 3), carries no `_Mesh/_Point` pair,
and dropping it in would have meant renaming it. Both families' md5s are recorded in
`out/corpus_md5_before.tsv` so the choice is visible, not hidden.

**Axes were regenerated, and the old ones were never used as the classify axis.** No corpus axis
exists for the Juglet, the surfaces cannot be written before an axis exists (`:2190-2192` runs the
classify before `:2290` writes the PLYs), and the forbidden pre-classifier axes were not used. Pass
1 per piece therefore ran with a **PCA bootstrap axis** (`out/boot/`, written by
`boot_axis.py`) whose only job is to satisfy the axis gate; PotSAC (`sfs_axes`, today's python
port, seed 0, step 10) then ran over the two pass-1 walls to produce the real axis
(`out/axes/`), and pass 2 — the pass whose surfaces and breaklines are kept — used that axis.
Verified in code that this cannot bias the segmentation: the `SFS_AXIS_FILE` axis is read **only**
inside `classifyAndOrderPaper234` (`mesh_processing_headless.cpp:2004-2049`); clustering and the
appendix-A merge use per-cluster PCA axes (`pcaAxis234` :1805, `medianInternal234` :1917-1918,
`axes[]` :1961), so no axis file can change whether a piece segments.

### The nine pieces

| piece | surface | clusters (shipped 4.5 deg) | classify: face0 n / interior_frac, face1 n / interior_frac | decision | Breakline_0 dots |
|---|---|---|---|---|---|
| 1 | **PRODUCED** | 22 | 3489 / 0.0000, 626 / 0.0000 (satA 626, satB 3489) | swapped -> Surface_0=interior | 57 |
| 2 | absent | 0 | — | — | — |
| 3 | absent | 2 | — | — | — |
| 4 | **PRODUCED** | 2 | 242 / 0.0826, 51 / 0.9412 (satA 23, satB 270) | swapped -> Surface_0=interior | 15 |
| 5 | absent | 1 | — | — | — |
| 6 | **PRODUCED** | 2 | 365 / 0.0000, 213 / 0.0000 (satA 213, satB 365) | swapped -> Surface_0=interior | 31 |
| 7 | **PRODUCED** | 5 | 403 / 0.0000, 263 / 0.3878 (satA 161, satB 505) | swapped -> Surface_0=interior | 33 |
| 8 | absent | 2 | — | — | — |
| 9 | absent | 0 | — | — | — |

**Four of nine produce a surface — 1, 4, 6, 7. Five do not, and they fail in two different ways:**
- **Piece 2 and piece 9: zero clusters.** `Number of clusters is equal to 0`; the retry ladder
  then walks the smoothness threshold to about 44.5 deg and stops (21-22 `Single cluster found`
  lines — that message is printed for any `clusters < 2`, so it does not mean "exactly one").
- **Pieces 3, 5, 8: two clusters that the appendix-A merge fuses back to one.** Piece 3 logs
  `pass 1: merge 99 into 169`, piece 8 logs `merge 196 into 224`; both then log
  `pass 1 done: 1 clusters`, and the single-cluster branch (`:2316-2338`) writes no PLY at all.
  Piece 5 yields one cluster outright.
- **Bounded retries change nothing.** Three attempts per absent piece in fresh stage dirs —
  shipped 4.5 deg, then 3.5, then 3.0 (`SFS_SMOOTHNESS_DEG`) — give identical cluster counts
  every time. All 19 attempt rows with the setting tried and the counts obtained are in
  `out/juglet_attempts.tsv`; each attempt's log is `out/logs/<piece>.attempt-<tag>.log`.
- Even where it produces, the split is fragmentary: the two exported walls hold 3489 + 626 points
  out of 24294 input (14546 after the 0.6 fixed-radius downsample), 242 + 51 of 3651, 365 + 213 of
  5126, 403 + 263 of 8421. The cloud is mesh vertices, roughly 2-3 mm spacing before the downsample.
- **This is not the prior run's pattern and not the prior run's cause.** 2026-09-30 logged 7
  surfaces with 3 and 9 absent, under MATLAB-era axes and before tickets 271 and 287 (the current log
  shows the chain that now runs: `[SPLITTER-234] rule=PCL-REGION-GROWING ... paper=PAPER-CHAIN
  theta=3.40000`). Today: 1, 4, 6, 7 in; 2, 3, 5, 8, 9 out.

### Criterion 2 — the Breakline_0 the assembler reads is the one the interior vote chose

Code path, no inference: the axis-ray vote runs in `classifyAndOrderPaper234`
(`mesh_processing_headless.cpp:2004-2049`), printing `classify: face0 n=.. interior_frac=.. face1
n=.. interior_frac=.. satA=.. satB=..` (`:2038-2040`) and then either `classify: swapped ->
Surface_0=interior` (`:2045`, `pclusters[0]` and `[1]` exchanged) or `classify: kept ->
Surface_0=interior` (`:2047`). Slot 0 is then materialised as `cloudWithNormals_Cluster1`
(`:2249-2252`) and saved as `tmpSurfaceCluster_Improved_0.ply` (`:2290`), copied to
`<piece>_Surface_0.ply` and converted to `<piece>_Surface_0.xyz` (`:2601-2602`). The edge stage
takes `surfaceFile0 = fileNameOnly + "_Surface_0.xyz"` (`edgeline_extraction_headless.cpp:3701-3702`)
and calls `processFragmentData` on it (`:3718-3719`); inside, the output name is derived by
replacing `Surface_0` with `Breakline_0` (`:3517-3520`) and written (`:3531-3536`). So
**Breakline_0 is produced from Surface_0 and from nothing else**, and Surface_0 is the vote's
winner. The artefacts that record the decision per piece are `out/juglet_pieces.tsv`
(columns `classify`, `decision`) and `out/classify.tsv` for Pot A.

Two facts worth stating so the chain is not over-read:
- The exported surface files are **not** the cluster point counts:
  `improveSurfaceBoundaryByFittingBSplineSurface` rebuilds each boundary (`:2264-2271`), so piece
  1's 3489-point face is written as 3580 points and Pot A piece 01's 32775-point face as 66759. A
  count mismatch is expected, not evidence of a mix-up.
- An empirical ride check (median nearest-surface distance of Breakline_0) confirms the chain on 11 of
  the 12 produced pieces: Pot A 0.171-0.265 mm to Surface_0 against 3.196-5.000 mm to Surface_1, and
  Juglet piece 4 0.462 vs 0.875, piece 6 0.553 vs 2.297, piece 7 0.510 vs 6.337. The exception is
  **Juglet piece 1, 0.454 mm to Surface_0 against 0.415 mm to Surface_1 — inconclusive, not contrary**:
  its exported Surface_1 is a 12092-point filled patch that overlaps Surface_0 in space, so both
  distances are small. The code path above, not the ride number, is what establishes the claim.

### Criterion 3 — md5 of every output, and no copies between pieces

`out/files.md5` lists md5, path and byte size for all **48** files in the bundle. All 48 md5s are
distinct; within each class (`.S0.xyz`, `.S1.xyz`, `.Bl0.pcd`, `.Bl1.pcd`) 12 files give 12
distinct md5s, duplicates: none. Breakline_0, the file the ticket-17 corruption hit:

| piece | Breakline_0 md5 | bytes |
|---|---|---|
| Juglet_Piece_1 | `55face7956f1908c16d2c64fad0cd458` | 3775 |
| Juglet_Piece_4 | `4f5af7b036242678f1b111e406e5abfc` | 1234 |
| Juglet_Piece_6 | `fc1a2b0e0511a5fb26a37533d7a7c997` | 2360 |
| Juglet_Piece_7 | `713f3a422496c53125d47f8398616dcf` | 2440 |
| Pot_A_Piece_01 | `16e03c347b365bfb1b74f4d9f2494ba4` | 13546 |
| Pot_A_Piece_02 | `914331ab99f6b7887912dc10a3b5d885` | 10974 |
| Pot_A_Piece_03 | `1c7aab304545d257ab47b32e802f5259` | 10119 |
| Pot_A_Piece_04 | `b9520d1e5b587a5562e2008ef1b91995` | 9945 |
| Pot_A_Piece_05 | `285fa24e0eef98c721a8b09768c2d0d0` | 9546 |
| Pot_A_Piece_06 | `8ed66b5cdd6db5216f6a925d1659332c` | 10029 |
| Pot_A_Piece_07 | `9cc38ecb4f428241d8b7060aab4c81f8` | 4289 |
| Pot_A_Piece_08 | `8e77d6135660000a79f05101c6c620f6` | 4012 |

**Verdict: no two pieces' outputs are byte-identical, in any class.** Pieces 2, 3, 5, 8 and 9 have
no outputs at all (absent, not empty files), so nothing could be inherited this time.

### Criterion 4 — Pot A, same batch, same settings: 15 of 15

Eight pieces through exactly the p296 chain (frozen-corpus axis, shipped defaults,
`scripts/stage_piece.sh`). Classify: piece 01 **kept** (face0 32775 @ 0.9685, face1 27551 @ 0.0,
satA 59292, satB 1034), pieces 02-08 **swapped** (face0 frac 0.0000, face1 frac 1.0000), theta 3.4
on all eight — the same kept/swapped pattern as p296.

The bar is the assembler's own join test on `Breakline_0` at the reference poses
(`gate_probe_b0.py`, `_0`-only, gates 2.0 mm / 0.85 and 20 deg / 0.7, `simple_graph` 15 mates).
Measured on the rebuilt files: **15/15 strict passes**, per-pair inliers 1-2 32, 1-3 47, 1-4 34,
1-5 30, 1-6 16, 1-7 27, 2-4 6, 2-5 21, 2-8 18, 3-5 30, 3-6 11, 4-6 14, 4-7 13, 4-8 17, 6-7 22;
minimum inlier distance 0.28-1.06 mm. The weakest pair (2-4, 6 inliers) clears the gate, but note
ticket 14's caveat that 1-2 passes thin and 2-8 rides on piece 8's wall rim — the pair-level
inlier counts above are the evidence, the pass count alone is not. **The batch is not void.**

### Criterion 5 — the bundle

`/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0055_d8af9d2_p07-juglet-stage1/out/geom/`
— **kept in place, stage 2 consumes it**, as recorded in `run.json`. 48 files, 28 MB: per produced
piece `Juglet_Piece_N.S0.xyz` / `.S1.xyz` / `.Bl0.pcd` / `.Bl1.pcd`, and the same four for
`Pot_A_Piece_01..08`. Axes: `out/axes/Juglet_Piece_N_Axis.xyz` (PotSAC, 6 numbers per line,
position first) plus the bootstrap axes actually used for pass 1 in `out/boot/`. Record tables:
`out/juglet_pieces.tsv`, `out/juglet_attempts.tsv`, `out/classify.tsv`, `out/pieces_run.tsv`,
`out/files.md5`, `out/logs/` (one log per attempt and per final pass).

**Geometry deleted, with a counted record** (`out/GEOMETRY_DELETED.txt`): the 17 per-piece stage
trees under `stage/` held **888 files / 664,559,322 bytes** — xyz 329, pcd 221, ply 187, obj 31,
txt 65, other 55 — 638 MB, removed after the bundle was copied out; the run directory is now 47 MB.
The build tree was deleted by the job itself. The staged inputs were symlinks into the frozen
corpus, so no corpus geometry was copied or touched.

### Criterion 6 — the frozen corpus is unchanged

`out/corpus_md5_before.tsv` and `out/corpus_md5_after.tsv` hash **85 files** before and after the
job: nine Juglet clouds, both mesh families, the old Juglet axis family,
`Dataset/Juglet/Piece0N.obj`, and for Pot A the eight pieces' `Point/`, `Mesh/`, `Axes/`,
`Surfaces_0/1` and `Breaklines_0/1`. `out/corpus_verdict.txt`: `[RUN] corpus md5 UNCHANGED (85 files)`.
Nothing under `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp` was written.

### What this leaves stage 2

Of the ten touching joins, **two are scorable from this bundle: 1-4 and 6-7**. 1-2, 1-8 and 2-5
become unmeasurable because pieces 2, 5 and 8 have no surface, and the five non-touching pairs stay
out of the denominator for the material reason already on record. That is a thinner denominator than
the 5-scorable shape the 2026-10-26 decision assumed, and it is a result about the input clouds as
much as about the method: five sherds of 2565-6211 vertices do not split into two walls under the
current chain even with the tolerance loosened.

**Not done in this ticket, by design:** no assembly, no scoring against the reference poses, no
visual-qa staging. That is stage 2.
