# 01: Establish a C++ test seam for the edge-line stage

**What to build:** a runnable test target for the edge-line stage, so
that every later change to it can be checked without a full pipeline
run. Today the repository has no CTest wiring and no unit tests at all;
the first test written must pin the behaviour we have actually measured,
so that later tickets change it deliberately rather than accidentally.

The tests run inside the build container on Spartan. The laptop cannot
build this code (no PCL/Eigen), which is why this seam lives on the
cluster and why the end-to-end acceptance probe must stay on the laptop.

**Answers:** E1

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

**Needs-eye:** none — this ticket produces a test target, not a
geometry claim.

- [ ] A test target is registered with CTest and runs green from a single
      documented command, inside the container, on Spartan
- [ ] The first test pins today's measured behaviour on a synthetic
      boundary cloud: it fails in a way that names the defect (a stalled
      or derailed traversal producing internal jumps far larger than the
      median step), rather than passing because the defect is not yet
      characterised
- [ ] The test target builds from the same source as the pipeline, so a
      test can never pass against different code than production uses
- [ ] Running the tests is one command, documented in the repository, and
      its output is legible enough that a failure names the property that
      broke
- [ ] No test asserts on log text, on point counts alone, or on the
      identity of an internal function — only on output geometry

## Note

This ticket deliberately pins a *known-bad* behaviour. That is what makes
the later tickets falsifiable: if 02 or 03 cannot turn the pinned test
green, the change did not work, and no cluster run is needed to learn
that.
