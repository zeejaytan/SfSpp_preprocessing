# 282 — The build must say which source it compiled

Answers: E1
Status: ready-for-agent
Working in: build.sh, CMakeLists.txt area (no C++ semantics)
Needs-eye: no

## What happened

Ticket 280's worker ran build.sh with the nurbs target and got a binary built from
**original_nurbs_preprocessing/edgeline_extraction_headless.cpp** — a pre-247 duplicate
(md5_lf 3273d87ee09fd2e567cbeaddfa824890, 3721 lines, STOP-267=0, FULL-263=0, VOTE-247=0) —
while the live program is the root source that CMakeLists.txt:38 builds (md5_lf
8264da3647d048e67d983edfe810b59d, 3725 lines). The duplicate is a different program: no
no-discard walk, no stop rule, no vote-order host.

Nothing was lost — the worker noticed and rebuilt the live root project — but the failure mode
is the dangerous kind: a run that produces a full set of surfaces and lines, exits 0, and
scores badly for reasons that have nothing to do with the method. It is the same shape as
ticket 277 (missing axis file silently keeping size order).

## What to build

1. **Every build prints what it compiled**: absolute source path, line count and md5 of each
   compiled translation unit that matters (at minimum the two headless .cpp files), plus the
   binary's md5. This is a one-line-per-file banner, not a doc.
2. **The legacy duplicate is refused by default.** Building it must require an explicit flag
   that names the path, and the flag's help text must say why (ticket 280). If the duplicate
   is dead, prefer deleting it and letting git history hold it — check first whether anything
   references it.
3. **A post-build sanity check**: the fresh binary must contain the shipped-default markers
   ([STOP-267], [FULL-263], [VOTE-247]). If any is missing, the build fails instead of
   reporting success. That single check would have caught this trap on the spot.

## Acceptance

- A build of the live source prints source paths, line counts, source md5s and the binary md5.
- The legacy target refuses to build without an explicit opt-in, naming the source it would
  have compiled.
- A binary missing any of the three markers fails the build.
- The six guard lanes of ticket 271 still reproduce under the normal build path.

## Evidence to report

- the banner as printed, verbatim
- the refusal as printed, verbatim
- the marker check firing on a deliberately wrong binary (build the duplicate behind the
  opt-in flag to produce one)
- confirmation that nothing else in the repo references the duplicate, or what does
