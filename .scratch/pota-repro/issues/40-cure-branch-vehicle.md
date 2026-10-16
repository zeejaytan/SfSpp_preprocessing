# 40: Cure-branch vehicle — 3 hunks onto upstream base, repo-built 8/8+15/15

**What to deliver:** a clean, traceable cure branch that reproduces ticket-36 numbers from checkout.

**Answers:** E1

**Blocked by:** 38-land-cure-set (vehicle ruling: cure-tree recipe).

**Status:** ready-for-agent

**Starting position (bar ruling 2026-10-16: cure-tree recipe).** Ticket 36 proved upstream@9195c01 + 3 staged hunks = 8/8+15/15 both arms. Ticket 38 proved the fork + same 3 hunks = fresh 7/8+10/15 in 3/3 runs (ORIG wobbles 7/8+7/15 ↔ 8/8+13/15 on identical pruned counts — beam variance, same binary). Remaining fork↔cure delta (refinement weighting et al.) is NOT chased piecemeal per the ruling. So the B–J vehicle is a cure branch, not the fork.

**Steps:**
1. In the `structure-from-sherds-pp` laptop clone, create branch `cure-potA` from upstream @9195c01 (add upstream remote if absent; DO NOT touch fork main — it stays at b35905b). Apply the 3 hunks (cherry-pick 9f432bc/89f771c/b35905b if contexts apply, else apply by hand from the ticket-28/abl2 record) — final diff vs 9195c01 must be exactly those 3 one-liners. Push the branch.
2. REPO-BUILT REPRODUCE on Spartan from fresh clones (prep @ f1fd6b4 + cure branch, zero patches): gate 15/15, then E2E k=5/b=3 shim both arms with LINK-SHIM-OK + DRIVER-SHIM-OK asserts, non-empty snapshots. Expect ticket-36 numbers: ORIG 8/8+15/15, fresh 8/8+15/15, pruned 124/63 + 420/119.
3. REPEATS (variance is proven — one run proves nothing): minimum TWO full E2E runs; both must hit 8/8+15/15 both arms. If either misses, stop and report (do not chase — hand back to lead).
4. Strict tables recorded as DIAGNOSTIC only. Seating render both arms (eye-check). sacct-direct polling. COMMIT NOTHING except the cure branch. Comments-only ticket edits.

**Acceptance:** cure branch pushed (diff = 3 one-liners vs upstream); 2/2 E2E runs 8/8+15/15 both arms with valid ORIG controls; renders; job IDs + sacct states.

**Successor:** ticket 39 (B–J E2E on this vehicle, repeats per pot).
