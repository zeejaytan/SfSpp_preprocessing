# 17: Diagnose the Pot H collapse (1/11)

**What to build:** a diagnosis, not a fix — one focused ticket answering why the frozen finder collapses wholesale on Pot H when it direction-passes 75% everywhere else.

**Answers:** E1

**Blocked by:** 10-axle-generalise (frozen cross-pot evidence below).

**Status:** results-in

**Starting position (from 10, jobs 33106488–33106709):** Pot H 1/11 — only H10 direction-passes (3.03°, position 21.97 over). H01/H03/H04 return nset=0 (finder finds nothing); the rest return 1–2 modes against 2–6 shipped axes, all direction-failed (13–85° off). Point counts 276–2119 throughout — small fragments, multi-axis everywhere. Frozen finder: `.scratch/pota-repro/p15-stage/axle_finder/` (committed). Compare with the passing small pieces that DO work (e.g. G pot 7/7, D01–D16) and with the D17–D32/J tails (same small-multi signature, partial passes) to isolate what makes H wholesale rather than partial.

**Hypotheses, in evidence order:**
1. **Below the span floor** — H fragments are smaller than anything in the fit set (V3b: ball patches catastrophic, thin slabs fail); check shape-span per H piece vs the passing smalls, and whether any H piece spans enough 2D shape to be identifiable at all (admission-test question).
2. **Multi-axis dilution** — 2–6 true modes split the vote below the minfrac/dedup floors (peel stops, modes killed by x1.1); check per-piece vote counts, peel traces, dedup kills vs shipped counts.
3. **Fragment-type difference** — H pieces are a different kind (base-heavy? trim? scrap?) whose geometry the wall-tuned vote cannot see; check surface classification + curvature profile vs wall pieces.

**Rules:** diagnose and propose — do not modify `p15-stage/axle_finder/` (experiment copies on Spartan only). One hypothesis at a time, each with the measurement that kills or keeps it. If H1 (span floor) survives, the deliverable includes the admission-test proposal (which fragments the finder should refuse, with thresholds) rather than a fix.

- [ ] Verdict: which hypothesis survives, with numbers (spans, counts, peel traces, curvature profiles)
- [ ] Fix or admission-test proposal: exact change/thresholds + re-validation protocol for the follow-up ticket
- [ ] Job IDs + sacct states; no commits; Comments-only ticket edits

## Comments (worker, 2026-10-16)

**Verdict: H1-raw is KILLED; H1-per-mode + H2 + H3 all survive as one combined
mechanism.** Pot H is not "smaller than the fit set" — H01 alone has 25,324
points (16,002 + 9,322 per surface) and a 158mm bbox, dwarfing passing G07
(3,019 pts, 37mm bbox, 7/7 G pot passes). What makes H wholesale instead of
partial is a stack of three individually-proven effects below. Finder
 untouched throughout (`.scratch/pota-repro/p15-stage/axle_finder/` never
modified; all probes are read-only scripts in Spartan `potsac-p17-run/`,
mirrored at laptop `.scratch/pota-repro/p17-stage/`).

**H1 (span floor): KILLED in raw form, SURVIVES per-mode.** Counts/bboxes meet
or exceed passing smalls on every H piece (smallest H11: 4,539 pts >
G07's 3,019). Split never shatters anything (`af_split` eps10/minpts300:
ncomp=1, kept=1.00 on all 69 pieces measured). But per-AXIS support is below
any identifiability floor: tight-inlier share of held truth (`|R|<=1`,
`af_inliers`) is 0.06–0.17 on ALL 11 H pieces and ALL 25 shipped axes, vs
0.34–0.55 on passing controls (G06 0.524, G07 0.503, D27-ax1 0.546, A07
0.34–0.39) and 0.15–0.22 on failing D30. Example: H09-ax1 is a 4mm-wide
radial band (rad 55–59mm) × 51mm long — a narrow strip, not a patch. The
absolute GM-cost level agrees: vote-best cost 1.6–1.85/pt on H and ~1.6 on
D30-fail, vs 0.9–1.2 on every passing control (G06 0.94, G07 0.98, D27 0.9,
A07 1.2). H clouds are uniformly "unlikely" under the axis model.

**H2 (vote dilution): SURVIVES for all multi-axis pieces + sets the nset=0
gate.** No vote poverty — the 6000-vote always reaches cost-par with truth
(~2% margin), and refine-from-shipped HOLDS on most axes (H03 0.04°/0.08mm,
H04 0.02°/1.60mm, H05 both ≤2.5°/≤1.5mm, H09 5/6 axes ≤6.4°). The killer is
the floors, not the search: (a) truth support 0.066–0.095 on H01/H03/H04 sits
BELOW the peel minfrac 0.10 — even an oracle proposing truth is rejected,
round-1 winners 0.060–0.090 < 0.10 → STOP → nset=0; (b) on H05–H09/H11 peel
passes minfrac at 0.10–0.17 shares but the landscape is flat (vote-best ≈
truth cost), winners are spurious, and the x1.1 dedup kills the rest —
H05 3 kept rounds → nset=1 (nans=2), H09 3 rounds → nset=2 (nans=6),
H11 2 rounds → nset=1 (nans=3); (c) H02: spurious winner out-supports truth
(0.115 vs 0.098) → returned 85°/427mm off. H10, the lone pass, proves the
knife-edge: truth support 0.108, winner 0.108, clears 0.10 by 0.008.

**H3 (fragment type): SURVIVES for H01–H04 — they are base-type, not wall.**
Angle(mean surface normal, shipped axis): H01 4.5°/15.2°, H02 12.6°/24.5°,
H03 2.3°/16.7°, H04 10.1°/8.0° — normals face ALONG the axis (base-cap
geometry; fragments touch the axis: radial min 0.2–11.6mm), vs 31–74° on
passing wall controls (G06 48–51°, G07 31–50°, D27-ax1 72–74°, A07 19–59°).
Planarity agrees (H01–H06 ≤0.020, thinnest of the 69-piece survey). The
wall-assuming chain (GM vote + tight-inlier peel + 10% floor) cannot see
axis-facing plates: many near-equivalent axes fit, GM saturates, LM goes
singular (657 singular-Jacobian warnings on H's 11 pieces vs ~6–10/piece on
every other pot — symptom, not cause). Multi-axis H pieces are mixed:
H06-ax1 (80°) and H09-ax1 (89.9°) ARE wall-like, but own only ~12–14% support
each → back to H1-per-mode + H2.

**Piece-level assignment:** H01/H03/H04 nset=0 = H3 (base-type) + sub-minfrac
truth (H1-floor); H02 = H3 + spurious-winner; H05–H09/H11 = H2 dilution +
H1-per-mode (+partial H3); H10 pass = same family, luck (0.108 clears 0.10).

**Admission-test proposal (no fix — the finder should refuse, finder-observable
only, no shipped key):** refuse/flag a fragment when BOTH (1) vote-best GM
cost > 1.4/pt (H 1.6–1.85, D30-fail ~1.6; all passing ≤1.2) AND (2) round-1
peel-winner share < 0.20 (H 0.06–0.17, D30 0.22, A07-fail 0.39; all passing
≥0.39). Both come from the finder's own round-1 vote+peel. Thresholds to be
confirmed on the full B–J distribution (esp. J tails) by the follow-up.
**Re-validation protocol (follow-up ticket):** implement the gate in a
Spartan-side experiment copy; run all B–J pieces; require refusal of ≥9/11 H
plus the D30/J-tail fails with ZERO refusals among current dirpass pieces
(especially G07, D32, small-J passes) — report the confusion matrix; only then
the E2E gate proof. Suggested extra: render H01–H04 meshes (base-cap check
for the conservator's eye) before closing H3 — geometry claim, needs a look
per workspace rules.

**Probe bug, caught and rerun (honest record):** v1 peel/span misread Axes
files as [dir;pos] — they are [pos;dir] per `score_vs_shipped.m:3`. This made
v1 "shipped ranks 6001/6000 with saturated cost" on ALL pieces incl. passing
G07 — impossible, which is what caught it. V1 winner/dedup traces were
key-independent and stand; all shipped-relative numbers above are v2 (fixed
convention, same-point-set cost/pt comparisons; the cross-set vote-rank column
was dropped as invalid by construction).

**Jobs (all COMPLETED 0:0, `sacct` direct — `slurm_poll.sh` exits
immediately):** 33107484 (span v1, superseded — radial convention bug);
33107810 (peel v1, superseded — same bug, winner traces valid); 33108716
(span v2, 00:01:16); 33108743 (peel v2, 00:03:43); 33109148 (type probe,
00:01:32). Ticket-10 reference jobs 33106488–33106709 (prior worker). No
commits; Comments-only edit. Staging: laptop
`.scratch/pota-repro/p17-stage/` (`p17_span/peel/type.m` + 3 sbatches)
mirrors Spartan `potsac-p17-run/`.
