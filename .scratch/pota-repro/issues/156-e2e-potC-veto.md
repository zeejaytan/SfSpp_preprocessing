# E2E Pot C with the veto-cured C01 — does the cure seat sherds

GOAL: THE CURE SEATS SHERDS.

**Answers:** E1

**Blocked by:** 155 (vetoed binary proven: P02_0 97 vs 743, P05_0 97 vs 343; relay path in 155 Comments) + 145 (bar: 2/3+1/3 x3 with 314-bundle C01 UNSEATED -- the mark to beat) + 98 (E2E recipe, controls, seating-render style) + 89 (author-regime recipe).

**Status:** results-in

## Comments (worker, 2026-10-19 -- relayed by lead; worker's ticket write-back failed, report verified independently)

**Verdict: veto-cured C01 FAILS the 98 gate on Pot C piece 01 -- veto misfires, E2E x3 omitted by entailment, bar not beaten.**

Job 33424165 COMPLETED 0:0 (lead-verified via sacct). Own tree pota156_C (inputs md5-identical to ORIG mesh + p39 Point PCD; relay worktree exec-only). Cured binary asserted in-job (FACE VETO + SPLIT-WALK markers). Edge log: [FACE VETO] kept=223 dropped=141 (surface 0), kept=109 dropped=0 (surface 1) (lead-verified in edgeline_stage.log). Outputs: Pot_C_Piece_01_Breakline_0 n=162, Bl_1 n=96 (181-line pcd lead-verified).

Gate (98 Bl_0 ruler, pose cancels): cured-Bl_0 vs ORIG-Bl_0 med 27.68mm cov2 0.0%; vs ORIG-Bl_1 33.45/9.3% -- tracks NEITHER loop. Regressed vs fresh (5.61/22.9%). Control reproduces 98 census exactly -- pipeline valid, failure real. Cured-Bl_1 ~= fresh-Bl_1 (med 0.70). Render artifacts/pota156/C156_gate_C01.png lead eye-checked: cured red sits interior, far from both ORIG loops.

Mechanism: veto keeps align<=0.5; C01's flaring-break fracture normals sit within 60 deg of outward radial, so the Pot-A-tuned rule eats the true rim. Byte-identical-on-Pot-A does not generalize to Pot C piece 01.

E2E omitted: only C01 changes vs 145's C_FIN bar run; fresh C01 at 5.61mm did not seat, cured at 27.68mm cannot -- best possible E2E = tie, entailed. No C_CURE bundle frozen. Recommended next: retune veto (per-piece/normal-aware) under a new ticket; re-gate before any E2E.

**What to deliver:** end-to-end Pot C assembly with a veto-cured C01. Cured C01 = veto at SOURCE (cured-binary extraction of Pot C, preferred) or veto applied to the 314 bag with stated justification (fallback -- the veto field is ORIG-free and bag-agnostic per 153/155, but source is cleaner). Bundle: cured C01 + C02/C04 + C03 control + Pot C ORIG + A controls (same as 98/145). Bar (must beat): seating ABOVE 2/3+1/3 with C01 seated AT GT. E2E x3 runs. Same-binary ORIG control alongside or the run is void. Render: seating view eye-checked (green seated / red miss, GT gray, 98 style).

**Starting position:** .scratch/pota98_repro/ (E2E recipe, controls, bar), .scratch/pota144_repro/ + pota143_repro/ (314 bundle if fallback path), 155 Comments (cured worktree sfs_cure_1c6a8f9 on Spartan, relay commands, binary paths). New scratch pota156_repro/; renders under laptop artifacts/pota156/.

**Rules:** bundle byte-verified first or stop; sacct State/ExitCode recorded; COMMIT NOTHING; tickets 39-155 read-only (39 owns D-J lanes -- do not touch its run dirs); Comments-only ticket edits; worker eye-checks every render it claims.

- [ ] Cured C01 produced (source preferred, fallback justified)
- [ ] Bundle frozen + verified, controls stated
- [ ] E2E x3 with job records
- [ ] Seating vs 145's bar (C01 at GT?)
- [ ] Verdict + render paths

**Comments (worker 156, 2026-10-19): VERDICT = VETO MISFIRES ON POT C PIECE 01 -- GATE FAILED, E2E OMITTED BY ENTAILMENT.**

Cure ran clean at source: Spartan job 33424165 (sbatch pota156_repro/run_pota156_extract.sbatch) COMPLETED 0:0 el 31s. Own tree pota156_C (inputs md5-identical to ORIG mesh + p39 Point PCD). Cured binary asserted in-job (FACE VETO + SPLIT-WALK markers present). Edge log: [FACE VETO] kept=223 dropped=141 (surface 0), kept=109 dropped=0 (surface 1); SPLIT-WALK sequenced=166 cuts=25 / sequenced=107 cuts=2. Outputs: C01 Bl_0 n=162, Bl_1 n=96 (pota156_C/Dataset/Breaklines/Pot_C/). Provenance scripts: pota156_repro/p156_gate.py, p156_control.py, p156_probe.py, p156_render_gate.py; slurm out: pota156_repro/slurm-33424165.out.

Gate (98 Bl_0 ruler, same-T mapping, TO==TS byte-identical so pose cancels -- pure geometry): cured-Bl_0 vs ORIG-Bl_0 med=27.68mm cov2=0.0%; vs ORIG-Bl_1 med=33.45 cov2=9.3%. REGRESSED vs fresh (314-trace): fresh-Bl_0 vs ORIG-Bl_0 med=5.61 cov2=22.9% (control run reproduces 98 census exactly: 5.61/22.9, 5.96/25.4, 46.54/0, 47.96/0 -- pipeline valid). Cured-Bl_1 ~= fresh-Bl_1 (med 0.70, cov2 95.8%, recall 100%; veto dropped 0 dots there). Cured-Bl_0 shares only 9.3% with fresh-Bl_0 (same T); single 56.6mm teleport remnant at idx15. Eye-checked render (XY+XZ @GT, ORIG gray/black, fresh blue, cured red): cured-Bl_0 is a small interior patch + rim fragment + vertical drop artifact, NOT the vessel-circle rim. Render: laptop artifacts/pota156/C156_gate_C01.png (= Spartan pota156_repro/C156_gate_C01.png).

Mechanism (hypothesis, from 155 diff edgeline_extraction_headless.cpp:913-949): veto keeps dots with normal-vs-centroid-radial align<=0.5 (drops outer-lip-face dots). On Pot C piece 01 it dropped 141/364 surface-0 dots INCLUDING the true fracture rim -- i.e. this piece's fracture-face normals sit within 60 deg of outward radial (flaring break), so the Pot-A-tuned rule eats the rim. Byte-identical-on-Pot-A does not generalize to Pot C piece 01.

E2E x3 OMITTED deliberately (not foregone -- entailed): only C01 changes vs 145's C_FIN bar run (C02/C03/C04/A inputs identical, assembly stable 2/3+1/3 x3 in 145); fresh C01 at med 5.61 did NOT seat (145: C01 UNSEATED); cured C01 at med 27.68 (0% within 2mm) cannot seat at GT; C03 missed in all 145 runs for its own reasons (unchanged inputs). Best possible E2E = tie 2/3+1/3 != beat. Three 4-arm AC jobs would burn cluster budget for zero information. No C_CURE bundle frozen (nothing gate-passing to freeze). run_pota156_stage_AC.sbatch port is staged in pota156_repro/ if a future veto version passes the gate.

Next: retune veto (per-piece or normal-aware rule) under a new ticket; re-gate with p156_gate.py + p156_control.py before any E2E. COMMIT NOTHING done (no git commits; 39-155 untouched; relay worktree sfs_cure_1c6a8f9 read/exec-only, no writes).
