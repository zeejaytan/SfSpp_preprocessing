# E2 — Which differences in our extracted surfaces cost SfS++ joins?

**Status:** open · **Blocked by:** none · **Effort:** controlled Pot E surface tests following the axis-input diagnostics

## Where it stands

On Pot E, sherds 27 and 28 seat together with the authors’ axis set even when it uses our axis file for sherd 27. With our axis set they miss their join. The authors’ file for sherd 27 alone did not restore it. The best complete author-background swap seats 62 of 62 joins, with sherd 28 turned 4.34° from its reference orientation relative to sherd 27. The usable reciprocal swap puts it nearly half a turn out. Both wall samples largely cover the same surfaces in the native scan frame, with at least 99.3% of samples within 1 mm of the corresponding wall.

Swapping only wall normals at fixed sample points moves the estimated axes toward the donor on both sherds in both directions ([Surface Parity 04](../.scratch/surface-parity/issues/04-test-wall-normals-at-fixed-points.md)). On sherd 27, giving our points the authors’ normals moves our best candidate (rank 2) from 7.35° / 5.9 mm to 4.81° / 3.6 mm from the reference axis, and reverses the shift in reverse (authors’ rank 2 moves from 2.87° / 2.0 mm to 6.61° / 4.9 mm). On sherd 28, our single candidate moves from 11.28° / 69.9 mm to 4.99° / 31.2 mm with the authors’ normals, while authors’ rank 1 moves from 10.93° / 68.7 mm to 17.45° / 105.8 mm and rank 2 from 3.60° / 22.0 mm to 4.92° / 31.4 mm with ours. Candidate counts (`k`) stayed tied to the point coordinates rather than the normals.

Isolating duplicates, stride, coverage, and spatial sampling at untouched normals ([Surface Parity 05](../.scratch/surface-parity/issues/05-test-sampling-and-coverage-at-fixed-normals.md)) points directly to duplicate wall points. Our extracted `.S0`/`.S1` wall files carry ~47% exact duplicate XYZ rows (E27: 8,567 of 18,137; E28: 7,260 of 15,539), whereas the authors’ files have zero. Removing exact duplicate XYZ rows alone (`OWN_DEDUP`, still at stride 10 and untouched normals) restores sherd 28’s missing second candidate (`k=1 → 2`, best axis moving from 11.28° / 69.9 mm to 4.03° / 25.6 mm, near the authors’ 3.60° / 22.0 mm) and improves sherd 27 (`k=3 → 2`, best axis moving from 7.35° / 5.9 mm to 3.86° / 2.9 mm, near the authors’ 2.87° / 2.0 mm). Forcing stride 1 (`OWN_STRIDE1`) or 1 mm coverage filtering (`OWN_SHARED_1MM`) while duplicates remain leaves sherd 28 stuck at `k=1` (11.28°–11.37°). Common 1 mm voxel sampling produces matching candidate counts on both sides (`3/3` on E27, `2/2` on E28). Caveat: dropping 1 point on the authors’ sherd 28 wall (`AUTHOR_SHARED_1MM`, 4,480 → 4,479 points) dropped `k=2 → 1`, showing threshold sensitivity near `keep_lines`. Whether deduplicating our wall files recovers the lost Pot E joins in assembly is not yet tested.

Weight: One pot; four axis sets with two attempted repeats each in Surface Parity 01 (seven complete, one excluded for missing poses; Axis-parity Ticket 19 also passed twice swapping only sherd 28 into the authors’ set); two sherds across 12 arms in Surface Parity 04 (99.3–100% of target normals transferred, 4/4 archive & sham byte-identical); and two sherds across 10 arms each (20 runs) in Surface Parity 05 (4/4 archive byte-identical, 8/8 fixtures PASS, job `35624709`).

Next: Carry deduplicated OWN wall axes (`OWN_DEDUP` across Pot E sherds) into the unchanged Ticket 19 assembler to test whether deduplication actually recovers the 3 lost Pot E joins (out of 62), and inspect why `MeshPreprocessingHeadless` writes ~47% duplicate XYZ rows.

Picture: SfSpp_preprocessing/artifacts/surface-parity-05/evidence/renders/Pot_E_Piece_28.png | Pot E sherd 28 sampling and common-voxel axis comparison (20 mm bar).

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
