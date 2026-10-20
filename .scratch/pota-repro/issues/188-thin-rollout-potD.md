# 188 - Thin-loop roll-out: Pot D

Status: landed (lead 2026-10-20: 29/29 singles verified, P22 artifact exonerated, E2E decline accepted -- rerun would duplicate 84)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Apply the 185 thin-then-walk cure to every doubled rim edge of Pot D, bundle, and E2E x3 vs this pot's established bar (cite the prior ticket that set it).

## Method (worker runs FULL chain, SSH works -- Host spartan)
1. Census: for each rim piece, test for doubling with key-free signals (closure distance, arc vs plan perimeter, D-token count per the 179 recipe). Name which edges are doubled.
2. Cure: apply the 185 v3 recipe (thin TRUE strip to centreline, uniform 1.8mm resample, verbatim walk_m144) to each doubled edge. Gate each loop: closure <=2.0, single wrap, rim-truth med where an author key exists (check-only).
3. Bundle: rebuild this pot's bundle with ONLY the cured Bl_0 slots changed (byte-proofs, only-changed-diff, veto-absence record, same guards as 180/186).
4. E2E: upload, login-node build (expect BUILD DONE), sbatch x3 + laptop-side poll per AGENTS.md, sacct tallies. Own a falsifier in advance.

## Constraints
Laptop + Spartan both allowed. COMMIT NOTHING (worker). No repo sources touched, dataset read-only. Finish by writing the self-contained result to this ticket's Comments + final output -- never via send_message (child-to-parent messaging does not exist).

## Acceptance
Per-piece doubling census + per-loop gates + bundle byte-proofs + E2E tallies x3 (Total/pruned/sherd/edge) vs the pot's bar + honest verdict (pass / honest negative with the refusing numbers).

## Required evidence
Ticket Comments + final output: census numbers, loop gates, md5s, job IDs, per-run tallies, verdict.

## Comments (worker, 2026-10-20 -- HONEST NEGATIVE, no cure target; COMMIT NOTHING)

**Status: results-in. Verdict: HONEST NEGATIVE -- the bar-setting bundle contains zero doubled edges, so thin-then-walk has no target on Pot D. No bundle rebuilt, no E2E run (either would duplicate ticket 84 byte-for-byte / job-for-job). 84 stands.**

**0. Base + bar (cited).** Bar-setting ticket: **84** (SXC, landed 2026-10-18): E2E 22/27+49/66, 21/27+47/66, 22/27+49/66 x3 (jobs 33361199/200/201, all COMPLETED 0:0) vs same-vehicle ORIG 23/22/23+55/55/53. Base used here = 84's bundle `/data/gpfs/projects/punim2657/pota84_repro/prep/pota84_bundle_D_SXC` -- the only base on which ONLY-cured-slots-changed is a valid comparison vs the bar. Boundary: login-node numpy screening (read-only) + laptop renders; no repo sources touched; dataset read-only; nothing committed.

**1. Census method (key-free, 179 recipe).** Per piece Bl_0: n, arc, plan-perimeter (PCA-plane angle-sort polygon), arc/plan ratio, closure, step med/max, gaps>5mm, D-token count (0.15 bins) + longest run; rim-truth med/cov vs ORIG Bl_0 CHECK-ONLY distances (zero ORIG points in any fix). Script `.scratch/pota188_repro/p188_census.py`, full 58-row table `.scratch/pota188_repro/p188_census.txt` (laptop copy + Spartan `/data/gpfs/projects/punim2657/pota188_repro/p188_census.txt`). Doubling call: ratio>=1.5 OR closure>5 OR ntok>=8 (179: author 3/run4 vs doubled 34/run2).

**2. SXC census: 29/29 clean single loops -- ZERO doubled.** ratio 0.97-1.14 on 28 pieces (P22 0.26 is a non-planar-loop ruler artifact: closure 1.67, gaps 0, ntok 4, orig_med 0.75 -- clean, and fresh-byte-identical control); closure <=1.92 on all 29 (gate <=2.0 PASS 29/29); gaps5 = 0 on 22 pieces, 1 on 7 (P01/P02/P03/P04/P05/P07/P11, max 11.4mm -- pre-existing in moved content per 84, 6/7 seat x3 there); ntok 3-4, runs 16-183; rim-truth med 0.51-0.86, cov ~full (D27 71% = thin small piece n=56, ratio 0.98/closed/gaps 0 -- clean, not doubled).

**3. Fresh census (context -- where the doubling actually lives): 13 doubled/forest Bl_0.** P03 (arc 1.6x, angle-sort plan explodes 4014), P08 (closure 17.2, gaps 4, ntok 20), P10 (forest n=649/gaps 17/ntok 42/closure 32.9), P11 (closure 114, ntok 16), P12 (forest n=689/gaps 21/ntok 48), P13 (closure 48.4, ntok 15), P14 (forest n=681/gaps 23/ntok 50), P15 (forest n=646/gaps 17/ntok 44), P16 (ratio 1.84/closure 77/ntok 21), P17 (ratio 1.97/closure 51.4/gaps 13/ntok 26), P19 (closure 53.8, ntok 18), P21 (closure 38, ntok 17), P26 (ratio 1.83/closure 41/gaps 6/ntok 20). Other 13 fresh Bl_0 are clean-but-swapped singles (ratio ~1.0, closed, ntok 3-4, orig_med ~7-9); P22/P28/P29 byte-identical controls. Byte-proof: SXC Bl_0 == fresh Bl_1 (D12 md5 7a0b8fc1a41dd55e5d3d8810b3693db9 both sides) -- per 63 Bl_1 is runtime-inert, so 84's slot-exchange already moved all 13 forest/doubled contents to the inert slot. That is why the bar-setting bundle has no target.

**4. Falsifier (owned in advance): proceed to cure+bundle+E2E iff >=1 doubled SXC Bl_0. Found 0 -> stopped.** No bundle rebuilt (output would be byte-identical to 84 SXC); no E2E (would duplicate 84 jobs 33361199-201, ~4.5 node-hours for zero information). No sbatch submitted, no job IDs to report. The single-jump SXC slots (7x1j) and thin D27 are single loops, not doubling -- 185's cure does not target them; left untouched.

**5. Render (eye-checked).** `.scratch/pota188_repro/p188_P17_fresh_vs_sxc.png`: order-coloured P17 -- fresh Bl_0 visibly laps twice with scattered second pass (n=131) vs SXC Bl_0 one clean circuit (n=88). Numbers and picture agree.

**6. Recommendation for lead.** The 13 doubled fresh-exterior walks are recoverable by thin-then-walk ONLY together with a slot decision (they are exterior-wall content: installing cured versions as Bl_0 reintroduces the 80 swap-wrongness) -- a two-variable experiment, not made here; needs a lead call. If a sibling rollout claims targets on an SXC-based bar, ask for its per-piece census first: on Pot D the same census shape would read 0/29.

**Jobs:** none (login-node screening only -- no cause named a run until the falsifier, which did not trigger). Spartan work dir `/data/gpfs/projects/punim2657/pota188_repro/` (census script + table only); 39/84 lanes, flaggers, vehicle untouched.
