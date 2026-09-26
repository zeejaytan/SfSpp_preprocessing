# 08: Is the ordering defect Juglet-specific, or general?

**Answers:** E1

**Blocked by:** 01-establish-cpp-test-seam

**Status:** resolved — and the answer invalidates the premise of ticket 03

**Needs-eye:** none — measurements on real and synthetic geometry, no
geometry claim carried forward without a render.

## ANSWER: the defect is GENERAL, and it is therefore not the Juglet's problem

**The walk truncates on roughly half the sherd faces of *both* pots.**

| | Juglet | Pot_A (the 15/15 control) |
|---|---|---|
| faces measured | 18 (9 sherds × 2 walls) | 16 (8 sherds × 2 walls) |
| fully covered (≥0.9) | **8 / 18** | **7 / 16** |
| median coverage | 0.866 | 0.883 |
| worst coverage | 0.143 | 0.252 |
| traced/ref, median | 0.914 | 0.904 |

The two pots are indistinguishable on this measure. **Pot_A assembles
perfectly (15/15 correct joins) while suffering the same truncation.** So the
truncation is neither Juglet-specific nor, apparently, sufficient to prevent
correct reassembly.

### The consequence, which is the point of this ticket

Ticket 01 diagnosed the walk as the reason the Juglet proposes zero joins,
and ticket 03 was going to be built on that. **That premise is wrong.** A
defect that is equally present in the pot that works cannot explain the pot
that doesn't.

This is the failure mode `../AGENTS.md` warns about — *"the method genuinely
failed" / "the measurement was broken" / "the reference answer was wrong"*
kept apart. Here it is a fourth thing: **a real defect that is not the
cause of the observed failure.** The defect is real; the causal story was
wrong.

The walk is still worth fixing. It discards 15–75% of an edge on half the
faces of both pots, which is a genuine quality problem, and the paper
specifies a normal-vote ordering the code never had. But it must be
presented as **an independent defect, not the Juglet's cause**, and it must
not be credited with fixing the Juglet.

### What the measurement also refutes

- **Exact duplicates do not predict failure.** Every Pot_A cloud contains
  duplicates (26–124 points, median 54) and Pot_A does *better* than the
  Juglet, most of whose clouds have none. Whatever breaks on the Juglet, it
  is not duplicate-driven.
- **Spacing spread does not predict failure, on either pot.** Within the
  Juglet, the highest-spread face (8.1×) was covered perfectly (1.000) and
  the worst face (0.153) has low spread (2.7×). The spread metric is
  *degenerate* for Pot_A — every Pot_A cloud has `nn_min = 0`, so p90/p10
  divides by zero — which is why it cannot be compared across pots at all.

So ticket 01's mechanism (density contrast, off-plane scatter) is
**sufficient in synthetic form and unproven on real data**, and the honest
statement is now: *the walk truncates on about half of all sherd faces, and
we do not know which input property decides which faces.*

## What this points at instead

The preprocessing-side defect is general, so it does not discriminate
between the two pots. Something else must explain the Juglet's zero joins.
The leading candidate is already on record and is **not** in this chain:

- **Arbitrary face assignment.** `Surface_0` is the *largest cluster* with
  no interior/exterior test (ticket 04's territory). On a thin thrown pot
  the largest cluster tends to be the same physical face on both sherds, so
  the gate sees coincident traces; on the Juglet the inner and outer areas
  are close in size, so "largest" lands on *different* faces for different
  sherds. The earlier finding stands: **10 of 18 true Juglet mates are
  inner-vs-outer**, i.e. the traces are being compared against the wrong
  face.

That is a face-*selection* problem, not an ordering problem, and it would
produce exactly what we see: a pot where the geometry is fine but the
matches are systematically against the wrong side of the wall.

**This is a hypothesis, not a result.** It is consistent with the evidence
and it is the next thing to test, but nothing here demonstrates it.

## Two limitations, stated rather than buried

1. **The Pot_A breaklines I measured may not be the ones that scored 15/15.**
   I regenerated both pots' breaklines in an isolated tree
   (`diag_scope/`, nothing live touched). The 15/15 figure comes from an
   earlier assembly run against `Dataset/Breaklines/Pot_A`. The pipeline is
   deterministic given its inputs, so they *should* be equivalent — but that
   is an assumption, and this workspace has been burned by assuming an
   artefact was the one that was measured. **Before acting on "Pot_A
   truncates yet scores 15/15", confirm the 15/15 run used these
   breaklines.**
2. **Coverage is measured on the walk's output, not on the emitted
   breakline files.** The emitted files are resampled and padded to 200
   points, which is exactly what hid a 3.6 mm fragment before. Truncation
   measured here may be partly masked downstream.

## Method, so it can be repeated

- `run_scope_check2.sh` — Juglet arm, staged from the complete per-piece set
  in `Juglet_Dataset_tidycheck/SfS_pp/Surfaces/`. 18/18 snapshots.
- `run_scope_pota.sh` — Pot_A arm: builds `MeshPreprocessingHeadless`, runs
  the mesh stage (no Pot_A `_unclustered.ply` existed anywhere), then the
  edgeline stage. 16/16 snapshots.
- `scripts/diagnostics/compare_pot_boundary_clouds.py` — the measurement.

Both arms run in throwaway trees because the binaries use **relative**
paths, so the working directory decides what is read and written. Running in
the real tree would have overwritten `Temp/Temp_edge/` and `Dataset/`, which
may hold live assembly inputs.

`Temp/Temp_edge/<pot>/boundary.pcd` is overwritten per sherd, so both runs
poll every 0.3 s and de-duplicate by md5. Each script reports
snapshots-against-pieces and warns if they disagree; both were complete
(18/18 and 16/16), so the samples are sound.

## Acceptance criteria

- [x] Pot_A boundary clouds measured with the same definitions as the Juglet
- [x] The comparison states explicitly whether Pot_A's spacing variation is
      materially smaller — **it cannot be compared at all**, because every
      Pot_A cloud contains exact duplicates and the metric divides by zero.
      Reported as a metric limitation rather than as a result.
- [x] The finding is recorded as one of the three named outcomes. It is
      **"the defect is general"** — Pot_A truncates too.
- [x] Ticket 03's premise is corrected and its status recorded as blocked
      on a causal explanation, not on the fix itself

## Note on why this ticket existed

It was written to answer "Juglet or general?" *before* a fix was built on
the answer. It did its job: the answer is "general", the fix's premise is
wrong, and nothing was built on it. One narrow scope correction came out of
it too — the 59-point fixture committed in ticket 01 is the **worst of the
18** Juglet faces, not a typical one, and ticket 01's text and the test
README have been corrected to say so.
