# Re-segmentation: find the real rim edge instead of stopping short

GOAL: THE SEGMENTATION REACHES THE TRUE RIM EDGE ON EVERY SHERD-FACE, POT A AND POT C.

**Answers:** E1

**Blocked by:** 172 (drop stage: surfaceSegmentation region-growing 4.5deg smoothness, mesh_processing.cpp:1341, rim strip in unclustered rejects), 171 (veto load-bearing on Pot A double-face pieces -- regression tripwire), 173 (densified bag 753, cap 211/211 -- walk-side input ready).

**Status:** results-in

**Lead ruling (2026-10-20): ACCEPT a+b as the ticket, CLOSE c as not-the-blocker.** (a) mesh-stage reclaim proven same-binary (188/188 stations <2mm, Pot A ref-cover 0.97-1.00, bit-exact control); (b) veto-free edge reproduces 171 red + first veto-free P04/P05/P06 loops, sort complete, zero genuine leavers. (c) needs no scope call: 176 run-1 E2E ties the bar with a gated rim (0.95) AND byte-identical T estimates to 145 -- the seating is stuck downstream of the rims (assembler-side), so no edge-coherence rule would move it. Follow-up is an assembler-side debug ticket, not 174(c). p174_apply.py recovered: laptop copy .scratch/pota174_repro/p174_apply.py exists (lead verified present); segmentationStats.txt regrows. Eye-check of C174 renders: ACCEPTED on worker evidence (coverage/top/tripwire claims all numeric and consistent); conservator Needs-eye on seating views still open lane-wide.

**User ruling (2026-10-20):** the pot is real, the geometry is a real break surface -- preprocessing must accurately identify the real edge instead of stopping and leaving a gap.

**What to deliver:** (a) A segmentation rule change (threshold, rim-aware growth, post-pass reclaim of unclustered rim strip, or re-segmented Surface_0 -- worker's choice with reasons) such that the accepted sheet reaches the true rim edge: sheet-to-rim distance <2mm at all 188 C01 gap stations AND Pot A rims covered at least as well as today. (b) NO FACE-SPILL: inner/outer faces stay separate (the 4.5deg cutoff's real job) -- prove with the same Pot A pairs 171 used: veto-free counts must not regress past cured counts on the 6 veto-needing pairs, and C01's false second loop must not return. (c) Walk + gate the result (M144-family, no invented dots): C01 coverage/gate vs fresh bar (92/211, 5.61/22.9) and 173 (211/211 union, med 1.26).

**Bar:** sheet reaches every C01 gap station <2mm AND zero face-spill on 171's Pot A pairs AND walk coverage >= fresh with flips/selfint DOWN vs 173 s1. Any leg failing = honest negative owning which leg with numbers.

**Starting position:** 172 Comments (drop stage, file+line, rejects evidence, gap table); 171 Comments (per-pair owners, veto-free vs cured counts, overlays); 173 Comments (bag recipe, walk numbers, residue analysis). Relay worktree at cure HEAD per 155; binaries rebuilt there. New scratch pota174_repro/; renders artifacts/pota174/.

**Rules:** dataset read-only; production checkout untouched (foreign-WIP dirty); relay worktree restore byte-identical; COMMIT NOTHING; tickets 39-173 read-only; edit this ticket's Comments section ONLY; same-binary ORIG control alongside or void; sacct State/ExitCode for every sbatch; eye-check every render.

- [ ] segmentation change + rim-reach numbers (C01 + Pot A)
- [ ] no-face-spill proof on 171 pairs
- [ ] walk + gate vs fresh bar and 173
- [ ] Verdict + render paths

## Comments (worker, 2026-10-20)

**Verdict: leg (a) PROVEN at mesh stage, same-binary, in-binary. Leg (b-rebased) gated. Leg (c) BLOCKED on loop extraction -- needs lead scope. Path is veto-free throughout per lead steer (no veto before/after).**

Rule change (worker's choice, with reasons): post-pass RECLAIM of the unclustered rim strip (threshold sweep killed first: 8deg merges faces -- thr8-S0 absorbs 99.9% of control-S1 within 1mm; 12deg identical; 20deg total merge. Threshold cannot pass both legs). Reclaim: free point joins nearest cluster if within D=6mm and normal-dot>cos(60deg), 12 rounds, labels preserved, ORIG-free. Patch SFS-P174 (+72 lines, mesh_processing_headless.cpp) + env SFS_RECLAIM_D/A. Deliverable kept as untracked worktree patch: pota174_reclaim_noveto.diff (also holds the SFS_NOVETO edge bypass below).

(a) rim reach, mesh stage, same-binary ORIG control (control 4.5deg reproduces staged S0 BIT-EXACT, med/max 0.000, n=11165): C01 reclaim S0 188/188 gap stations <2mm (max 1.816, in-binary, reproduces sim exactly); Pot A ref-cover (worktree ROOT Dataset refs, P02 md5 6b26826ddd92ae5772daac4267514193): PA01 S1 0.997/0.85, PA02 S0 1.000/0.54, PA03 S0 1.000/0.66, PA04 S1 1.000/0.53, PA05 S0 1.000/0.38, PA06 S0 1.000/0.35 (2mm both-dir; S1 faces correctly do NOT cover). No welding at mesh stage. Renders: C174_C01_coverage.png (every run below bar), C174_C01_top.png (188/188 green on rim). Eye-checked.

(b) rebased per 2026-10-20 steer (veto dropped entirely; cured-vs-noveto deltas VOID; gate re-segmented-vs-ORIG primary): veto-free edge via SFS_NOVETO=1 (faceVetoThr=2 keep-all + T05 bypass, env-gated, default=cure). D0+noveto reproduces 171-NOVETO red: P01_1 321 dots 0.542/1.68 EXACT; P02_0 165 0.988/0.45 ref 1.000/0.67; P03_0 150 1.000/0.62 ref 1.000/0.67; first-ever veto-free P04_0 145 0.993/0.55 ref 0.983/0.73, P05_0 150 0.980/0.62 ref 1.000/0.62, P06_0 145 0.979/0.69 ref 0.969/0.72. Sort COMPLETE: trackers P02-P06 (refcov>=0.969, must-cover), mixed P01_1 (outer+interior spurs), genuine leavers NONE. Reclaim+noveto edge fails everywhere (stubs/scribble: P06 2-dot, C01 Bl 21-dot) -- reclaim band defeats the boundary sequencer. Renders: C174_P02_0/P03_0/P01_1/P04_0_tripwire.png (red rides rim, blue cure stub). Eye-checked.

(c) BLOCKED: veto-free C01 loops are unwalkable -- D0+noveto Bl_0 (351 dots) is interior scribble, D6+noveto (21 dots) is off-rim stub (render C174_D_loops.png vs ORIG 211). Without veto+T05 the estimator sequences noise (they were load-bearing for coherence). Walk needs lead scope: walk mesh-boundary directly vs new edge coherence rule (new method either way).

Provenance: 8/8 E2E (145 jobs) reads pota40_bundle (.pcd only, NOT worktree) -- all 8 Bl_0 DIFF vs worktree refs; bundle is frame-shifted ~3.5mm (centroid-align: P02/P03/P04/P06 cov 0.70-1.00; P01_1 0.000, P05_0 0.65). Role test: seating lane absorbs the shift.

Jobs (sacct): sweep 33448352 COMPLETED 0:0 ~2m; builds 33448517/33448560 FAILED-noop (apptainer path), 33448720 COMPLETED 0:0; run1 33448755 COMPLETED-but-all-arms-127 ($APT-unset bug, zero writes); JobB 33448811 COMPLETED 0:0 el 27:40; ebuild 33449535 COMPLETED 0:0 el 48s; JobD 33449583 COMPLETED 0:0; restore-build COMPLETED 0:0 (edge binary md5 19397aab41908acc15f640c7a44aff55 == 171's veto record).

Restore: tracked diff md5 e546596c90f8552ed9a40db34c5c2a4b == baseline; binaries rebuilt from restored sources; Pot_A Dataset restored (md5 5ab3ddbc==backup); 18 staged Surface files restored from laptop copies. GAPS (worker error, owned): original_nurbs_preprocessing/segmentationStats.txt + p174_apply.py were baseline-untracked and deleted in cleanup with no backup (segStats regrows next run; p174_apply.py unrecoverable -- check lead copies). Worktree status = baseline list minus those 2 plus pota174_reclaim_noveto.diff (deliverable, mirrors 155 convention). COMMIT NOTHING honored. Laptop evidence: .scratch/pota174_repro/p174_evidence.txt; scripts p174_*.py; renders artifacts/pota174/C174_*.png.


**Evidence-path note (2026-10-23):** paths under .scratch/pota1xx_repro/ and .scratch/pota22x/ cited above were removed by the scratch cleanup of this date (untracked intermediates; not recoverable). The numbers, quotes and verdicts in this ticket stand as recorded -- do not chase those paths or re-derive from them.
