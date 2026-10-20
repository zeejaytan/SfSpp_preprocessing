# 192 - Thin-loop roll-out: Pot I

Status: landed (lead 2026-10-20: 0/30 rim loops doubled verified, 60/60 manifest live, E2E decline accepted -- rerun would re-print 94; rim-truth-before-thinning lesson banked)
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
Apply the 185 thin-then-walk cure to every doubled rim edge of Pot I, bundle, and E2E x3 vs this pot's established bar (cite the prior ticket that set it).

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

**Verdict: honest negative -- Pot I has no doubled rim edge for the 185 thin-then-walk cure to fix. No bundle rebuilt, no E2E cut (re-running the byte-identical landed bundle would re-print 94's numbers at ~3 GPU-hours cost for zero information). Full chain executed through the gates; the gates refuse every candidate. COMMIT NOTHING held (only this section appended).**

**0. Boundary kept.** Dataset read-only; production checkout never entered; tickets 39-191 read-only (numbers quoted from 91/94 Comments); no assembler source touched; no ORIG points used anywhere (ORIG evidence = 91's seated-frame NN distances + 94's bar, both cited). Spartan work area pota192_repro/ only (census192.py + census192.txt); pota91/pota94/pota39 lanes untouched (read-only). Vehicle asm HEAD still bffefb6 (cure-potA, same as 94) -- vehicle unchanged since the landed run.

**1. Doubling census (login node, 179 key-free recipe: closure, arc, gaps>5mm, D-tokens at 0.15 bins; scipy absent on login node so no hull-perimeter -- closure+arc+tokens already decide). Full table: pota192_repro/census192.txt.**

SXC base (= landed cure bundle, Bl_0 = rim used by the matcher): ALL 30 Bl_0 loops clean singles -- closure 1.43-1.94mm, gaps 0-1, D-tokens 2-5, med step ~1.9mm. Zero doubled (examples: I06-Bl_0 133pts/arc 250/closure 1.91/ntok 4; I09-Bl_0 176/332/1.88/3; I13-Bl_0 101/207/1.91/2; I27-Bl_0 dense 55/91/1.70/3). Single 5-18mm jumps on 6 pieces (01/02/05/11/13/14) are the pre-existing byte-identical Bl_1-slot content 91 called out, not doubling (arc/closure/ntok normal). Gate result: 0/30 Bl_0 slots fail closure<=2.0 / single-wrap / ntok -- nothing to thin.

Fresh t39-pipe base: 17 Bl_0s ARE doubled by the same signals (arc 466-1821mm, closure 8-125mm, gaps up to 23, ntok 14-52; e.g. I09-Bl_0 n=723/arc 1821/closure 125/ntok 52; I06 n=821/1699/59.6/45; I10 n=699/1481/42.4/50). BUT 91's ORIG-evidence census (distances only, seated frame) proves none of them is the rim: 12 are foot-edge traces (fresh-Bl_0 vs ORIG rim med 5.3-11.4mm, cov 0-40%: I01 7.11/0, I02 11.43/0, I04 7.15/33, I11 7.05/12, I12 5.63/32, I14 6.92/36, I15 6.94/40, I16 7.93/27, I18 5.31/35, I20 6.87/40, I21 7.28/35, I08 7.00/26) and 5 are forest tracking neither edge (I06 2.68/44, I09 3.62/48, I10 1.53/55, I13 5.32/23, I19 4.81/48). Thinning them makes pretty loops of foot/garbage -- the 185 rim-truth gate (med ~0.6-0.8 + full coverage, cf. 180: 0.76/100%, 185: 0.64/97%) refuses all 17. Controls I25/I30 fresh-Bl_0s are rim AND already clean (67pts/123/1.43, 40/73.7/1.68) -- nothing to cure.

**2. Loop gates: no loop built.** Step-2 gates evaluated against both bases without building: (a) SXC Bl_0s already satisfy every gate (closure<=2.0, single wrap, ntok<=5, rim-truth 0.53-0.83 per gate91) -- re-walking them changes seating input for no reason; 186 lead ruling ("no further input-side iteration without new evidence") applies. (b) All 17 doubled fresh Bl_0s fail the rim-truth leg (~5-11mm vs ~0.7mm bar). Falsifier owned in advance: had any SXC Bl_0 shown closure>2.0 or ntok>>5 with rim-truth med <2mm, it would have been thinned, bundled, and E2E'd x3 -- 0/30 met it.

**3. Bundle byte-proofs: base untouched, landed state verified intact.** No rebuild performed (only-Bl_0-changed diff would be empty). pota91_bundle_I_SXC verified live vs pota94_I_SXC_BL_md5.txt: 60/60 OK, 0 FAILED; I27 dense Bl_0 md5 d0a1e771... == 94's byte-proof (55pts in place). Bl_1 slots holding doubled foot content (SXC Bl_1 = fresh Bl_0) deliberately untouched: out of scope per step 3 (Bl_0 only), and 94's 25/27 landing proves they don't block seating.

**4. E2E: NOT re-run; bar cited from 94 (sacct-verified).** Bar set by ticket 94 (I27-dense SXC, same vehicle bffefb6, k=5/b=3): I_SXC 25/27+54/65 x3 bit-identical (jobs 33387455/56/57, all sacct COMPLETED 0:0, ~47-62min) vs I_orig 25/27+59/65 x3 exact -- at ORIG sherd level, -5 edges. Context: pre-swap fresh bar was 63's 8/27+3/65 (39 unflagged 9+4). A same-vehicle re-run of the unchanged bundle today would print 94's numbers again; the thin cure contributes nothing on top, so no jobs cut.

**5. Meaning for the work.** Pot I's rims are cured already (swap + I27 densify, ticket 94) -- loop quality was never Pot I's gate; rim identity was, and it is fixed. The thin-then-walk rollout has no Pot I target. If the rollout series needs a Pot I data point, the citable result is: 0/30 rim loops doubled, 17/17 doubled fresh-Bl_0s refused as non-rim. Sibling pots should run the same rim-truth leg before thinning -- any "doubled" slot whose content is foot/forest must be refused, not beautified (ticket-58 lesson: foot-contaminated input destroys seating).

**Evidence.** Spartan pota192_repro/census192.py + census192.txt (60-slot table); live manifest re-check 60/60 OK. Laptop: this Comments section only. No renders (no geometry changed -- nothing to stage under visual-qa).
