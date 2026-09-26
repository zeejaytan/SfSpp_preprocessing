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

## Note

The gate probe runs on the **laptop**, never inside the extracting job.
Scoring a re-extract from within the process that produced it is how a
broken input gets certified by its own producer.

The segment-boundary non-determinism (piece 1 differs between runs) is
**not** fixed here. It is a separate ticket, deliberately unbundled so
that the effect of 02-06 remains attributable.
