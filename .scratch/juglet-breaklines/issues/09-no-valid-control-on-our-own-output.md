# 09: We have no valid control on our own preprocessing

**Answers:** E1

**Blocked by:** nothing — this is the precondition for every other ticket here

**Status:** ready-for-agent

**Needs-eye:** none — this is a measurement defect, not a geometry claim.

## The finding

The acceptance probe has three arms. Run them:

| arm | whose breaklines | strict pass at truth |
|---|---|---|
| `pota_orig` | the SfS++ **authors' released sample** | **15/15**, min gaps 0.09–1.30 mm |
| `pota` | **our preprocessing's Pot_A output** | **0/15**, min gaps **2466–3305 mm** |
| `juglet` | our preprocessing's Juglet output | 0/18, min gaps 0.17–30 mm |

**The 15/15 that has been quoted as "Pot_A no-regression" is the authors'
data, not our output.** `data_path.h` has two separate Pot_A datasets:
`POT_A` reads our pipeline's `NURBS_Dataset_20251103/`, and `POT_A_ORIG`
reads `sfs_main/original_samples/`. The control has been the second all
along.

And our own Pot_A output scores 0/15 — **but that number is not usable
either.** Both Pot_A ground-truth files are byte-identical, and our
breakline bundle sits **1881 mm away in z** from the authors':

| | piece-centre range (mm) | per-piece extent (median) |
|---|---|---|
| ours | x −198…172, y −155…181, z −1676…−1370 | 25 × 71 × 64 |
| authors | x −30…29, y −7…52, z 300…429 | 53 × 89 × 40 |

A "gap" of 2466–3305 mm is that offset, not a broken curve. **The `pota`
0/15 measures a coordinate frame, not the quality of our curves.** Reporting
it as a geometry result would repeat exactly the mistake this workspace has
already paid for twice (chamfer distance on unnormalised data; the
measurement-broken finding in `intent/S1`).

## Why the Juglet's 0/18 is still believable, and the Pot_A one is not

The Juglet bundle and its ground truth were built together and are mutually
consistent: its reported gaps (0.17–30 mm) are the right order for a
1.8 mm-walled pot. A frame error would show as ~10³ mm. The Juglet arm is
internally consistent; the Pot_A arm is not, because it borrows the
*original* sample's ground truth while supplying *our* breaklines.

## The consequence

**There is currently no valid measurement of our own preprocessing on any
pot it should handle.** So the central question — *is the Juglet's 0/18 our
preprocessing's fault, or this material's?* — **cannot be answered**, and
every ticket in this chain is reasoning around that gap.

This also inverts the priority order. Before improving anything, the
comparison has to be made capable of failing informatively.

## A second, independent defect found on the way

`main_headless.cpp:64` in the assembly repo:

```cpp
if (shard[i].edge_line_.point_.cols() < 50) { shard_on_off[i] = false; ... }
```

**A breakline with fewer than 50 points silently removes that sherd from
matching** — no warning, no log line, the pot just assembles from fewer
pieces than it should. And our Pot_A bundle already has two such pieces:

| piece | points in our bundle |
|---|---|
| 6 | **30** |
| 8 | **30** |
| others | 116–162 |

So on Pot_A the assembler would quietly drop 2 of 8 sherds. This is a real
interface defect independent of the Juglet, it is cheap to fix, and it has
an unambiguous success criterion. Note also that this bundle holds 30–162
points, **not** a padded 200 — so the padding-to-200 discussed in ticket 06
is not reflected in this Nov-2025 bundle at all.

## What to do

1. **Establish the frame convention.** Find out what transform the
   original sample's ground truth encodes, and what our preprocessing
   writes instead. One of the two is wrong; the paper does not say, so this
   is a decision to record, not a bug to guess at. Candidate: the
   `NURBS_Dataset_*` bundles are written in an axis-extracted frame that the
   assembly's GT was never built for.
2. **Re-run the `pota` arm in a matched frame.** It must be possible for the
   arm to report 15/15. Until it can pass, it cannot fail informatively.
3. **Then re-read the Juglet.** With a working control, the comparison
   Juglet-vs-Pot_A on our own output finally means something, and the
   face-selection hypothesis (ticket 04) becomes testable.
4. **Separately: make the 50-point drop visible.** At minimum log which
   sherds were dropped and why. Silently assembling from a subset is how a
   bad extraction looks like a good result.

## Acceptance criteria

- [ ] The `pota` arm can report a non-zero pass rate, or the reason it
      cannot is documented and the arm is labelled not-a-control
- [ ] The frame difference between our output and the original sample is
      explained in one paragraph, with the transform that reconciles them
- [ ] The 15/15 control is either re-established on **our** output or
      relabelled everywhere as *the authors' sample*, so no reader takes it
      as evidence about our pipeline
- [ ] The 50-point drop is logged, and the number of dropped sherds is
      reported for both pots
- [ ] `intent/E1` states plainly that no valid control existed before this
      ticket, so earlier reasoning that assumed one can be located and
      re-examined

## Note

This ticket exists because the "Pot_A is not regressed" control was read as
evidence about our preprocessing when it was evidence about someone else's.
That is not a code bug. It is a missing measurement, and it was invisible
because the number attached to it looked like a pass.
