Status: open

# Ticket 277: the axis target cannot compile — and no binary has ever existed for it

Answers: none.
Needs-eye: no.

## Goal

Decide what happens to the axis-of-symmetry stage, now that `build.sh --target axis` proved it does
not compile. Not a build-script question: the generated project file is correct and configures cleanly,
and then the source fails.

## What was found (job 33733113, worktree sfs_preprocessing.wt/buildsh-20261024)

- `axis_extraction_cpp.cpp:21: error: 'Vector6d' in namespace 'Eigen' does not name a type`, plus the
  same identifier at :159 and :193 — 11 occurrences, all introduced by `ff40fc9` ("Local fixes: MATLAB
  bugs, headless build, path corrections, SFS format").
- Eigen's fixed-size typedefs stop at 4 (`Vector4d`); there is no `Vector6d`. The code wants
  "direction(3) + position(3)".
- `AxisExtractionHeadless` is in **no** tracked `CMakeLists.txt`: `3bd5c10` added the target,
  `e34db86` removed it again ("axis extraction runs via MATLAB"), the source file stayed behind.
- No `AxisExtractionHeadless` binary exists in any build directory on the cluster, so this target has
  never compiled there — the failure is not new, it was just invisible while the legacy scripts still
  pointed at a target that had been deleted.

## Why it matters

A dead target inside a tool people are asked to use is a trap: `build.sh --target axis` accepts the
flag, does everything right, and then dies in a header-less type. Worse is the alternative reading —
that the axis stage is half-portable and one typedef from working — because the C++ in that file has
never been executed by anyone.

## Decision (2026-10-24)

Keep the target in the interface and make it fail loudly. `build.sh --target axis` now refuses at
preflight, before it looks for the image or runs cmake: it prints why the stage cannot compile,
names this ticket's path, and exits **4** — a code a caller can tell apart from a compile failure
(`2`, say). Nothing is built, the source, the tracked `CMakeLists.txt` and the other targets are
untouched, and `--dry-run` is refused the same way. The refusal is one small function in
`build.sh` beside the target validation, with a comment naming this ticket, so a future porter
knows exactly what to delete. This ticket stays open and is the record of the gap.

## Done when

Either

- (a) the binary builds and runs on one named pot, with its output put beside the MATLAB result, so we
  can say whether the port was ever faithful; or
- (b) `build.sh` no longer offers the target, `docs/notes/build.md` says why in one line, and the source
  file is marked as an unported experiment in its own header.

Do not choose (a) without a reason to want the axis stage: the pipeline's current readers take the axis
from the MATLAB path, and resurrecting a port nobody has run is how a second, silently different answer
gets born.

## Evidence

- `/data/gpfs/projects/punim2657/sfs_preprocessing.wt/buildsh-run/logs/slurm-33733113.out` (the three
  invocations, exit 0 / 0 / 2).
- `docs/notes/build.md` — where the 33 legacy scripts went, and the target list build.sh now offers.
