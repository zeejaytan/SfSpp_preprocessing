Status: ready-for-agent

# Ticket 239: full Pot D E2E on merged main (paper path, tree-built chain)

Answers: E2E proof for Pot D (29 pieces) on the chain main now builds itself.
Needs-eye: no.

## Goal
Run the full Pot D end-to-end on origin/main post-238: mesh + edge binaries built FROM THE TREE (verify md5s: mesh d72979aa, edge dc472b0e), fresh arm + ORIG control arm, 214 protocol.

## Boundary
- Fresh worktree of origin/main + fresh Spartan copy. Rebuild BOTH binaries in the container first; if either md5 differs from the reference, STOP and report (do not seat with mismatched binaries).
- Pot D = all 29 sherds. Fresh arm seats with our lanes; ORIG control arm validates the vehicle (214 precedent).
- Per-piece lane check per the swap rule (ledger Section B): verify slot mapping per piece before seating; blanket-apply nothing.
- Main worktree (user 204-edit) off limits except ticket commit + push of this ticket (lead does the landing).

## Constraints
- 214 numbers are the bar to match-or-beat (22 SWAP-clean + P03 agree + 6 MIXED: P12/P15/P16/P22/P25/P27). Report per-piece: which of the 6 MIXED resolve on the paper path, which persist, with lane scores (med/cov both lanes, slots, votes).
- No code changes, no commits to main. Evidence only: lanes, scores, seat renders, tallies.
- Spartan: pull --ff-only first, STOP and report on divergence.

## Acceptance
- Fresh arm tallies + ORIG control tallies + per-piece lane table (29 rows) + seat render eye-checked good. sacct COMPLETED for every job, binary md5s cited.

## Required evidence to report
Rebuilt binary md5s; job IDs + sacct states; per-piece lane scores; fresh/ORIG tallies; seat render path; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.
