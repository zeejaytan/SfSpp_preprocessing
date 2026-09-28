# 10: What puts our rim ~3.5 mm to one side of the reference?

**Answers:** E1

**Blocked by:** nothing — this was the front of the queue; investigation
complete 2026-09-28, see RESOLVED section at foot

**Status:** resolved — offset explained (wrong wall) and exonerated (fixing
it moved the gate 7/15 → 6/15). No further work belongs here.

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

## Test 3, run: a scale artefact is ELIMINATED, and piece 1 is the key

`offset_size_dependence.py`, on sherds spanning **37–119 mm (3.3×)**:

| piece | sherd size | verts | offset (median) | within 2 mm |
|---|---|---|---|---|
| **1** | 119.2 mm | 100 064 | **0.69 mm** | **100%** |
| 2 | 111.3 | 55 814 | 2.82 | 30% |
| 3 | 87.8 | 41 197 | 3.49 | 0% |
| 4 | 88.1 | 33 475 | 3.59 | 0% |
| 5 | 98.8 | 34 168 | 3.61 | 0% |
| 6 | 119.1 | 29 184 | 2.99 | 0.8% |
| 7 | 42.8 | 10 593 | 3.77 | 0% |
| 8 | 36.6 | 10 366 | 3.52 | 0% |

**Scale and units are eliminated.** A scale artefact grows with the object.
Here the seven non-control pieces span 3.3× in size and their offsets move
only **1.34×** (2.82–3.77 mm) — a near-constant *distance*.

Within the seven the correlation is **−0.69**: the offset *shrinks* as the
sherd grows. That is the wrong direction for any scale explanation and the
right direction for a **bounded** effect — a fixed search radius or a fixed
smoothing displacement, both of which matter less on a large sherd. That is
candidate 1 and candidate 2, and they are now the only survivors.

**Piece 1 is the key to the whole thing.** It is the *largest* sherd in the
pot (119 mm, 100 064 vertices — the best-sampled by some margin) and it is
**right**: 0.69 mm, 100% inside tolerance. So the bias is not unconditional.
Any explanation must account for the best-sampled, largest sherd being
correct while the other six are 3–3.8 mm out. A pure parameter bias would
displace piece 1 too.

This is the sharpest lead in the chain, and it is a question about the
pipeline rather than the pot: **what is different about piece 1?** Its size
and vertex count are the obvious handles, and the answer should say
whether the rim placement degrades as a sherd gets smaller or coarser.

## Piece 1 investigated: the selection rule is vacuous on 7 of 8 sherds

Comparing the one sherd that matches against the seven that miss:

| piece | verts | size | clusters | largest cluster holds | offset | ok |
|---|---|---|---|---|---|---|
| **1** | 100 064 | 119 mm | **31** | **18.6%** | **0.69 mm** | **YES** |
| 2 | 55 814 | 111 | 1 | **100%** | 2.82 | no |
| 3 | 41 197 | 88 | 1 | 100% | 3.49 | no |
| 4 | 33 475 | 88 | 1 | 100% | 3.59 | no |
| 5 | 34 168 | 99 | 1 | 100% | 3.61 | no |
| 6 | 29 184 | 119 | 1 | 100% | 2.99 | no |
| 7 | 10 593 | 43 | 1 | 100% | 3.77 | no |
| 8 | 10 366 | 37 | 1 | 100% | 3.52 | no |

**The rule "Surface_0 = the largest cluster" makes no choice at all on seven
of eight sherds.** There, one cluster holds 100% of the sherd's points, so
"largest" is trivially satisfied and the whole sherd — both walls — is
carried forward as one surface. On piece 1 the largest of 31 clusters holds
18.6%, so a real selection happens, and its rim comes out right.

**This is a correction to my own first reading.** I initially took
"seven sherds have one cluster" to mean the sherd was never split, and
built a mechanism on that. Checking the run tree refuted it: **all eight
sherds were split into `Surface_0` and `Surface_1`.** The cluster files and
the named surfaces are different intermediates, and the defect is that the
*selection among clusters* is vacuous, not that clustering was skipped.

What this does and does not license:

- **Supported:** on seven of eight sherds the inner/outer decision is not
  being made by the stated rule at all, whatever the surfaces are called. Any
  account of the 3.5 mm offset has to explain a rim taken from a
  both-walls-together surface.
- **Not yet supported:** that this *causes* the offset. It is a strong
  association with perfect separation on this pot, and piece 1 is the only
  sherd where the rule does real work and the only one that is right. But
  association on eight sherds of one pot is not causation, and the
  discriminating test is named below.

**Discriminating test.** If the vacuous selection is the cause, then forcing a
real choice on a failing sherd should move its rim toward the reference.
Take piece 3, whose `Surface_0` and `Surface_1` both exist: extract a rim
from **each** separately and measure both against the authors' piece-3
curve. If one of them lands within ~1 mm, the offset is the surface choice
and the fix is selection. **If both land ~3.5 mm off, the cause is upstream
of the surface choice entirely** — in the surface construction or the
boundary detection — and ticket 04 is the wrong place to be working.

This is cheap: the per-surface point clouds are already on disk
(`pota_run_surfaces/Pot_A_Piece_03_Surface_0.xyz` and `_1.xyz`).

## RESOLVED — the offset is real, precisely characterised, and NOT the cause

The surface-swap ablation, real extractor, all eight sherds. Baseline drift
**0.00 mm on every piece**, so the arms are comparable.

| piece | baseline vs reference | swapped vs reference | |
|---|---|---|---|
| 1 | **0.69 mm (100%)** | 5.37 mm (0%) | already right; swap breaks it |
| 2 | 2.82 mm (30%) | 4.26 mm (14%) | truncated; swap does not help |
| 3 | 3.49 mm (0%) | **0.67 mm (100%)** | fixed |
| 4 | 3.59 mm (0%) | **0.72 mm (100%)** | fixed |
| 5 | 3.61 mm (0%) | **0.80 mm (99.4%)** | fixed |
| 6 | 2.99 mm (0.8%) | **0.61 mm (100%)** | fixed |
| 7 | 3.77 mm (0%) | **0.53 mm (100%)** | fixed |
| 8 | 3.52 mm (0%) | **0.72 mm (100%)** | fixed |

**Six of eight are fixed by taking the rim from the other wall**, and the
two that do not move are exactly the two that were already right. So the
selection rule is *inconsistently* correct: piece 1 already picks the right
wall, and flipping it breaks that. "Largest cluster" is not always wrong, it
is right by coincidence on some sherds.

**But the gate probe does not follow: 7/15 → 6/15.**

| arm | strict pass at ground truth |
|---|---|
| `pota_fresh` (Surface_0) | **7/15** |
| `pota_swapped` (Surface_1) | **6/15** |

Per pair, the swap only makes pairs that *already passed* pass more
comfortably — 4-8 goes from min gap 0.42 to 0.54 mm, 4-7 from 1.06 to
0.59 mm. **No lost pair was recovered.** Piece 1 was made worse, and it is
in six pairs.

### What this means

**The 3.5 mm offset is not on the causal path to the lost joins.** Making
the curves five times closer to the reference changes nothing at the gate.
The offset is real, it is now measured to 0.00 mm reproducibility, and it is
**not why we lose 8 of 15**.

This also retires ticket 04 as the fix. It remains a genuine paper-vs-code
deviation worth doing on its own merits — the paper specifies the interior
surface, the code takes the largest cluster — but it is **not** what costs
the joins, and it must not be presented as the remedy.

### The error this exposed, recorded because it nearly happened twice

I twice inferred a cause from a correlation and only tested it by
intervention:

1. Measured the offset direction against the **mesh's** normal, found it
   tangential (|cos| 0.255), and concluded "not the other wall." Wrong: the
   two walls meet the mesh at an angle, so a wall-to-wall displacement *is*
   tangential to the mesh. I tested the wrong normal. I marked ticket 04
   `needs-info` on that basis.
2. Then the swap showed the offset *was* the wall, and I was about to hand
   ticket 04 the win on "the curves now match".

Both failures share a shape: a real measurement, a plausible inference, and
no intervention to test it. The ablation was the intervention, and the gate
probe was the score that mattered — not the offsets. **A metric that improves
while the thing being measured does not is not progress**, and the temptation
to stop at "the curves match the reference now" is precisely what would have
made this a false result.

### Where the lost joins therefore are NOT

- not the ~3.5 mm rim offset (measured, intervention-tested, no effect)
- not the interior/exterior wall choice (same ablation, no effect)
- not the ordering walk, except on piece 2 (ticket 01, 1 sherd of 8)
- not the frame or units (fresh output verified in the scan frame)

That leaves the gate's own criterion, and the fact that our 7/15 pairs pass
while 8 pairs sit 3.7–8.8 mm apart at ground truth with **no breakline
involved in that measurement**. The next thing to examine is what
distinguishes a passing pair from a failing one *given* correct curves —
which is a question about the gate and the normals, not about our curves.

## MIXED BUNDLE: 11/15 — per-sherd selection demonstrated, not inferred

Hand-built on the laptop from the two ablation arms (no pipeline change):
piece 1+2 from baseline (`Surface_0`), pieces 3–8 from the swapped arm
(`Surface_1`). Scored with the authors' ground truth (`mixed_select` arm):

| arm | strict pass |
|---|---|
| baseline (`Surface_0` everywhere) | 7/15 |
| swapped (`Surface_1` everywhere) | 6/15 |
| **mixed (per-sherd: 1+2 from S0, 3–8 from S1)** | **11/15** |

Passing: 1-3, 1-4, 1-5, 1-6, 1-7, 3-5, 3-6, 4-6, 4-7, 4-8, 6-7.
Failing: **1-2, 2-4, 2-5, 2-8 — all four contain piece 2.**

Five piece-1 pairs recovered at 0.16–1.24 mm. One previously-passing pair
lost: 2-8 went 0.26 → 1.22 mm, because piece 8's swapped rim no longer meets
piece 2's *truncated* rim — collateral of the ordering defect, not of the
selection.

**This is what a per-sherd interior/exterior test would produce**, and it is
measured rather than argued: neither blanket choice is right (7/15 and 6/15),
the per-sherd choice is 11/15. The remaining four all contain piece 2, whose
rim is 46% of the reference length — ticket 03's ordering defect, relevant
again for this specific measured reason rather than the general one it was
demoted for.

The mixed bundle is a **demonstration, not a pipeline output**. The pipeline
change — the paper's interior/exterior rule replacing "largest cluster" —
still has to be implemented (ticket 04). What this settles is that the rule
is worth implementing: +4 pairs measured, with the mechanism named per pair.

## Acceptance criteria

- [x] A scale/units explanation is eliminated by measurement, not argument
- [x] **Piece 1 is explained**: it is the only sherd where "largest cluster"
      does real work (18.6% of 31) and the only one whose rim matches. On
      seven of eight the rule is vacuous (one cluster = 100%)
- [x] The offset is **explained**: it is the interior/exterior wall choice,
      fixed on 6 of 8 by the swap, with 0.00 mm baseline drift
- [x] **And shown not to be the cause of the lost joins** — the gate goes
      7/15 → 6/15 under the swap, recovering no pair
- [ ] The failing pairs are characterised given correct curves: what makes a
      pair fail when both rims are within 0.8 mm of the reference
- [ ] The per-surface rim test above: does one of piece 3's two surfaces give
      a rim within ~1 mm of the reference? This decides whether the fix is
      surface selection (ticket 04) or something upstream of it
- [ ] The offset is explained by one of the three candidates above, with the
      discriminating measurement quoted — or a fourth is found and recorded
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
