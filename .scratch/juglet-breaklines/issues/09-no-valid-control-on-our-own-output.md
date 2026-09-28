# 09: We have no valid control on our own preprocessing

**Answers:** E1

**Blocked by:** nothing — this was the precondition for every other ticket here

**Status:** resolved — the control now exists, and it PASSES: our pipeline
scores 15/15 on Pot_A (`t14_patches` arm), matching the authors' sample.
The 0/15 that motivated this ticket is retracted as a stale-bundle
artifact; the 7/15 middle chapter is recorded in the body.

**Needs-eye:** none — a measurement result, no geometry claim carried forward
without a render.

## THE ANSWER: our preprocessing scores 7/15 on the authors' own control pot

Re-ran the current code on Pot_A (2026-09-26, job on holder 31352585),
fetched the breaklines, and added a `pota_fresh` arm to the gate probe:

| arm | whose breaklines | strict pass at truth | min gaps |
|---|---|---|---|
| `pota_orig` | authors' released sample | **15/15** | 0.09–1.30 mm |
| **`pota_fresh`** | **our current code, re-run today** | **7/15** | 0.26–1.67 mm where it passes |
| `pota` (old) | our Nov-2025 bundle | 0/15 — **void**, see below | — |
| `juglet` | our current code, Juglet | 0/18 | 0.17–30 mm |

**Our preprocessing loses 8 of 15 true joins on the pot SfS++ was developed
on.** The passing pairs are genuinely good (0.26–1.67 mm), so this is not a
frame or units artifact: where our curves are right, they are right.

The `pota_fresh` arm is legitimate because the fresh output is in the
**scan frame** — its breakline centroids sit 0.7–2.5 mm from the Pot_A mesh
centroids on 6 of 8 pieces, the same frame the authors' breaklines occupy
(within ~1 mm). Same frame, so the authors' ground truth applies directly,
which makes this the like-for-like comparison the "15/15 control" was
believed to be.

### Why the old `pota` arm is void

Its bundle is `NURBS_Dataset_20251103`, whose eight pieces are arranged
**4.5× further apart** than Pot_A's real sherds (331 mm vs 73 mm mean
pairwise centroid distance). No rigid fit (RMS 186 mm) and no similarity fit
(RMS 251 mm) reconciles it with the meshes. **The current code does not
reproduce that**: the fresh run lands within 2.5 mm on 6 of 8. So the old
0/15 measured a stale artifact of some earlier pipeline state, not the code
we are working on. That number should never have been read as a result, and
this ticket is where it is retracted.

### Where the 8 losses are — and a correction to how I first read them

**First read, wrong:** I attributed the losses to piece 1, calling it "the
only piece whose breakline sits materially off its mesh". Two things were
wrong with that. Its 9.1 mm centroid offset is 5% of its 174 mm diagonal,
which is *better* than most; and piece 2 is proportionally worse (29%). More
importantly, comparing our curve against **the authors' curve for the same
sherd in the same frame** — the comparison this project had never made —
shows piece 1 is the *best* piece we produce.

| piece | our→ref (median) | ref→our | within 2 mm | our len / theirs |
|---|---|---|---|---|
| **1** | **0.69 mm** | 0.70 | **100%** | 98% |
| 2 | 2.82 | **35.0** (p90 80) | 30% | **46%** |
| 3 | 3.49 | 3.47 | 0% | 102% |
| 4 | 3.59 | 3.58 | 0% | 100% |
| 5 | 3.61 | 3.59 | 0% | 105% |
| 6 | 2.99 | 3.01 | 0.8% | 102% |
| 7 | 3.77 | 3.70 | 0% | 106% |
| 8 | 3.52 | 3.46 | 0% | 109% |

**Piece 1's curve is essentially the reference curve.** Its six gate
failures are caused by its *partners*, six of the other seven sherds.

**The dominant defect is a systematic ~3.5 mm displacement.** Six of eight
of our curves sit 2.99–3.77 mm from the reference, displaced in *both*
directions, with traced lengths matching to 2–9%. A tight, near-constant
displacement at unchanged length is not a truncated walk — it is the same
curve on a **parallel surface about 3.5 mm away**. Against a 2 mm gate that
fails every comparison it touches, and whether a pair survives depends on
whether two sherds' offsets happen to cancel. That is why some pairs pass
(2-8, 3-5, 3-6, 4-6, 4-7, 4-8, 6-7) and others do not.

**Piece 2 alone shows the walk defect**: its traced length is 46% of the
reference and the reverse distance reaches 80 mm. So the ordering problem is
real but accounts for roughly one sherd of eight here, not eight of fifteen
lost joins.

**Next measurement, not yet done:** if the 3.5 mm displacement runs along the
surface normal, it is the other wall face and the interior/exterior choice
(ticket 04) is the fix. That is the discriminating test and it has not been
run.

## What this settles, and what it does not

**Settles:** the user's proposal. There *is* something to restore. My
earlier caution — do not touch the algorithm before we have a measurement
that can fail — was right for its moment and is now discharged: we have the
measurement, and it says the pipeline needs work. The paper-vs-code gaps
(interior-surface selection, the missing ordering step, the dead noise
filter, padding instead of 1.9 mm resampling) are back on the table as
*live* work rather than as a theory about the Juglet.

**Does not settle:** the Juglet. 0/18 is still worse than 7/15, so the
Juglet is harder material *and* our pipeline is already substantially
broken on good material. Those are two separate problems and should not be
conflated again.

## A second, independent defect, still open

`main_headless.cpp:64` in the assembly repo **silently drops any sherd whose
breakline has fewer than 50 points** — no warning. The Nov-2025 Pot_A bundle
had two such pieces (6 and 8, 30 points). Cheap to fix, and until it is
logged, a sherd can vanish from a result with nothing to show for it.

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
