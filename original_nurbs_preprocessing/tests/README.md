# Edge-line ordering tests

Tests for `getPointsInSequence`, the ordering step of SfS++ §IV-B1. The
ticket this serves is `.scratch/juglet-breaklines/issues/01-establish-cpp-test-seam.md`;
the defect itself is documented in `../edge_line_ordering.h`.

## Running them

The container has PCL, Eigen and CGAL; the laptop has none of them, so
these run on Spartan inside a held allocation:

```bash
srun --jobid=<HOLDER_JOBID> --overlap --cpus-per-task=8 bash run_ticket01.sh
```

That builds, runs every test, then runs `ctest` so the enabled/disabled
split is visible. It **refuses to run the tests if the build failed**, so a
stale binary can never be measured — a failure mode that already bit once
during this ticket's development.

To run one test, inside the container:

```bash
./test_edge_line_ordering juglet-boundary
```

Valid names: `clean-rim`, `juglet-boundary`, `dense-patch`,
`offplane-scatter`, `no-revisit`, or `all` (the default).

## What the tests assert, and why coverage

Every assertion is on the **output cloud**, never on internals, log text or
point counts alone.

The contract: **a traversal of a rim visits essentially every rim point.**
So the assertion is `coverage = out/in >= 0.9`, plus a traced-length check
`traced / reference >= 0.3` where `reference` is the cloud's minimum
spanning tree length — a proxy for rim length that tracks the true value to
within 1.7% on circles of radius 6.3, 15 and 40 mm.

**Coverage, not step size.** An earlier version of this test asserted that
the largest step would dwarf the median step, and it **passed** while the
function was discarding 85% of the rim. A walk that stops early takes
*small* steps. No check on step size can see this defect. The step-ratio
idea came from this ticket's original acceptance criterion, which was
wrong; measurement corrected it.

## Observed output

Taken from the cluster on 2026-09-26, not predicted:

```
  [clean-rim         ] in= 400 out= 400 cov=1.000 traced=  94.01mm ref=  94.01mm traced/ref=1.000
  [juglet-boundary   ] in=  59 out=   9 cov=0.153 traced=   2.14mm ref=  36.84mm traced/ref=0.058
  [dense-patch       ] in=  59 out=   9 cov=0.153 traced=   2.36mm ref=  92.39mm traced/ref=0.026
  [offplane-scatter  ] in= 400 out=  52 cov=0.130 traced=  35.54mm ref= 215.03mm traced/ref=0.165
  [no-revisit        ] in=  59 out=   9 cov=0.153 repeats=0
```

The real Juglet edge: **59 points in, 9 out** — 2.1 mm of rim traced out of
36.8 mm, about 6% of it. That is the whole defect in one line.

`juglet-boundary` is real pipeline output. The other two are
**reconstructions, ours, not the authors'** — the paper says nothing about
sampling density; they were built to match properties measured on the real
cloud.

## Known-broken tests, and how they are disabled

| Test | State | Why |
|---|---|---|
| `clean-rim` | enabled, passes | the case that already works; a fix must not break it |
| `no-revisit` | enabled, passes | no point appears twice |
| `juglet-boundary` | disabled, fails | the defect, on a real sherd edge |
| `dense-patch` | disabled, fails | same defect, synthetic cause |
| `offplane-scatter` | disabled, fails | a second, independent trigger |

Each is re-enabled by the ticket that turns **that test** green — never in a
batch, and never by loosening a threshold.

**On the mechanism, measured rather than assumed:** the `DISABLED_` *name
prefix* did **not** work. With it alone, `ctest` ran all three and reported
`40% tests passed, 3 tests failed out of 5`. The prefix is now only a
visible label; the `DISABLED` **test property** does the actual disabling.
`run_ticket01.sh` must report 2/2 passed with 3 disabled — if it does not,
this file is out of date.

## Two numbers that do not belong to this function

The figures *"10–24 mm internal jumps, 0.27–2.15× traced length"*, which
appear in the older diagnosis, were measured on the **emitted breakline
files** — after B-spline resampling and 200-point padding. They describe a
later stage. They were previously quoted in `edge_line_ordering.h` as
though they described this function, which was wrong, and no test here
asserts on them.

## The fixture

`data/juglet_boundary_59.txt` is a real 59-point Juglet boundary cloud, as
the pipeline wrote it. Plain text because `*.pcd` is gitignored
project-wide, so a `.pcd` fixture could never be committed and the test
could never run on a fresh clone.

**Scope: one sherd face of eighteen, and it is the worst of them.**
`Temp_edge/` is overwritten per sherd, so the file left on the cluster is
whichever sherd ran last. Ticket 08 later measured all eighteen Juglet
faces (9 sherds × 2 wall faces), and this fixture turned out to be the
**minimum** coverage in the set:

| | coverage |
|---|---|
| this fixture | **0.153** (worst of 18) |
| median Juglet face | **0.866** |
| faces reaching full coverage | **8 of 18** |

The walk is therefore **not** uniformly broken on the Juglet — it traverses
nearly half the sherd faces completely. It is the right fixture to regress
against because it is real, tiny and maximally sensitive, but it is the
worst case and must not be quoted as typical.

**And the cause is not settled.** The mechanism this test was written
against — uneven spacing along the rim — reproduces the failure exactly in
synthetic form, but across the real 18 faces spacing spread does *not*
predict which ones fail: the face with the *highest* spread (8.1×)
succeeded completely, while this low-spread face (2.7×) failed worst. The
mechanism is **sufficient but unproven**. See ticket 08.
