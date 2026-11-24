# E2 — Which differences in our extracted surfaces cost SfS++ joins?

**Status:** open · **Blocked by:** none · **Effort:** one Pot E diagnostic, then a controlled surface test if it isolates a sherd

## Where it stands

On Pot E, the same axis estimator and assembler seat all 62 reference joins when the axes are estimated from the authors’ surfaces. With axes estimated from our surfaces, 59 joins seat and 13–28, 27–28 and 28–31 are lost. The breaklines and other assembly geometry are fixed. This identifies sensitivity to the surface input. The responsible feature of that input is unknown.

Weight: One pot, two repeats per condition in axis-parity Ticket 19. Our E28 file can seat all 62 joins in the author-surface axis set.

Next: [Surface parity 01](../.scratch/surface-parity/issues/01-isolate-e27-surface-axis-effect.md) compares both walls on E27 and E28 and tests whether a single E27 axis-file swap changes 27–28.

## Why it matters

We need a surface extraction recipe for our own scans that can match the authors’ sample-input result. Knowing which difference changes a join will tell us which part of extraction is worth changing and provide a test for whether the change works.

## Done when

- [ ] Localise a repeatable Pot E join loss to an identified sherd or bounded combination of sherds using reciprocal axis-file controls and the unchanged assembler.
- [ ] Establish whether changing retained surface area, sampling density, or normals individually changes the relevant axis and recovers the join. Report signed axis direction in degrees, the distance to a named point in millimetres, the candidate fracture stretches, and the number of joins recovered out of 62. A null or mixed result must show which hypotheses were tested and where they remain coupled.
- [ ] Show the changed surface on two locked views with a 20 mm scale bar and the resulting placement against the reference. Validate any proposed extraction change against the released Pot E sample and existing comparison pots before making it the default.

## Gate / stop condition

Start with 27–28. If the archived full-set contrast cannot be reproduced, stop attributing the loss to individual sherds. If E27 alone does not isolate the join, retain the surface measurements and use the trace to choose a bounded pair or assembly context before changing the extraction recipe. A surface difference earns a repair trial only when a controlled change carries through to a scored join.

## Source

[E1](E1-do-our-breaklines-let-sfs-find-joins.md), [axis-parity Ticket 18](../.scratch/axis-parity/issues/18-trace-first-e28-join-loss.md), and the frozen Ticket 19 run `20261124-0443_21446b8_t19-decisions`. The conservator asked to open this question on 2026-11-24.
