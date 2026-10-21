Status: ready-for-agent

# Ticket 238: restore working root-edge source to main

Answers: E1 (Pot A/E2E chain needs tree-built edge lanes).
Needs-eye: no.

## Goal
Make main's own tree build working edge lanes again. The good reference binary dc472b0e was built from root edgeline_extraction_headless.cpp at exp-218 commit 885f433 (file md5 89ab05b1, verified by lead); main's current file (md5 ce76a872, 154-era content) builds STUB lanes (proven 236/237). Restore the good source, verify, commit.

## Boundary
- Exactly 1 file: the ROOT edgeline_extraction_headless.cpp (not the vendored subdir copy, not mesh, not old path, not flags).
- Take the file content at commit 885f433 (branch exp-218, reachable on origin). If its ifdef defaults differ from plain-old behavior, keep default = old behavior (all arms off) -- verify by reading the flags.
- Fresh worktree + fresh Spartan copy. Main worktree (user 204-edit) off limits except final commit + push.

## Constraints
- Rebuild the root edge binary in the container. Verify FIRST against dc472b0e: binary md5 match if the build is deterministic, else lane-diff on P22+P12 (must be full lanes: P22 ~176/177-class, P12 both lanes; stubs = FAIL, stop and report).
- Then Pot A short re-proof on the paper path (fresh arm minimum; 236 numbers are the bar: 8/8+15/15, strict 8/8). Drop => STOP, no push.
- Commit message states: which source restored (885f433/md5), why (main's file built stubs), what verified it.

## Acceptance
- origin/main root edge file md5 = 89ab05b1. Tree-built edge binary yields full lanes (not stubs). Pot A holds. No other files touched.

## Required evidence to report
Restored file md5; edge binary md5 (+ dc472b0e comparison); lane counts P22/P12; Pot A tallies; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.
