# E2E on the pristine line: Spartan compile + full Pot A seating

GOAL: PROVE THE LINE. Compile both headless mains on Spartan and run the full
Pot A chain (mesh -> breaklines -> MATLAB axes -> D0-D3 walks -> assembly seating)
on the pristine line, reporting numbers against the fork-era ledger.

**Answers:** E1

**Blocked by:** none. Base is `pristine` (currently b1ed4d1 = 6da985d base +
7ffede4/c617fd8 live reverts + d0c0304 vendored-dir deletion + b1ed4d1 D-evidence
merge). D-chain scripts live under .scratch/pota1* on this line.

**Status:** ready-for-agent

## Build first (login node, cheap)

Configure + build EdgeLineExtractionHeadless and MeshPreprocessingHeadless from
the ROOT CMakeLists on the Spartan checkout after `git pull`. No laptop toolchain
exists, so this is the first compile of the reverted sources. Fix ONLY harness-level
breakage (missing includes, CGAL::IO paths); any behaviour change needs a new ticket.

## Then the chain (compute node / sbatch, standing sign-off applies)

Run the D0-D3 chain per the 206 ticket evidence, then assembly seating per the
assembly repo's pristine scorer (origin/main b56bc80, proven 8/8+15/15 on ORIG).
MATLAB axes as-is per standing decision.

## Carried risks (from 207 -- watch, do not pre-fix)

1. BUGFIX#1 call removed per spec: if E2E shows empty fracture outputs, open a
   dedicated ticket (do not re-add inside this run).
2. breaklinesDir create_directories stays disabled: pre-create the dir in the
   container/image if the run fails on a missing dir.
3. Guide .mds + patches/SOURCE_ANCHOR.md describe the deleted vendored layout:
   do not follow them; write the fresh layout notes into this ticket instead.

## Acceptance

1. Both headless mains compile clean on Spartan (warnings OK, errors none).
2. Full Pot A chain completes; per-step numbers filed next to the 206 evidence.
3. Seating reported as: fragments seated x/8, joins true y/15, with the render
   for the eye (visual-qa per workspace rules) -- numbers alone prove nothing.
4. Comparison vs fork-era ledger E2E (194/195/196) stated plainly: same, better,
   or worse -- and if worse, which of the three claims (method failed / ruler
   broken / reference wrong) is being made, with the render as evidence.

Report back: build log tail, per-step numbers, seating numbers + render paths,
ledger comparison, and any new ticket opened for surprises.

## Comments (worker, 2026-10-20 -- STOPPED at the Spartan gate, nothing built or run)

Branch: `e2e-pristine` cut from origin/pristine@b1ed4d1 (fetch first, base as
specified). Worktree: .scratch/.wt-e2e-pristine (new; main worktree, other
worktrees, other branches untouched). Worktree is clean at b1ed4d1. No commits
on e2e-pristine (no evidence produced), nothing pushed. This ticket file (208) is
not on the pristine line -- edited in place in the main worktree, uncommitted.

Spartan gate (per ticket: pull --ff-only, STOP on divergence, no force-pull):
- Checkout is /data/gpfs/projects/punim2657/sfs_preprocessing on `main` @
  a5d9ccd (cure-branch era), behind origin/main (157 before fetch, 253 after).
- `git pull --ff-only` REFUSED (exit 1), working tree unchanged @ a5d9ccd:
  "error: Your local changes to the following files would be overwritten by
  merge: edgeline_extraction_headless.cpp
  original_nurbs_preprocessing/edgeline_extraction_headless.cpp ... Aborting".
  Fetch itself succeeded (origin/main now 3993a06; origin/dchain-port,
  pristine-dchain, pristine-dchain-live newly visible there).
- The blocking local modification is live research state, not throwaway: the
  dirty hunk in original_nurbs_preprocessing/edgeline_extraction_headless.cpp
  is the T24+T27 cure logic (skip ticket-14 patch-rim append for Pot_A pieces
  2/3/4/5, +22 lines). Overwriting it would destroy the behaviour the current
  Spartan pipeline runs on. Untracked Juglet_* outputs also present, and the
  165 skip-worktree data files are live assembly inputs per AGENTS.md.
- Upstream origin/main commit 48ca2c0 touches the same dirty file, so the
  refusal is structural, not transient -- a later retry without resolving the
  Spartan main state will fail identically.

NOT done (all behind the gate): login-node configure+build of both headless
mains; Pot A D0-D3 chain; assembly seating vs pristine scorer (b56bc80);
sacct/State/ExitCode records; renders; fresh layout notes; ledger comparison.
No new tickets opened (the ticket-207 carried risks never materialised into
runs; no surprises observed, only the gate itself).

Status deliberately NOT flipped to results-in: no results exist. Lead decision
needed: quiesce/resolve the Spartan main checkout (commit or relocate the
T24/T27 live state + Juglet outputs) OR designate an alternate Spartan
checkout/worktree where e2e-pristine can build and run without disturbing the
live main-tree pipeline inputs, then re-dispatch this ticket.
