# 222 - Gap-gated stopping rule (user rule m03059, 221 follow-up)

Status: ready-for-agent
Answers: none (splitter-method trial; context 220/221, rulers 214/217)

## Goal
Test the user's rule: keep tightening until the FIRST step with two big balanced faces AND a clean gap between them. Lead-measured on P12@10: S0-S1 min gap = 0.00 at [10.8, 14.3, 465.0] (bridge; rest of rim median ~9.5mm apart) -- R2 stopped while a bridge still joined the faces on one side, both lips pooled, walk crossed (user m03059; amends 221 "splitting RIGHT" to "split leaves a bridge"). Question: does a 2-big-balanced AND gap-clean step exist before shattering, per piece?

## Boundary (worker: read-only except where named)
- PREFER analysis-only: the pota221_ladder tree (Spartan sfs-fix-221) already holds thr_* surfaces per threshold per piece -- compute S0<->S1 min-gap + gap-cleanliness per step from EXISTING outputs. New mesh runs only if a step's surfaces are missing/poisoned (trap 1: single-cluster files repeat the previous piece -- exclude by md5).
- If code is touched (gap metric inside binary): branch exp-222 off origin/exp-221, unmerged. Otherwise no branch needed -- say so.
- MAY run: edge + score vs author lanes at the gap-clean stop IF one is found (bar med<2, cov>=90%, slots per piece, 209 pattern). Spartan work in sfs-fix-221 tree or fresh copy; pull --ff-only; STOP on divergence.
- Do NOT touch: main worktree (user 204-edit live), .wt-*, other branches, stashes, bundles, other tickets (append Comments here only). ORIG-free (author lanes as ruler only).

## Constraints
- Gap-clean definition is the worker's first deliverable (lead suggestion: min S0-S1 separation > wall-thickness scale, e.g. >=2mm, AND/OR overlap fraction ~0%; must also hold P16/P01 controls without breaking their current good splits).
- R1 balance conditions frozen from 220 (top2>=70%, third<=8%, 2nd/1st>=0.5). R3 = first threshold satisfying R1 AND gap-clean. Record R3 per piece (or NONE).
- 100% dot accounting where recomputed; reuse 221 numbers where untouched (cite, don't redo).
- Report channel = this ticket's Comments + completion notice (no send_message downward).

## Acceptance (lead judges; numbers + cites + paths)
- Per piece (P12/P15 primary, P16/P01 controls): threshold -> (top2, third, bal, min-gap, gap-clean?) table; R3 stop or NONE with reason (shatters first / never balances / never separates).
- Stretch (only if R3 found): lane scores at R3 vs bar; Bl0 unharmed?
- Verdict: does the user's rule exist on each piece? If NONE anywhere before shattering, splitter needs bridge-cutting -- report that, propose nothing ungrounded.

## Required evidence to report
- Gap tables per piece (with step surfaces cited), R3 stops or NONE-reasons, stretch scores if run, sacct State/ExitCode for any jobs, branch (only if code touched, unmerged).
