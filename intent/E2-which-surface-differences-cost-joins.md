# E2 — Which differences in our extracted surfaces cost SfS++ joins?

**Status:** open · **Blocked by:** none · **Effort:** controlled Pot E surface tests following the axis-input diagnostics

## Where it stands

On Pot E, sherds 27 and 28 seat together with the authors’ axis set even when it uses our axis file for sherd 27. With our axis set they miss their join. The authors’ file for sherd 27 alone did not restore it. The best complete author-background swap seats 62 of 62 joins, with sherd 28 turned 4.34° from its reference orientation relative to sherd 27. The usable reciprocal swap puts it nearly half a turn out. Both wall samples largely cover the same surfaces in the native scan frame, with at least 99.3% of samples within 1 mm of the corresponding wall. The source of the join loss remains open.

Weight: One pot, four axis sets, two attempted repeats each in Surface Parity 01. Seven outputs are complete. A reciprocal run with three missing sherd poses is excluded. Axis-parity Ticket 19 separately shows that swapping only sherd 28 into the authors’ set also passes twice.

Next: [Surface Parity 04](../.scratch/surface-parity/issues/04-test-wall-normals-at-fixed-points.md) swaps wall normals while holding sample positions and order fixed. Coverage and sampling remain separate tests. Carry a useful change in axis candidates to assembly for confirmation.

Picture: SfSpp_preprocessing/artifacts/surface-parity-01/evidence/renders/AUTHOR_E27_OWN_1_27-28.png | Pot E sherds 27 and 28 with our sherd 27 axis in the authors’ axis set.

## Why it matters

We need a surface extraction recipe for our own scans that can match the authors’ sample-input result. Knowing which difference changes a join will tell us which part of extraction is worth changing and provide a test for whether the change works.

## Done when

- [ ] Localise a repeatable Pot E join loss to an identified sherd or bounded combination of sherds using reciprocal axis-file controls and the unchanged assembler.
- [ ] Establish whether changing retained surface area, sampling density, or normals individually changes the relevant axis and recovers the join. Report signed axis direction in degrees, the distance to a named point in millimetres, the candidate fracture stretches, and the number of joins recovered out of 62. A null or mixed result must show which hypotheses were tested and where they remain coupled.
- [ ] Show the changed surface on two locked views with a 20 mm scale bar and the resulting placement against the reference. Validate any proposed extraction change against the released Pot E sample and existing comparison pots before making it the default.

## Gate / stop condition

Start with 27–28. If the archived full-set contrast cannot be reproduced, stop attributing the loss to individual sherds. Keep localisation separate from surface diagnosis. If a controlled change affects the axes but its effect in the full assembly remains ambiguous, use the matching trace to choose a bounded sherd comparison. A surface difference earns a repair trial only when a controlled change carries through to a scored join.

## Source

[E1](E1-do-our-breaklines-let-sfs-find-joins.md), [axis-parity Ticket 18](../.scratch/axis-parity/issues/18-trace-first-e28-join-loss.md), and the frozen Ticket 19 run `20261124-0443_21446b8_t19-decisions`. The conservator asked to open this question on 2026-11-24.
