# E2 — Which differences in our extracted surfaces cost SfS++ joins?

**Status:** open · **Blocked by:** none · **Effort:** controlled Pot E surface tests following the axis-input diagnostics

## Where it stands

On Pot E, sherds 27 and 28 seat together with the authors’ axis set even when it uses our axis file for sherd 27. With our axis set they miss their join. The authors’ file for sherd 27 alone did not restore it. The best complete author-background swap seats 62 of 62 joins, with sherd 28 turned 4.34° from its reference orientation relative to sherd 27. The usable reciprocal swap puts it nearly half a turn out. Both wall samples largely cover the same surfaces in the native scan frame, with at least 99.3% of samples within 1 mm of the corresponding wall.

Swapping only wall normals at fixed sample points moves the estimated axes toward the donor on both sherds in both directions ([Surface Parity 04](../.scratch/surface-parity/issues/04-test-wall-normals-at-fixed-points.md)). On sherd 27, giving our points the authors’ normals moves our best candidate (rank 2) from 7.35° / 5.9 mm to 4.81° / 3.6 mm from the reference axis, and reverses the shift in reverse (authors’ rank 2 moves from 2.87° / 2.0 mm to 6.61° / 4.9 mm). On sherd 28, our single candidate moves from 11.28° / 69.9 mm to 4.99° / 31.2 mm with the authors’ normals, while authors’ rank 1 moves from 10.93° / 68.7 mm to 17.45° / 105.8 mm and rank 2 from 3.60° / 22.0 mm to 4.92° / 31.4 mm with ours. Candidate counts (`k`) stayed tied to the point coordinates rather than the normals (sherd 27: 3 on our points, 2 on theirs; sherd 28: 1 on our points, 2 on theirs), so sampling or coverage still governs how many candidates survive, and whether these normal-shifted axes recover the 27–28 join in assembly is not yet tested.

Weight: One pot; four axis sets with two attempted repeats each in Surface Parity 01 (seven complete, one excluded for missing poses; Axis-parity Ticket 19 also passed twice swapping only sherd 28 into the authors’ set); and two sherds across 12 extraction arms in Surface Parity 04 (99.3–100% of target normals transferred, all 4 native archive checks and all 4 sham controls byte-identical).

Next: Either carry the normal-transferred axes (and/or the deferred E27+E28 axis pair in [Ticket 02](../.scratch/surface-parity/issues/02-test-the-e27-e28-axis-pair.md)) into the unchanged assembler to test whether the axis shift recovers join 27–28, or isolate point sampling and coverage at fixed normals to explain why sherd 28 yields 1 candidate on our points vs 2 on the authors’.

Picture: SfSpp_preprocessing/artifacts/surface-parity-04/evidence/r4/renders/Pot_E_Piece_27.png | Pot E sherd 27 wall normals swapped at fixed points (native blue vs transferred orange arrows; native solid vs transferred dashed axes).

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
