# 10: What puts our rim ~3.5 mm to one side of the reference?

**Answers:** E1

**Blocked by:** nothing — this is now the front of the queue

**Status:** ready-for-agent

**Needs-eye:** **required before this ticket can close.** The offset is a
geometry claim and the render already exists
(`structure-from-sherds-pp/artifacts/piece3_render/`). Stage it in
`visual-qa/` as a single look and get the conservator's eye on it. A pass
rate cannot close this.

## The finding this ticket exists to explain

Ticket 09 measured our preprocessing for the first time. On Pot_A, where
all 15 true pairs genuinely touch (0.02–0.12 mm at ground truth), we score
**7/15**. Comparing our breakline with the **authors' breakline for the
same sherd in the same frame** localises the damage:

| piece | our→authors (median) | within 2 mm | length vs theirs | radius vs theirs |
|---|---|---|---|---|
| 1 | **0.69 mm** | **100%** | 0.98 | 0.996 |
| 2 | 2.82 mm | 30% | **0.46** | 0.406 |
| 3 | 3.49 mm | 0% | 1.02 | 1.029 |
| 4 | 3.59 mm | 0% | 1.00 | 1.032 |
| 5 | 3.61 mm | 0% | 1.05 | 1.032 |
| 6 | 2.99 mm | 0.8% | 1.02 | 1.031 |
| 7 | 3.77 mm | 0% | 1.06 | 1.051 |
| 8 | 3.52 mm | 0% | 1.09 | 1.076 |

Six of eight sit **2.99–3.77 mm off** — a near-constant displacement, same
loop size, same length, running the whole way round. Against a 2 mm gate
that fails every comparison it touches, and a pair survives only when two
sherds' offsets happen to cancel. That is why 7 pairs pass and 8 do not:
not because some sherds are good, but because some errors cancel.

## What has already been refuted, so it is not re-tried

- **Not the other wall face.** The offset direction versus the local surface
  normal: |cos| median **0.255**, 59.5% of offsets tangential, only 11.5%
  normal-aligned. A wall offset would be normal-aligned. Ticket 04 is
  therefore *not* the fix for Pot_A.
- **Not displaced inward.** Radius ratio 1.029 and area ratio 1.054 against
  the reference — the same size, very slightly *outward*. (E1's flagged
  "traced loop sitting radially inside its own surface's extent" is the
  opposite of what we measure.)
- **Not an over-permissive boundary detector.** Rendered and inspected:
  piece 1's sherd has obvious interior ring features and our curve walks
  past all of them to the true outer edge; piece 3's offset is a clean
  parallel displacement, not a loop hopping between features.
- **Not the ordering walk, except on one sherd.** Piece 2 has 46% of the
  reference's traced length, which is the truncation measured in ticket 01.
  The other seven are not truncated. Ticket 03 is demoted accordingly.
- **Not a frame or units problem.** The fresh output sits 0.7–2.5 mm from
  the Pot_A mesh centroids on 6 of 8, the frame the authors' data occupies.

## The candidates that remain, and how to tell them apart

The offset is tangential, consistent, and roughly constant in magnitude.
That is consistent with a **systematic geometric bias in where the boundary
detector places the rim**, and the code has candidates:

1. **The boundary detector's parameters.** `setRadiusSearch(4)` and
   `setAngleThreshold(M_PI * 0.6)` = 108°, flagged in E1 as "very
   permissive". A radius search of 4 mm is the same order as the offset
   itself. *Test:* re-extract one sherd at radius 1, 2 and 4 mm and see
   whether the offset moves with it. **If it does, this is the cause and the
   fix is a parameter.** If the offset is invariant to the radius, it is
   not.
2. **The smoothing/resampling applied before detection.** If the surface is
   smoothed or resampled inward before the boundary is taken, the rim would
   sit consistently inside the true edge by roughly the smoothing
   displacement. *Test:* measure our rim's distance to the raw mesh (0.169 mm
   — it lies on the sherd) and to a *smoothed* version of it. If the
   smoothed surface is ~3.5 mm inside the raw one, that is the mechanism.
3. **A units or scale convention in the surface stage** that shifts the rim
   consistently. *Test:* the offset should then scale with the pot, so
   compare pieces of very different size (pieces 7 and 8 are ~25 mm across,
   piece 1 is ~63 mm). **If the offset is the same 3.5 mm on both, it is not
   a scale error.**

Test 1 and test 3 are cheap and can be run before any code changes. **Do
test 3 first** — it is arithmetic on data already on disk, and it would
eliminate a whole class of explanations for nothing.

## Acceptance criteria

- [ ] The offset is explained by one of the three candidates above, with the
      discriminating measurement quoted — or a fourth is found and recorded
- [ ] At least one prediction is tested that could have come out otherwise
      (radius sweep, size dependence), not only measurements that agree
- [ ] The witnessed render of the offset is staged in `visual-qa/` and the
      conservator's note recorded
- [ ] `scripts/diagnostics/` or the assembly repo's `artifacts/juglet_run1/`
      holds the script that produced each number above, runnable
- [ ] The per-pair Pot_A score is re-measured after any change, against all
      15 touching pairs, and reported as movement in 7/15 — not against a
      15/15 that was never ours

## Note

This ticket supersedes the ordering of 02–06. Those describe real
paper-vs-code gaps and remain worth doing on their own merits, but none of
them is the cause of the 8 lost Pot_A joins, and doing them first would be
six tickets of work that cannot move the number this question is about.
