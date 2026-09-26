# 02: Make the extractor emit both wall faces, and cover the seam

**What to build:** the smallest change to `edgeline_extraction.cpp` that
makes Juglet breaklines pass a join gate, **one variable at a time**,
starting with the cause ticket 01 identified as dominant.

**Answers:** E1

**Blocked by:** 01 (the measurement decides which change to make first —
do not start this before 01 reports)

**Status:** **re-scoped 2026-09-26 — the premise was wrong.** The
extractor ALREADY emits both wall faces (`Breakline_0` and
`Breakline_1`); the assembler simply never reads the second one. And
reading it makes the gate *worse*, not better. The remaining real
problem is **coverage**. Findings below, all measured on the laptop
before touching any C++.

## Findings (2026-09-26) — three of them, and they re-point the work

Scripts + output: `../structure-from-sherds-pp/artifacts/juglet_run1/`
(`both_breaklines_test.py|.txt`, `face_pairing_test.py|.txt`,
`normal_convention_test.py|.txt`).

### 1. The extractor already emits both faces — no change needed here

`Breakline_1` is a genuine trace of the second surface: distance to
`Surface_1` is 0.07–0.34 mm on 7 of 9 sherds (3.17 mm on s7, 2.87 mm on
s5). `Breakline_0` is the `Surface_0` trace. **All 9 `Breakline_0` files
sit on `Surface_0`** (median 0.11–0.30 mm) — the assembler has only ever
seen one wall face per sherd, because `data_path.h` hardcodes
`Breakline_0.pcd` and nothing reads the `_1` file.

### 2. …but reading both makes the gate worse, so do NOT "just read both"

| breaklines given to the gate | true mates pass | false pairs pass |
|---|---|---|
| `_0` only (today) | **0/18** | 1/18 |
| `_1` only | 0/18 | 1/18 |
| both pooled | 1/18 | **4/18** |

Pooling lets an inner-face point match an outer-face point 0.17 mm away
with opposed normals. All four face-pairing conventions were tested
(`0↔0`, `1↔1`, `0↔1`, `1↔0`): only 1/18 true mates passes under *any*
convention. **Face pairing is not the lever.**

### 3. The normal convention is a real but small effect — and it is an ASSEMBLER change

Two sherds that mate share one fracture surface, so their outward
normals are **antiparallel** (dot ≈ −1), while
`UnifiedPotteryValidation` demands `dot > +0.85`.
`robust_icp.cpp:396` already uses `abs(dot)` — the pipeline contradicts
itself. At ground truth, `abs` lifts true mates **0/18 → 2/18** (6-7, 2-9)
with **no** increase in false pairs (1/18 either way).

**This was already tried and refuted at runtime** (SFS_NORMAL_ABS=1,
0/18) — but that run was at *refined* ~10 mm-off placements, never at
truth. The laptop test at truth shows the effect is real but confined to
pairs that are also close enough. Not the main fix, and not ours.

### 4. Coverage is the real remaining problem

14 of 36 directed true contacts lie within 2 mm of a breakline point;
**the other 22 are 2.8–29.5 mm away.** The breaklines *are* closed loops
(loop gap ≈ median step on all 9 sherds), so this is not a broken loop —
it is a loop that does not pass through the seam. Per sherd, the
untraced fraction is large (e.g. s1 has contacts 23.5–27.9 mm from its
own breakline while the loop looks well-formed).

**So the work is:** find why the traced rim misses the seam region. The
watertight mesh topology gives no open boundary to compare against
(edge-use histogram is all 2s — verified), so "the rim" must be defined
from the surface clusters. Candidate causes, to be separated one at a
time: (a) the fracture region is being dropped by the surface
segmentation before the rim trace runs; (b) the rim trace is closing on
the wrong loop (an interior curvature ring rather than the outer
boundary); (c) the resampling/BSpline step pulls the loop inboard.
**Suspect (b) first** — the radial band of the traced loop sits inside
the surface's own extent on 5 of 9 sherds (s4: 27.6% of its surface is
radially outside the loop, s5: 26.6%, s6: 20.9%), which is what a
mis-closed loop looks like.

## Where the fix now lives (re-scoped)

| Change | Repo | Ticket |
|---|---|---|
| Extractor: trace the true outer boundary, not an interior loop | **preprocessing** | this one |
| Assembler: read `Breakline_1`; align normal convention with `robust_icp` | **structure-from-sherds-pp** | to be opened |
| Acceptance test for both | — | `gate_probe_b0.py <bundle>` |

**The assembly-side items are deliberately not actioned here.** If the
extractor's rim is corrected and the gate still fails, that is a finding
to hand back, not a thing to fix in this repo.

## Ticket 01's findings that reorder this work

- The extractor traces **one** wall face per sherd, arbitrarily
  (inner: 1, 5, 9; outer: 2, 3, 4, 6, 7, 8). 10/18 true mates are
  therefore inner-vs-outer and invisible to the gate — but the split is
  uninformative (10/18 non-mates are same-face too).
- On the 8 **same-face** true mates, normals agree at **0.92–1.00
  (6–23°)**, comfortably passing the gate. The opposed-normals reading
  from 2-9 was a *symptom* of the opposite-face assignment, not a second
  defect.
- Only **1/8** same-face mates has traces within 2 mm at ground truth
  (the rest 5–30 mm off). **Coverage is the dominant cause.**

**So: start with (2) seam coverage. It is necessary and insufficient on
its own — it can only help the 8 same-face pairs, of which 7 still miss
the seam. Then (1) both-faces, which is what unlocks the other 10.** Both
are needed; do them in that order, one at a time, so the gate number
attributes the credit.

**Needs-eye:** `visual-qa` pair showing the extracted breakline on both
sides of a real seam, correct-vs-attempt, witnessed by the conservator,
before any claim of improvement is recorded. Stage the desc with
`visual-qa-helper`; the gate number alone does not close this ticket.

## The change, in the order it should be tried

Ticket 01 picks one. The candidates, roughly in order of expected effect:

1. **Both-faces emission.** Where a fracture rim bounds both the inner
   and the outer surface cluster, emit the rim on both. Directly attacks
   the 1.7 mm / 129°-opposed failure. Candidate sites: segmentation
   (`clusteringOnNormals`, `edgeline_extraction.cpp` ~line 2118) and the
   boundary-detection path patched in `patches/juglet_boundary_radius.patch`.
2. **Seam coverage.** Extend/resample segments so they span the contact
   region rather than stopping short. Candidate site: sampling
   (`smoothAndSampleBreaklinesVer4UsingBSpline`, ~line 480) and segment
   assembly (~line 1632). Attacks the 0.2–30 mm misses.
3. **Ambiguity resolution.** If ticket 01 finds most points equidistant
   from both faces, neither 1 nor 2 is enough on its own — the extractor
   needs the wall-normal structure, not a distance rule. **Stop and
   report if this is the case**; it is a design question, not a tuning
   one.

## Discipline (learned the hard way this week)

- **One variable per experiment.** A bundle of changes that moves the
  number teaches nothing about which change did it.
- **Every change lands as a versioned patch** in `patches/`, named
  `juglet_edgeline_<what>.patch`, applied from the nested dir, **one hunk
  per file**. `patch` silently drops misordered hunks while exiting 0 —
  after every patch, verify the marker string is present in the built
  binary's output.
- **Never edit the Spartan checkout's tracked files by hand**; the
  pipeline there is versioned from this repo. Untracked data on Spartan
  is skip-worktree flagged — check `git ls-files -v | grep ^S` before a
  pull that touches those paths.
- **The acceptance test is the gate probe**, not a render and not a
  segment count:
  `python ../structure-from-sherds-pp/artifacts/juglet_run1/gate_probe_b0.py <bundle>`
- **A count is not a shape** (ticket 02's predecessor learned this: a
  bundle passed "200 points per file" while containing sub-millimetre
  dots). Verify extents in millimetres on every regenerated bundle.

## Acceptance

- Juglet true-mate pass rate at ground truth is **materially non-zero**
  and the number is quoted per pair, not as a total only.
- **Pot_A still 15/15** on the same probe. If not, the change is
  Juglet-only and must be labelled that way in the ticket and the
  intent question.
- One witnessed `visual-qa` look at the seam, staged correct-vs-attempt.
- **The remainder is recorded honestly:** which mates still fail, and
  whether wear, wall thickness, or both. "Fixed" is not available until
  the probe says so.
- If the probe passes but the assembler still finds nothing, **that is a
  finding, not a failure of this ticket** — hand it back to
  `../structure-from-sherds-pp` with the numbers attached.
