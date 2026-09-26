# 01: Establish a C++ test seam for the edge-line stage

**Answers:** E1

**Blocked by:** None (can start immediately)

**Status:** in-progress

**Needs-eye:** none — this ticket produces a test target and a
characterisation, not a geometry claim.

## What was built

A CTest target that compiles `edge_line_ordering.cpp` — **the same file
the pipeline compiles** — so a test can never pass against different code
than production uses. The ordering code was lifted verbatim out of
`edgeline_extraction_headless.cpp`, where it was a free function in a
137 KB translation unit whose `main()` sits at line 3488 and which could
not be tested without dragging the whole pipeline in.

One command, inside the container, on Spartan:

```bash
srun --jobid=<HOLDER> --overlap bash run_ticket01.sh
```

`run_ticket01.sh` builds, runs the tests, then runs `ctest` so the
enabled/disabled split is visible. It refuses to run the tests if the
build failed, so a stale binary can never be measured.

## A CORRECTION TO THIS TICKET'S OWN ACCEPTANCE CRITERION

The criterion as first written asked for a test that fails on *"a stalled
or derailed traversal producing internal jumps far larger than the median
step"*.

**That criterion was wrong, and measurement said so.** A walk that stops
early takes **small** steps — it does not take large ones. The first
version of this test asserted exactly that ratio, and it **passed** while
the function was in fact discarding 85% of the rim. Had the criterion been
treated as correct, the defect would have been declared uncharacterisable
and the real one missed.

The defect is **truncation**, and the property that sees it is
**coverage**: a traversal of a rim visits essentially every rim point.
The criterion now reads *"a stalled traversal returning far fewer points
than it was given"*, and the test asserts coverage.

Two of this ticket's own artefacts were wrong in the same way and are
corrected here:

- The figures *"10–24 mm internal jumps, 0.27–2.15× traced length"*, quoted
  in the original diagnosis and then repeated in
  `edge_line_ordering.h`, were measured on the **emitted breakline files**
  after B-spline resampling and 200-point padding. They describe a later
  stage and say nothing about this function. No test asserts on them.
- The first synthetic test claimed to represent "a duplicate clump". It was
  not a clump: it placed 12 points *around* a rim rather than crowding one
  spot, so the walk correctly ignored them. It also asserted the wrong
  property. Both fixed.

## The defect, as measured

The walk appends the first unused point among its K nearest neighbours,
`K = max(5, min(50, n/10))`. It truncates as soon as all K candidates are
already visited; the outer loop then spins and appends nothing. Two
properties of the input decide whether that happens:

| Trigger | Evidence |
|---|---|
| **Density contrast** — part of the rim sampled ≥K× denser than the rim's median spacing | Real Juglet cloud: spacing 0.096–1.96 mm (**20×**), and **85% of points** have ≥K neighbours within K × median spacing. Result: **59 points in, 9 out**, 2.1 mm traced of a 36.8 mm rim — **6% of the rim**. |
| **Off-plane scatter** — points scatter further off the rim than the local spacing | Reproduced independently of density contrast: 0.6 mm scatter on a well-sampled rim drops coverage to 0.37. |

A synthetic ring at 40× contrast reproduces the real failure **exactly**:
9/59, coverage 0.153, 50 stalled steps.

## Hypotheses tested and REFUTED

Kept deliberately — a discarded hypothesis is evidence too.

- **"The walk is bounded near 2K−1, independent of rim length."** Refuted.
  On synthetic rings the walk covers **100%** at every point count and every
  K, including with K pinned at 8 while the rim grows 32×. K alone does not
  truncate it. (`scripts/diagnostics/test_saturation_bound.py`)
- **"Near-duplicate points are the cause."** Refuted **for the live path.**
  The walk's input is `boundary.pcd`, reloaded at
  `edgeline_extraction_headless.cpp:959`. That file has **zero** exact
  duplicate pairs. The duplicate-ridden `boundaryImproved.pcd` is written
  and then discarded by the dead reload. Duplicates are real in that
  discarded file but do not reach the walk.
- **"Uneven angular spacing or off-plane noise is the cause."** Partly
  refuted as stated: neither alone reproduces it at low density. Both
  matter *relative to the local spacing* — which is the unified statement
  above.

## Scope of the fixture — do not over-read it

`tests/data/juglet_boundary_59.txt` is **one sherd of nine**.
`Temp_edge/` is overwritten per sherd, so the file left on the cluster is
whichever sherd ran last. It is the smallest available piece of real
evidence, not a summary of the Juglet, and must never be reported as one.

The run logs show boundary clouds of **86–524 points** across the Juglet
run (K = 8–50), with resampler inputs of 75–129 — so the truncation is not
uniformly 9-of-59 across all nine sherds.

## Tests

| CTest entry | State | What it pins |
|---|---|---|
| `edge_line_ordering_clean_rim` | **enabled**, passes | the case that already works; a fix must not break it |
| `edge_line_ordering_no_revisit` | **enabled**, passes | no point appears twice |
| `DISABLED_..._juglet_boundary` | disabled, fails | **the defect, on a real sherd edge** |
| `DISABLED_..._dense_patch` | disabled, fails | the same defect from a synthetic cause |
| `DISABLED_..._offplane_scatter` | disabled, fails | the second, independent trigger |

`DISABLED_` marks **known-broken behaviour and nothing else** — a passing
test is enabled. Each prefix is removed by the ticket that turns that test
green, never in a batch and never by loosening a threshold. The two
synthetic cases are labelled **reconstructions, ours, not the authors'**:
the paper says nothing about sampling density.

Thresholds are measured, not chosen. Clean rings give `traced/reference`
= 1.000; the real Juglet cloud gives 0.058; the reference (MST length)
tracks true rim length to within 1.7% on circles of radius 6.3, 15 and
40 mm. The 0.3 and 0.9 bounds sit in an ~8× empty gap between the healthy
and broken populations.

## Acceptance criteria

- [x] A test target is registered with CTest and runs from a single
      documented command, inside the container, on Spartan
- [x] The test target builds from the same source as the pipeline
- [x] Running the tests is one command, documented in the repository, and
      its output names the property that broke
- [x] No test asserts on log text, on point counts alone, or on the
      identity of an internal function — only on output geometry
- [x] The first test pins today's measured behaviour **on real geometry**
      and fails in a way that names the defect — **corrected from the
      original step-ratio wording, which measurement refuted**; see above
- [ ] Behaviour-preservation check: the extraction moved production code,
      so the pipeline must be re-run and diffed against the known-good
      bundle to prove the move changed nothing
- [ ] The Python transcription in `scripts/diagnostics/` is checked against
      the C++ on the same fixture, so the diagnosis rests on the shipped
      code and not on a re-implementation

## Still owed

Whether this is Juglet-specific or general is **not** answered here, and
the difference matters. Ticket 08 tests it: Pot_A's boundary clouds have
never been measured, and the mechanism predicts they are near-uniformly
sampled. Until that is measured, the honest claim is "the walk truncates
on unevenly sampled or scattered edges" — not "the Juglet breaks it".
