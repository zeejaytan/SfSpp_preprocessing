# BetterWalk without the veto on Pot C — can the walker alone do it

GOAL: KNOW WHETHER THE WALKER NEEDS THE VETO.

**Answers:** E1

**Blocked by:** 156 (veto misfires on C01: kept=223 dropped=141 ate the true rim; gate 27.68mm/0%) + 155 (split-walk + half-plane guard ported, proven on Pot A relay).

**Status:** results-in

**What to deliver:** Pot C piece 01 extraction with veto DISABLED but the 155 sequencer (split-walk + half-plane guard) KEPT, gated the 98 way (cured-Bl_0 vs ORIG loops, pose cancels). Build a NOVETO variant in the relay worktree (veto bypass that keeps every admitted dot -- e.g. threshold to keep-all or env-gated skip; sequencer untouched), run on 156's staged Pot C inputs, gate vs fresh (5.61/22.9) and vs 156-cured (27.68/0). Verdict: does BetterWalk alone beat fresh on Pot C?

**Starting position:** 156 evidence (pota156_repro scripts, pota156_C tree, job scripts, gate scripts p156_gate.py/control/probe/render); 155 Comments (worktree, build commands, binary paths). New scratch pota158_repro/; renders artifacts/pota158/.

**Rules:** same-binary ORIG control alongside or void; veto-disable must not touch the sequencer code path (prove: SPLIT-WALK lines present, FACE VETO kept==all/dropped==0); COMMIT NOTHING (worktree-local build only); tickets 39-157 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [x] NOVETO binary built (veto keeps all, sequencer intact -- proof lines)
- [x] Pot C P01 run + gate vs fresh and vs 156-cured
- [x] Verdict (walker-alone vs fresh) + render paths

## Comments (worker, 2026-10-19 -- walker alone on Pot C, veto disabled)

**Verdict: the walker NEEDS the veto -- walker-alone FAILS the 98 gate on Pot C piece 01, worse than both fresh and 156-cured. BetterWalk alone does not beat fresh.**

Job 33424695 COMPLETED 0:0 el 33s. Own tree pota158_C (full copy of 156's staged tree; inputs md5-verified: Mesh.obj a0a3417 == ORIG Mesh_DS.obj, Point.pcd 651dd04 == p39 Dataset + Temp copies). NOVETO binary staged in pota158_repro (built in relay worktree from 155-ported sources + 4-line POTA158_NOVETO env gate: threshold 0.5 -> 2.0 keep-all; markers asserted in-job). Worktree restored byte-identical after build (source reverted, git diff --stat back to 127+/128-, cured binary md5 d653... restored). Sequencer file edge_line_ordering.cpp never touched.

NOVETO proof lines (edgeline_stage.log): [FACE VETO] kept=364 dropped=0 (align<= 2) surface 0 (all 223+141 admitted dots kept -- veto fully bypassed); kept=109 dropped=0 surface 1. [SPLIT-WALK] sequenced=340 cuts=51 (s0) / sequenced=107 cuts=2 (s1) -- sequencer intact and walking. Outputs: Bl_0 n=335, Bl_1 n=96 (= cured n=96; veto dropped 0 on surface 1, consistent).

Gate (98 Bl_0 ruler, pose cancels): NOVETO-Bl_0 vs ORIG-Bl_0 med=30.18 cov2=0.0%; vs ORIG-Bl_1 34.55/4.5% -- tracks NEITHER loop. Regressed vs fresh (5.61/22.9%) AND vs 156-cured (27.68/0.0%). NOVETO-Bl_0 steps max=46.95 med=1.91, 3 jumps >5mm (2 >= 40mm teleports); vs fresh-Bl_0 same-T med=17.71 cov2=8.1%. Control reproduces 98 census exactly (5.61/22.9, 5.96/25.4, 46.54/0, 47.96/0) -- pipeline valid, failure real. Render laptop artifacts/pota158/C158_gate_C01.png (= Spartan pota158_repro/C158_gate_C01.png) eye-checked: NOVETO red is interior scribble + rim fragment + vertical drop artifact, far from both ORIG loops; fresh blue roughly follows the rims.

Mechanism: without the veto the walker strings both lip faces (364 dots) into one 335-dot cloud with 51 cuts -- the half-plane guard banks teleports as cuts but cannot pick the true rim out of a two-face cloud. The veto compacts 364 -> 162 but with the Pot-A-tuned rule eats the true rim on this flaring break (156). So: veto load-bearing (off = strictly worse), current rule mis-tuned for Pot C.

E2E omitted by entailment (same logic as 156): fresh C01 at 5.61 did not seat in 145; NOVETO at 30.18 cannot. No bundle frozen. Next: retune veto (per-piece/normal-aware) under a new ticket; re-gate before any E2E. COMMIT NOTHING done (no commits; worktree restored; 39-157 untouched).

Provenance: pota158_repro/{p158_gate,control,probe,render_gate}.py (adapted 156 copies), run_pota158_extract.sbatch, slurm-33424695.out, EdgeLineExtractionHeadless_NOVETO (md5 75be...), edgeline_extraction_headless.cpp.orig158 (pre-patch backup).
