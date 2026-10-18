# Segment-flag probe (R-FLAG, the one OPEN item in the author recipe)

GOAL: MATCH AUTHOR'S INPUT.

**What to deliver:** Close ticket 89's R-FLAG (OPEN): find what the author segflags encode, whether our chain reads them at all, and whether adding author-style segflags to a landed bundle changes seating. Pass bar: a named mechanism (code cites) + verdict INERT or SEATING-SENSITIVE with numbers.

**Answers:** E1

**Blocked by:** 89 (R-FLAG OPEN: author files carry segment flags, ours lack them; R-SWAP/R-RESAMPLE/R-FOREST closed) + 95 (J RES bundle HOLDS: the test vehicle) + 45/46 (input/output fingerprinting)

**Status:** results-in (worker 2026-10-19 -- INERT with cites, no E2E; COMMIT NOTHING)

**Starting position:** Author ORIG bundle + t39-pipe fresh bundle + landed J RES bundle (92/95). Read the segment-block consumers first: does sfs_main (data_structure.cpp BuildTree and up) branch on segment flags/info at all (95 found info=0 inert — verify the flag path, not just info)? Compare one author rim's segment table against ours field by field.

**Rules:** code-first (read-only screening before any bundle change — if nothing reads the flags, close INERT with cites, no E2E); if something reads them, one variable (segflags only on the 8 J RES Bl_0, everything else byte-identical) + gate + E2E x3 vs 95's 7+13 on cure-potA @ bffefb6 with asserts; J ORIG + A controls in the same runs; sacct-direct polling (never scripts/slurm_poll.sh); COMMIT NOTHING; Comments-only ticket edits (append ## Comments worker-date + flip Status to results-in; checkboxes stay with lead); repeats >=3.

- [ ] Segment-table field compare (author vs ours, one rim)
- [ ] Consumer audit (who reads the flags — cites or INERT)
- [ ] If read: segflag-only variant + gate + E2E x3 vs 7+13
- [ ] Job IDs + sacct states (if E2E run)

## Comments (worker, 2026-10-19 -- COMMIT NOTHING)

**Verdict: INERT. A segflags-only variant on the J RES vehicle cannot move seating: every consumer of the per-segment flag column is gated on header info, and all 24 fresh J files (incl. all 8 exchanged Bl_0) carry info=0. No E2E run, no bundle copy, no jobs -- code-first screening closes the ticket.**

0. Read-only screening only (zero ORIG points; source bundles md5-guarded, never written). Vehicle: landed J RES bundle at pota92/prep/pota92_bundle_J_SXC (post-95 resample) -- md5sum -c pota95_J_RES_BL_md5.txt all OK 2026-10-19. Assembler: pota39_repro/asm @ bffefb6a983403ac45b96aa84a5c52f4fa0a814e tree-clean (verified in-job guard triple: HEAD match + P22FIX/P22FIX2/C2-0.436 present).

1. Segment-table field compare (author ORIG vs fresh J RES; full 24-file scan + CSV in artifacts/pota96/p96_J_segflag_compare.csv). ORIG headers: # nseg npts info then # start end flag lines. One-rim example J02-Bl_1 -- ORIG: # 6 197 1 with segs 1-35 0 / 36-81 0 / 82-113 1 / 114-129 0 / 130-167 0 / 168-197 0 (rim span 82-113 flagged, info=1). Fresh J02-Bl_1: # 7 858 0 all seven seg flags 0. Fresh J02-Bl_0 (resampled): # 6 139 0 all flags 0. All 24 fresh J files: info=0, every seg flag 0. Author-side nuance: three ORIG J files carry seg flags with info=0 and are self-inert by the same gate -- J10-Bl_1 (# 3 75 0 flags 1 1 0), J08-Bl_1 (# 4 60 0 flags 0 1 1 0), J03-Bl_1 (# 11 120 0 one seg flag 1). So even the author has inert flags on J: the header is the switch, not the flag column.

2. Consumer audit (cure-potA @ bffefb6, file:line cites -- every index_(2,j) read sits inside an is_seg_rim_ guard, and is_seg_rim_ comes ONLY from header info at data_structure.cpp:218-224: abs(info)==1||abs(info)==3). (a) data_structure.cpp:112-139 BuildTree: is_seg_rim_ true -> insert point i only via a seg with index_(2,j)==0; is_seg_rim_ false (info=0) -> else branch inserts ALL points. Fresh J (info=0) takes the else branch always -- flags never consulted. This confirms and extends 95 (info=0 inert) to the flag path. (b) feature_matching.cpp:226-242 LCS rim-span harvest gated on is_seg_rim_ + index_(2,i); 284-289 a_cdt||b_cdt -> LCSuff=0. With info=0, Rim spans stay 0,0 so a_cdt/b_cdt are identically false. (c) feature_matching.cpp:338-354 + 396-403 LCSGraphBuilding: same gate, same dead condition. (d) feature_matching.cpp:1121-1131 + 1271-1282 CountPCInlier rim_data harvest: gated on is_seg_rim_ + index_(2,j); empty under info=0. (e) ranking_system.cpp:1140 exclusive_index==1 filter keeps only pairs with BOTH endpoints is_seg_rim_ -- no-op when no rim files exist. (f) ranking_system.cpp:1806-1838 H_rim veto: rim_data assembled under is_seg_rim_ gate (1811), is_rim stays false, top_gap/bottom_gap kill at 1835-1837 never fires. Base-flag siblings (is_seg_base_/is_sane_base_ at feature_matching.cpp:1467-1471,1537-1541,1850-1851) key off abs(info)==2||3 -- likewise dead at info=0; J02-Bl_0 ORIG info=-2 vs fresh 0 noted as base-path instance, out of this ticket scope.

3. Why no E2E (rule: no E2E without a named consumer). The ticket-scoped variant is segflags-only on the 8 J RES Bl_0 with everything else byte-identical -- i.e. header stays info=0. By (a)-(f) that variant is bit-identical in assembler behavior to the landed bundle: no consumer reads index_(2,j) when is_seg_rim_ is false. The only E2E-moving flag interventions on record (47 on B: 4/9+2/15 -> 7/9+7/15 x3; 61 Arm C on J: +2/+1 via P01/P03/P04 masking per 62) always rewrote header AND flags together -- p47_flagger.py:106-112 sets h1[3]=1 iff any seg flagged (DATA md5 asserted invariant) and p61C_J_flagger.py does the same (top 0->1 reports). A header+flags variant on J RES would be a different (two-variable) intervention duplicating 61 Arm C, which already seated J 7/10+13/18 with flags on -- no consumer names it for the 95 RES vehicle, and 95 HOLDS exactly that tally unflagged. So: nothing to gate, nothing to run. Repeats n/a (code verdict, deterministic); sacct n/a (zero jobs cut -- login-node reads + md5 only, never slurm_poll.sh).

4. Evidence. Spartan read-only: ORIG + J_SXC headers/segments (paths above), pota95_J_RES_BL_md5.txt all-OK, asm HEAD bffefb6 clean. Laptop: artifacts/pota96/p96_J_segflag_compare.csv. Renders: none (no seating change to witness; 95 renders stand as the vehicle baseline). 39-95 lanes, flaggers, bundles untouched.

5. Recommendation. Close 89 R-FLAG as INERT-for-J-vehicle with a scope note: segflags matter ONLY with a rim/base header (47/61 mechanism intact elsewhere); on any info=0 bundle they are dead columns. If a future ticket wants author-style flags on J, it must propose header+flags together (two variables, new ticket) and say why it would beat both 95 (unflagged 7+13 HOLDS x3) and 61-J-flagged on the same pot. No follow-up E2E from this ticket.
