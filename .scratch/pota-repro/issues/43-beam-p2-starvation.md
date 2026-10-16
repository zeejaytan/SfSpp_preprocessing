# 43: Beam p2-starvation (Pot B) — why fitting candidates never seat

**What to deliver:** p2 seated, or the beam mechanism that stops it, named with numbers.

**Answers:** E1

**Blocked by:** 42-potb-rim-fix (rims fit; blocker is beam-side).

**Status:** results-in — mechanism delivered, p2 NOT seated by any arm

## Comments (worker, 2026-10-17, 09:50 AEDT) — final: LENNORM does not replicate; noise source hunt stopped

LEN3 (33236483, COMPLETED 0:0, same binary/node/env x3): L1 = 5/9 {1,3,6,7,9} (new edge 6-9, loses 1-4), L2 = L3 = 3/9+1/15 {1,3,7}. Same-binary split → LENNORM reroutes seatings but seats nothing replicably. L1/L2 LCS dumps prove the noise enters UPSTREAM of the beam: identical integer inliers, but `score`/`axisang` differ last-bit run-to-run (e.g. 0.650586 vs 0.650592).
THREADS probe (33236761, COMPLETED 0:0, P43_THREADS=1 single-threaded x3): T1 {1,3,4}, T2/T3 {1,3,4,7} — still split. NOT OMP/Eigen scheduling, NOT node (bm134 gave both 4/9 and 3/9), NOT binary (same-binary splits). Prime suspect remaining: uninitialized read feeding the score math (ASLR-varying garbage). Stopped here: the exact variable doesn't change the ticket's answer.
NET ACROSS 10 B-FRESH ARMS: p2 = 0 ok pairs every time (deterministic starvation). BASE mode = pieces {1,3,4,7} + 3 undirected edges {1-3, 1-4, 3-7} (tally prints 2/15 via the k/2 truncation). ORDER/WIDTH point estimates sit inside the noise band (no effect shown, none replicable either way). LENNORM twice seated a 5th piece via different edges (6-9 in L1; unknown 5th in 33219242) but never twice the same way, never p2. NO RENDER (nothing replicable to eye-check; will not render a lucky run). Controls green in all 4 full runs (B ORIG 9/9+15/15, A 8/8+15/15).
RECOMMENDED NEXT (for session, not this ticket): (a) prep-side exp4 lip-component — grow p2's true overlap, the only variable the beam demonstrably rewards; (b) non-LCS scoring term — axisang separates p2's surviving true edges (0.077, 0.149) from most false ones (up to 0.65); (c) determinism recipe for future arm comparisons still open (uninit hunt or valgrind, est. half day). All run dirs: `/data/gpfs/projects/punim2657/sfs_main/pota43_run_{33218437,33218721,33218722,33219242,33232934,33236170,33236370,33236483,33236761}/`. Scratch vehicle diff (uncommitted, DO NOT COMMIT without session review): `class/ranking_system.{cpp,h}` (P43_ORDER rotation + LENNORM norm fields/sort), `class/data_structure.{cpp,h}` (P43-VERBOSE pair print + P43_THREADS), plus untracked sbatch files and `shim_p43.cpp` in `/data/gpfs/projects/punim2657/pota43_repro/`.

**Working in:** scratch vehicle only — `/data/gpfs/projects/punim2657/pota43_repro/` (`asm/` = `cp -r` of cure-potA @ bffefb6, HEAD verified bffefb6 + clean; fork main @ b35905b untouched). Ticket-39/42 run dirs used read-only.

## Comments (worker, 2026-10-17)

**Question asked:** why does the beam starve p2 on fresh Pot-B rims (E2E 4/9+2/15) while ORIG seats 9/9+15/15?

**Scoring decomposition (exact, from P43-LCS Nhi Trinh in BASE job 33218437).** SortRoot node score = tanh(breakline_cols/100) x SUM(inlier) over touching LCS edges. Volume term is innocent: tanh(149/100)=0.903 (fresh p2) vs 0.905 (ORIG p2). The 731 -> 93 collapse (7.9x) = edge count 19 -> 8 (2.4x) x mean inlier 42.5 -> 13.0 (3.3x). Worse: GT-true pair p2-p1 has FIVE ORIG edges (inliers up to 78) but ZERO fresh edges — nothing to rank. Surviving true edges p2-p4 (inlier 16, size 7) and p2-p8 (22, size 11) rank ~40th+ globally (fresh top-10: 45-65), permanently below the per-state top-3 expansion frontier. Root order then buries p2 in the weakest state (state2 = roots 9,1,2).

**Arms (one variable each; every run carries B ORIG + A ORIG/FRESH controls in the same job):**

| arm | job (sacct COMPLETED 0:0) | B fresh | controls |
|---|---|---|---|
| BASE | 33218437 | 4/9 + 2/15 (reproduces 42) | B ORIG 9/9+15/15, A 8/8+15/15 |
| ORDER (P43_ORDER=p2first, p2 seeds state0) | 33218721 | 4/9 + 2/15, unchanged | all green |
| WIDTH (P43_TOPK=12, 12 states instead of 5) | 33218722 | 4/9 + 2/15, unchanged | all green |
| LENNORM (rank expansion frontier by inlier/LCS-row instead of absolute inlier) | 33219242 | **5/9 + 3/15 (+1 piece, +1 edge)** | all green |

In-container activation proven per arm (`P43-ORDER-P2FIRST-ARM`, `topk=12`, `P43-LENNORM-ARM` markers in binary.logs). ORDER x / WIDTH x: late entry and narrow beam are symptoms, not causes. LENNORM is the first beam-side change that moves B fresh without breaking ORIG.

**Which piece?** Replicated CountResult verdicts are NOT yet in hand (my laptop-side ICP replica failed: 0/0 vs stub 4/2 — rim curves slide under ICP, do not trust it). Next: VERBOSE single-arm job (P43_VERBOSE=1 prints stub's own per-piece verdicts for B fresh BASE-env + LENNORM-env, ~10 min). Render follows the verdict (eye-check before any claim; artifacts to `artifacts/pota43/`).

**Validity notes (self-caught, no data lost).** (1) First ORDER/WIDTH submissions ran as BASE duplicates — variant generator's string replace was a silent no-op; caught via DRIVER echo, resubmitted. (2) First LENNORM submission (33219158, CANCELLED by me) also ran header-only: the .cpp patch script died before writing while `diff --name-only` still matched — name-only allowlists do not prove content; now verified by marker counts in logs. Lesson for future tickets: assert replacement counts AND grep patch markers in build logs.

**Deliverable status:** mechanism named with numbers (above); p2 itself NOT yet seated. Full evidence: run dirs `/data/gpfs/projects/punim2657/sfs_main/pota43_run_{33218437,33218721,33218722,33219242}/`, LCS dumps + edgeline snapshots inside; seat-analysis scripts + fetched snapshots in `artifacts/pota43/` (`p43_seat_check.py`, `p43_icp.py`, `p43_stub_replica.py`, `seat/`).

## Comments (worker, 2026-10-17, 09:00 AEDT) — B-fresh beam is nondeterministic; tallies need repeats

VERBOSE job 33232934 (COMPLETED 0:0; env-gated per-piece print added to CountResult, scratch only) says: BASE-env B fresh = **3/9 + 2/15**, seated {p1, p3, p4} — NOT the 4/9 seen in three earlier BASE-env runs. LENNORM-env in the same job = **3/9 + 1/15**, seated {p1, p3, p7}. So the 5/9+3/15 LENNORM excursion (33219242) did not replicate. p2 unseated in all runs so far (0 ok edges everywhere).
Causes checked: LCS inventory identical in all 5 jobs (197 total, 83 pruned — feature matching is bit-stable); no RNG/time seeds in the code; the only OMP pragmas are order-independent (parallel-for over independent columns) or commented out. Same-node rerun (bm134: WIDTH 4/9 vs VERBOSE 3/9) rules out node/CPU differences. Remaining hypothesis: last-bit FP noise (codegen differences between builds — new struct fields/lambda capture change register allocation) flips near-tie beam states; the fresh beam sits on a knife-edge where integer-identical inputs diverge. DETER job 33236170 (3x B-fresh BASE-env, same binary, same node) now running to test this directly. CONSEQUENCE: the ORDER/WIDTH "no effect" reads and the LENNORM "+1" are all single-run point estimates on a noisy beam — the mechanism analysis (frontier math, missing p2-p1 edges) stands, but any seating claim now requires repeats ( >= 3) per condition. ## Comments (worker, 2026-10-17, 09:20 AEDT) — tally artifact found; knife-edge located at the 50 mm gate

PAIR job 33236370 (COMPLETED 0:0; pair-level print, BASE-env): similar DIRECTED pairs are (1,3),(1,4),(3,1),(3,7),(4,1),(7,3) — i.e. **3 true undirected edges {1-3, 1-4, 3-7}**, but the tally prints 2/15. Root cause READ IN THE CODE (`data_structure.cpp` CountResult): a similar (i,j) test sets BOTH af cells but increments k ONCE; the reverse direction is tested independently, and the relative-transform translation test is direction-ASYMMETRIC, so near-threshold pairs hit one direction only (k=5, and C++ integer `k/2` = 2). The "2/15" all along understates 3 seated edges. This also locates the knife-edge: the 3-7 pair sits at the 50 mm translation gate, so last-bit FP noise (across builds/nodes) flips it — that is the entire 3/9-vs-4/9 variance, not beam chaos. p2 has 0 ok pairs in EVERY verbose run (V_base, V_len, D1-D3, P1): starvation is deterministic at the pair level even where tallies wobble. LEN3 job 33236483 (3x B-fresh LENNORM-env, same binary/node, pair-level print) running to decide whether LENNORM replicably seats a 5th piece.

**Starting position:** B gate 15/15 on real pipe output (SFS-T42, job 33217089); GT-seated p2×p4 overlap ≈ ORIG; p2 candidates 0→93 yet p2 enters the beam last (others 323–795; ORIG p2 has 731); E2E stuck 4/9+2/15 ×2 across 3 different p2 rims (33217561/62). Structural gap: fresh p2 profiles run 9–15 rows vs ORIG 18–34 (~1-in-5 rows out-of-bin breaks every run; smoothing no gain). Controls: B ORIG 9/9+15/15, A both arms 8/8+15/15 — any experiment must keep them green in the same runs.

**Rules:** assembler-lane work happens in scratch copies of the cure vehicle ONLY (cure-potA @ bffefb6; fork main untouched); one variable per arm; beam-width/order changes need ORIG-validity in the same run (a faster wrong answer is failure, not progress); seating render of any claimed improvement (eye-check); no commits; sacct-direct polling; Comments-only ticket edits.

- [ ] Why p2 enters last: scoring decomposition (inlier-sum vs candidate count vs profile length)
- [ ] Width/order/profile-length arms, one variable at a time
- [ ] B fresh improvement + B ORIG 9/9+15/15 + A 8/8+15/15 in the same runs
- [ ] Job IDs + sacct states

**Successor:** cross-pot generalization of whatever seats B (D–J share the drowning shape).
