Status: ready-for-agent

# Ticket 245: merge the 244 density restore to main

Answers: whether the restored-density default is live on main with a verified binary.
Needs-eye: no.

## Goal
Apply artifacts/pota244/restore244.diff to origin/main, rebuild, verify the binary, spot-check P03, commit + push.

## Boundary
- Fresh worktree of origin/main + fresh Spartan copy. The ONLY source change: apply C:/PR/SfSpp_preprocessing/artifacts/pota244/restore244.diff (21+/7-, downsamplePointCloud + call site). No other edits.
- User decision 2026-10-22: keep the restore; sample-dataset match (48fb588 motive) is knowingly broken ~3.4x on big pieces. Record this decision in the commit message.
- Main worktree (user 204-edit) off limits except ticket commit+push (lead lands). No other pieces touched.

## Constraints
- Spartan: pull --ff-only first, STOP and report on divergence.
- Standing rule: source change => rebuild + verify binary. Same build node as 244 for md5 comparison (expect b8eb37599bb222764f789eabb5dd798c BYTE-IDENTICAL: main source @a41fa6a == 244 base @8f27cf0 plus ticket-only commits; identical-or-explained).
- Spot-check: P03 mesh + dc472b0e trace reproduces 244 (S0 ~107k, cut ~2396, Bl0 0.71/100-class). Full verdict: PASS only if identical-or-explained AND spot-check class holds.

## Acceptance
- main contains the restore; rebuilt mesh binary md5 cited (identical to b8eb3759 or explained); P03 spot-check numbers; sacct COMPLETED; commit pushed.

## Required evidence to report
Applied diff stat; build job + binary md5; P03 spot numbers; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.
