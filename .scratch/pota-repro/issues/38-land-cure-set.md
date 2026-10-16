# 38: Land the cure set — assembly commits + repo-built reproduce

**What to deliver:** the cure as landed commits, and a repo-built binary proving it.

**Answers:** E1

**Blocked by:** 36-cure-rebuild (bar ruling: paper's bar stands).

**Status:** ready-for-agent

**Starting position:** the pipeline half is landed (T13 b0083ae, T21 f39b1b0, T23 f08d960, T24+T27 48ca2c0 — verify present by `git log`). The assembly half exists only as uncommitted hunks + scratch sources: P22FIX (feature_matching.cpp:1989, drop `|| overlap_`), P22FIX2 (ranking_system.cpp:1838 CheckGraph site2 50→150), C2-restore (pairwise axis gate 0.610→true-upstream 0.436 — ac64c3f's "upstream 0.610" claim proven false, abl2 causal ORIG 0/8→8/8).

**Steps:**
1. AUDIT FIRST: `git status` + `git diff` in the `structure-from-sherds-pp` laptop clone. Only the two known one-liners may be present-controls; any other modification stops the ticket (report, do not commit around it). Verify each hunk byte-matches the proven version (P22FIX/P22FIX2 per ticket-28 verification; C2-restore = abl2 line).
2. Commit as THREE separate commits, one per hunk, each message carrying the why: symptom → proof (job IDs + tallies) → decision. Push to origin main. (Precedent: preprocessing-side landing commits.)
3. REPO-BUILT REPRODUCE (closes the ticket-28 provenance gap): fresh pull of both repos on Spartan, build from landed commits only, run the p28 wall-only bundle path end to end — gate 15/15, then E2E k=5/b=3 shim both arms: ORIG 8/8+15/15 valid control, fresh 8/8+15/15. Record strict tables as DIAGNOSTIC (expected ~6/15 ORIG, ~12/15 fresh per ticket 36 — a large deviation fails the run).
4. Seating render of both arms (eye-check), job IDs + sacct states, Comments-only edits here.

**Acceptance:** three assembly commits pushed with why-messages; repo-built (no scratch sources) gate 15/15 + E2E binary 8/8+15/15 both arms; strict recorded.

**Successor:** ticket 39 (B–J E2E).
