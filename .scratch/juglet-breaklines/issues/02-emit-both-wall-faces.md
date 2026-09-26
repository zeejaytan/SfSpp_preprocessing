# 02: Make the extractor emit both wall faces, and cover the seam

**What to build:** the smallest change to `edgeline_extraction.cpp` that
makes Juglet breaklines pass a join gate, **one variable at a time**,
starting with the cause ticket 01 identified as dominant.

**Answers:** E1

**Blocked by:** 01 (the measurement decides which change to make first —
do not start this before 01 reports)

**Status:** needs-info

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
