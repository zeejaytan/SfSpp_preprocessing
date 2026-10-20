# Port ledger-D default walk chain onto pristine-dchain (with F/G boundaries)

GOAL: PRISTINE BASE, PROVEN CHAIN. Re-apply the ledger-D default walk chain
(D0 densify, D1 split-by-surface, D2 gated thin, D3 recovery) onto the
pristine-dchain base, honouring the F and G boundaries, so the next E2E runs
on author behaviour plus the proven chain and nothing else.

**Answers:** E1

**Blocked by:** none (base surgery landed: 3095064 + 0da8891 edgeline + 6da985d mesh).

**Status:** done

**Starting position:** base branch `pristine-dchain` @ 6da985d (= upstream
3095064 + edgeline B1-B10 revert + mesh M1/M2/M4/M5/M6/boundary/dyn-reg
revert; keeps are headless includes, CGAL::IO paths, argv/env/single-file
main, ASCII PLY, prints, M8 guards). Donor implementation is fork `main`
(lane tickets 143/144/175/175/185, proven E2E 194/195/196). Ledger:
`.scratch/pota-repro/FIXES-LEDGER.md` sections D, F, G.

**Rules:** new worktree + new branch `dchain-port` off 6da985d (never touch
the main worktree -- it holds the user's uncommitted 204 edit -- nor
`.scratch/.wt-pristine-dchain`); MATLAB axes as-is (user decision: do not
port, replace, or re-tune axis computation); one chain step per commit;
COMMIT the branch and PUSH `origin dchain-port`; Comments-only ticket edits
(append ## Comments worker-date + flip Status; checkboxes stay with lead).

Port, in order (ledger D):
- [ ] D0 true densify (143): mesh-sampled ladder, 10->0/0->21->1 rung.
      Midpoints add zero true info (111/146) -- FORBIDDEN, do not port any
      midpoint synthesis even if the donor has it.
- [ ] D1 split by surface (175): separate face clouds PRE-pooling, walk each
      face, file both slots. True-face walk must beat the union walk.
- [ ] D2 thin + verbatim walk (185): ~2-wide strip to centreline, uniform
      1.8mm resample, walk_m144 UNCHANGED. GATED by F: apply ONLY where the
      179-census doubling diagnosis fires; clean singles pass through
      untouched (194/196 negative: blanket thin collapses seating 8/8->4/8).
- [ ] D3 recovery (144): state trigger (admitted-majority + coverage-payoff)
      through the 145/186 lineage behaviour.
- [ ] G throughout (204/C03): NEVER pool faces before splitting -- the
      geometric wall-facing re-split lets Bl_1 into Bl_0's bag (med 0.86mm
      vs disjoint 15.88). Split-first everywhere.

Acceptance (all required to land):
- [ ] Each step verified against its ledger numbers on the donor's own gate
      piece (D0: 32/32 on-arc, junk 0; D2: 204 dots / closure 1.79 /
      D-tokens 2 / rim-med 0.64; D1: both walks single laps, true-face wins;
      D3: 322/310, gate 3.9736, uncovered 0) -- same inputs, same numbers.
- [ ] Headless mesh main still builds and its argv/env/single-file modes work
      (do not break the 6da985d keeps).
- [ ] Full E2E seating is NOT this ticket's gate (follow-up ticket runs the
      control); but every step must be E2E-shaped: file both slots, keep rim
      truth medians computable.

## Comments (worker, 2026-10-20 -- PORT LANDED, 4 commits on origin/dchain-port)

**Branch:** `dchain-port` off pristine-dchain@6da985d (pushed to origin). Worktree .scratch/.wt-dchain-port. Commits: 5363dfc D0, d0da2f1 D1, 944eb2e D2, eb33ef3 D3. Diffstat vs 6da985d: 93 files, +2562, ALL under .scratch/pota1* (scripts + frozen inputs + re-run logs/npy). Zero C++/CMake/MATLAB changes -- pristine base untouched by construction.

**Per-step verification (donor gate piece C01, laptop numpy re-runs, every log/npy byte-identical to donor):**
- D0 (143 ladder): pool-A 10 admitted 10/10 on-arc junk 0; Rung-S 0/0; X2 21; X4 1 (32/32 on-arc, junk 0); full-314 greedy 140/314 med 3.9851 uncovered 91 spans [(115,205)]. Midpoints forbidden honored (grids snapped to S0 verts only).
- D1 (175 split): parent labels inner 212/outer 277/fold 264; TRUE=inner+fold 476 (correct-notion 211/211 med-seat 0.755) vs OUTER 277. Walks: TRUE spread0 439 dots 211/211 med 0.95; OUTER medoid 202 dots cov 78/211 med 2.15 -- true-face wins, both single laps. Slots filed (slot0 439/slot1 202, E2E-shaped).
- D2 (185 v3 + walk_m144): N1=204, closure 1.79, D-tokens 2, rim-med 0.6421 CHECK-ONLY. F honored: thin applied ONLY here; indication = C01 doubling diagnosis (179 s2: walk arc 691mm vs author 380 = 1.82x, 34 D-tokens), same gated class as 190/193; 194/196 blanket-thin collapse is the counter-precedent.
- D3 (144): T144 fired pre-run (24/32 majority + payoff +2/+18, structural, separates 282-FIRE from 116-stuck-SUPPRESS). M144: 322 seqlen, med 3.9736, uncovered 0, maxstep 22.8, 0 steps>25, 0>=40 -- BAR ALL-HOLD.

**Deliberately NOT ported:** p204_dchain.py as written -- it pools F0+F1 then geometrically re-splits by wall-facing, the exact pattern boundary G rejects (C03 Bl_1 into Bl_0's bag, med 0.86 vs disjoint 15.88). Ported instead: pool-free split-first composition (D1 slots walked separately, never pooled). No donor contradiction with F/G found beyond this already-flagged case.

**Not done (blocked, needs follow-up):** headless mesh main compile -- no cmake/g++/PCL/CGAL anywhere on the laptop (VS2022 Community present but no PCL/CGAL), and C++ builds belong on Spartan per AGENTS.md. State preserved: zero C++ files changed in all 4 commits. Suggest login-node build check as part of the E2E follow-up. Full E2E seating out of scope per ticket.

Report back: branch + commit hashes, per-step verification numbers
(input/got vs ledger), diffstat vs 6da985d, anything in the donor you
DELIBERATELY did not port and why, and any place the donor contradicts F/G.

## Comments (lead, 2026-10-20 -- ACCEPTED, verdict PASS with standing gap)

Independently verified: 4 commits on origin/dchain-port (5363dfc/d0da2f1/944eb2e/eb33ef3);
diffstat vs 6da985d is 93 files +2562 insertions-only, ALL under .scratch/pota1*
(zero C++/CMake/MATLAB -- build state identical to 6da985d by construction).
Read the committed gate logs myself: D2 N1=204 closure 1.79 D-tokens 2 rim-med 0.6421
on all 6 seeds; D3 uncovered=0 max-DO 4.95 -- both match the ledger and the worker report.
G-rejection (p204 pooling) is the honest composition and is recorded, not hidden.
Standing gap (unchanged): no Spartan compile of the headless mesh main and no E2E seating --
both belong to the E2E follow-up, which also owns the live-root-copy revert question
(review 2026-10-20: live root binaries still carry fork behaviour; dchain-port rebases cleanly
since it touches disjoint paths).
