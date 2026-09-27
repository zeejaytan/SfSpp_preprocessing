# 07: End-to-end acceptance — does the Juglet now join, and is Pot_A unharmed

**What to build:** the falsifiable end state. A regenerated Juglet bundle
whose true mates pass the assembler's own join test at correct placement,
with the working sample unchanged — and a witnessed render, because a
passing number is not something to believe on its own.

**Answers:** E1

**Blocked by:** 06 (and therefore 01-05)

**Status:** ready-for-agent

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

## Note

The gate probe runs on the **laptop**, never inside the extracting job.
Scoring a re-extract from within the process that produced it is how a
broken input gets certified by its own producer.

The segment-boundary non-determinism (piece 1 differs between runs) is
**not** fixed here. It is a separate ticket, deliberately unbundled so
that the effect of 02-06 remains attributable.
