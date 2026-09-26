# 02: Dedupe the boundary cloud before ordering

**What to build:** boundary points that sit almost on top of each other
stop derailing the edge-line traversal, so that a sherd with an eroded,
duplicate-heavy boundary still yields one continuous trace rather than
fragments.

This is the smallest change that addresses a failure we have measured
directly. Making the traversal take smaller steps (an earlier attempt,
since reverted) collapsed traces to a quarter of a millimetre, because
with a small neighbourhood the walk's next candidate was almost always
another point from the same tight clump. The clump is the problem, not
the step size.

**Answers:** E1

**Blocked by:** 01 (the pinned test is what makes this falsifiable)

**Status:** ready-for-agent

**Needs-eye:** none yet. The end-to-end render lands in 07; this ticket's
evidence is the seam test and the acceptance numbers.

- [ ] Boundary points closer together than the surface's own point
      spacing are collapsed before ordering, and the spacing used is
      derived from the cloud rather than hard-coded
- [ ] The pinned test from 01 turns green: a synthetic rim carrying a
      clump of near-duplicates is ordered as one loop instead of stalling
- [ ] The number of points removed is reported in the log, so a run that
      collapses most of its boundary is visible rather than silent
- [ ] A clean boundary with no duplicates is passed through unchanged —
      demonstrated by a test, not asserted
- [ ] Change is one variable: the acceptance probe is run before and
      after, and both numbers are recorded in this ticket

## Note

Do not retune the traversal neighbourhood in this ticket. One variable
per experiment: if this and 03 are bundled, and the acceptance number
improves, we will not know which one did it.
