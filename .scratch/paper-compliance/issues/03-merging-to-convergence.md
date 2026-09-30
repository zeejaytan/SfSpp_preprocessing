# 03: Does merging-to-convergence change anything?

**Answers:** E1

**Blocked by:** nothing — code change + rerun, or laptop simulation first

**Status:** ready-for-agent — spike done 2026-09-30: YES as a code-path
fact. Single pass CAN miss chain merges (Step 1 tests all pairs against
pre-merge membership; `merged[j]` skips chain partners; Step 2 appends
without re-verification). Whether it DOES on real data is unmeasured —
hence the build spec below. No laptop simulation: saved intermediates
can't replay membership-dependent gates faithfully; instrument and rerun.

**Needs-eye:** none unless cluster assignments visibly change on a sherd
that matters at the gate.

## What to build

- Iterate Steps 1–2 to convergence (no merges in a full pass) with the
  existing criteria UNCHANGED (tuning 0.95/0.1/0.75/0.25 is a separate
  decision; bundling makes results unattributable).
- Pass cap (e.g. 10) + one log line per pass:
  `mergeClusters pass <P>: <N> merges, <M> clusters remain` — a
  pathological input cannot loop forever and the behavior is visible.
  Pass-2-with-N>0 settles YES-on-data; all later passes N=0 settles
  behaviorally-identical-to-convergence for that input.
- Per-pair detail rides on the existing pass/fail log lines, prefixed by
  pass number so pairs that only pass with merged membership visible can
  be grouped.
- No criterion values change in this ticket.

## Why this ticket exists

Paper: cluster merging "repeats until no further merges are possible."
Ours (`mergeClusters`, `mesh_processing_headless.cpp:1427-1552): single
pass over pairs (collect in Step 1, merge in Step 2), no convergence loop.
The outer `surfaceSegmentation` loop retries on *count* < 2 with looser
angle instead — a different condition that can mask under-merging by
loosening rather than by merging. Ticket 16 gap 7. Unmeasured effect.

## Research spike (do first)

1. Read `mergeClusters` fully (criteria: kNN pairs ≥3, patch-normal dot
   >0.95, boundary-curvature diff ≤0.1, inner-point verification 0.75/0.25)
   and answer: on Pot_A piece 2/3 (saved intermediates on disk), would a
   second pass merge anything the first pass left? Simulate the second pass
   on laptop from the saved cluster files if feasible; otherwise reason
   from the merge-pair logs of a rerun with extra logging.
2. If a second pass merges nothing anywhere on Pot_A: close with that
   measurement — single-pass is behaviorally identical to convergence here,
   and the deviation is cosmetic.
3. If it merges: judge by the per-stage coverage table (ticket 13's method)
   whether the merged clusters change any surface that matters, then decide
   the lane.

## What to build (only if the spike shows merges)

- Iterate Steps 1–2 to convergence (no merges in a full pass) with the
  existing criteria unchanged and a pass cap + log line per pass, so a
  pathological input cannot loop forever and the behavior is visible.
- No criterion values change in this ticket. Tuning 0.95/0.1/0.75/0.25 is
  a separate decision with its own measurement; bundling it here would
  make any result unattributable.

## Acceptance criteria

- [x] Spike: second-pass merges on real data — Pot_A gate half:
      `merge_conv` 15/15, per-pair IDENTICAL to `t14_patches` (header
      excepted); vote pattern unchanged (01 KEPT, 02 guard-KEPT, 03–08
      EXCHANGED). Gate-identical bounds the data question: whatever pass 2
      does on Pot_A, no surface that matters changes. Pass-count lines
      pending from the Juglet rerun (mesh log now persisted to the tree).
- [x] Lane declared: cosmetic-close on Pot_A (no surface that matters
      changes); Juglet rerun decides whether any pair moves there.
- [x] Implemented: criteria unchanged, cap 10, per-pass log line. Guard
      audit re-run (vote pattern unchanged — the clusters the vote sees
      are stable).
- [ ] Authors' arm in every comparison (pota_orig 15/15 on record from
      ticket 17; re-confirm alongside the Juglet scoring)
- [ ] Juglet gate re-measured per pair (rerun in flight 2026-09-30)
