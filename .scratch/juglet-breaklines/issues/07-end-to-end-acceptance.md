# 07: End-to-end acceptance — does the Juglet now join, and is Pot_A unharmed

**What to build:** the falsifiable end state. A regenerated Juglet bundle
whose true mates pass the assembler's own join test at correct placement,
with the working sample unchanged — and a witnessed render, because a
passing number is not something to believe on its own.

**Answers:** E1

**Blocked by:** 06 (and therefore 01-05)

**Status:** in-progress — Pot_A half done by our own output (15/15,
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
- [ ] If the probe passes and the assembler still finds nothing, that is
      recorded as a finding and handed to `structure-from-sherds-pp` with
      the numbers attached — not treated as a failure here

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

## The look that would actually be worth having

A **single** look of piece 1's breakline on its own sherd with its
neighbours' breaklines at ground truth, so the conservator can judge whether
piece 1's rim sits where the rim of that sherd should. That is the one
genuinely open geometric question left: the curve is 0.69 mm from the
reference — our best — correctly oriented for its own surface, yet it opposes
every other sherd's rim at −0.96 to −1.00, accounting for six of the eight
remaining failures. Whether a conservator reads that as a rim in the right
place on an awkwardly-shaped sherd, or as a rim on the wrong part of it, is
not something the numbers settled. **That** is a judgement only the eye can
make, and unlike the pair above, the answer is not obvious.

## Note

The gate probe runs on the **laptop**, never inside the extracting job.
Scoring a re-extract from within the process that produced it is how a
broken input gets certified by its own producer.

The segment-boundary non-determinism (piece 1 differs between runs) is
**not** fixed here. It is a separate ticket, deliberately unbundled so
that the effect of 02-06 remains attributable.
