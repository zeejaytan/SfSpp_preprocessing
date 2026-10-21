Status: ready-for-agent
Answers: E1

# Ticket 236: strip the 27-skip on paper-split-chain, prove Pot A without it

## Goal
Remove the superseded 27-skip (T24+T27 appendage-skip, +22 lines) in branch paper-split-chain, then prove Pot A still seats 8/8+15/15 on the paper path without it. If Pot A holds, the skip is proven dead code and stays out (user rule: superseded fixes are removed, not kept).

## Boundary
- Branch paper-split-chain ONLY, new worktree. Main, other branches, other worktrees untouched.
- Do NOT touch T21, T13, T23, or the old splitter -- their fate is decided at merge time, not here.
- Read-only on tickets 27/234/235/210; edit only this ticket (append Comments, Status results-in). No commits, no pushes.

## Constraints
- Locate the skip (+22 lines from ticket 27) and every call site it guards. Remove it branch-wide (the branch is the paper-arm vehicle; the old path in this branch is not under test).
- Rebuild (container build, cite binary md5). Same-source check for everything else.
- No-op proof first (cheap): lane diff skip-present vs stripped on P22 + P12 -- expect byte-identical lanes. If they differ, STOP and report (the skip was load-bearing somewhere).
- Then Pot A E2E on the paper path, 210 protocol (strict bar 8/8+15/15, same k/b, ORIG control must reproduce or void).

## Acceptance
- Pot A 8/8+15/15 strict on the paper path with NO skip code in the branch. sacct COMPLETED for every job; binary md5 cited.
- Verdict: SKIP-DEAD (Pot A holds -- removal stands) or SKIP-LIVE (Pot A drops -- report the delta, revert the removal, skip stays).
- No-op lane diff result either way.

## Required evidence to report
Job IDs + sacct states; binary md5; the lane-diff result; Pot A strict tallies; verdict in ticket Comments; Status results-in; self-contained completion message to the parent.

## Comments
