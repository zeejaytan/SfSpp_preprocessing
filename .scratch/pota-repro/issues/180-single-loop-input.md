# Single-loop input: de-double, resample, close, reseat C01

GOAL: C01 SEATS WITH THE UNTOUCHED ASSEMBLER, BY FEEDING IT A SINGLE CLOSED LOOP.

**Answers:** E1

**Blocked by:** 179 (gating feature: ordered xyz as LCS token source; author 211-pt closed uniform 380mm loop / 3 D-tokens vs ours 439-pt open doubled 691mm walk / 34 D-tokens; curvature/normals/schema ruled out), 176 (439-dot TRUE walk source), 145 (CSXC rims, GT_C, 98 bar).

**Status:** ready-for-agent

**User ruling carries:** assembler NOT touched. Input only.

**What to deliver:** (1) De-double the 439-dot TRUE walk to one strand (arc ~380mm) + uniform arc-length resample at 1.80mm (n~=211) + close loop (<=2mm), zero gaps>5; hold channels + 13-seg machinery per 179. (2) Rebuild the C bundle with ONLY C01-Bl_0 changed (all other slots bit-identical to 176 -- prove with md5), rim-truth gate vs author (must hold ~0.95). (3) E2E x3 same-binary ORIG control alongside vs 98 bar. Lead relays the Spartan run from staged prep (worker has no SSH -- stage build + sbatch, do NOT submit).

**Bar (179 predictions):** Total 40 -> 100-125 band, pruned 8 -> 30-40 band, C01 pairs >=1 survivor, C01 seated (edges 1/3 -> >=2/3). FALSIFIER (179): Total stays ~40 -> gate is H/Theta or segment windows, proposal refuted -- report honestly, do not re-tune.

**Rules:** dataset read-only; production checkout foreign-WIP dirty, never touch -- relay worktree only, restore byte-identical; COMMIT NOTHING; tickets 39-179 read-only; edit this ticket's Comments section ONLY; same-binary ORIG control or void.

- [ ] Single-loop C01 input built + gated
- [ ] Bundle rebuilt, other slots bit-identical
- [ ] E2E staged for relay (x3 + controls)
## Comments (worker, 2026-10-20 -- single-loop input built + gated, E2E staged for lead relay; COMMIT NOTHING)

**Status: input legs COMPLETE, E2E STAGED-READY but NOT RUN -- this worker has no SSH (no submit). No verdict on the 179 bar yet; this is a progress report, not a landing.**

**0. Boundary kept.** Dataset read-only; production checkout never entered; tickets 39-179 read-only (numbers quoted from 179/176 Comments only); no assembler source touched (not even read); nothing committed; only this Comments section edited.

**1. Single-loop input numbers (laptop numpy, method = 179 s3 verbatim).** Source: p176_C01_TRUE_walk.npy (439 dots, md5 5f902355dd99a4fe35885bf596193733, seated frame -- frame verified: vs fresh-mesh med 356.9 = cross-frame, vs author-seated med 0.95 = exact 176 s7 gate repro). Doubling confirmed: every author station has >=1 walk neighbour <2mm (med 4.0), strand spread med 2.58mm, walk halves cover only 88/211 + 101/211 stations (strands interleave -- no clean halfway split). De-double = closed Viterbi single track through per-station candidates (one pick per author-ordered station, min total length incl. closure, no-stay constraint; author used for ORDER only, xyz stays ours): track 673.7 -> 395.6mm, 202/211 distinct picks. Inverse-T to mesh frame (176 s7a: bundle lives in mesh frame, assembler applies T). Closed-loop uniform arc-length resample at 1.80mm.

| qty | author ORIG | 176 doubled | 180 single |
|---|---|---|---|
| n | 211 | 439 | 220 |
| arc | 380.0mm | 691.4mm | 395.6mm |
| closure | 1.80mm | 17.67mm | 1.48mm (<=2 PASS) |
| gaps>5mm | 0 | 3 | 0 |
| zero-steps | 0 | 2 | 0 |
| spacing max/med | 1.97/1.80 | 14.77/1.36 | 1.80/1.79 |
| D-tokens (0.15 bins) | 3, longest run 4 | 34, longest run 2 | 4 (top bins 11:201, 10:13, 8:3), longest run 36 |

**2. Rim-truth gate vs author (176 s7 recipe: seat via T, NN vs author ORIG seated) -- HOLDS.** Ours-vs-author med 0.76, <2mm 100.0%, max 1.83; author-vs-ours med 0.75, max 1.83 (176 s7: med 0.95, <2mm 93.2%). Channels held per 179 s3(d): G0 author-normal donor (mesh-mesh NN med 0.76, n>5mm 0; P39-fresh ruled out shredded per 176 s7b) + G0-constant curvature 1.905766e-42 (non-gating per 179 row 10); 13-seg rescale machinery verbatim (402->220, head # 1 16 0, tail # 216 220 0). Eye-check: artifacts/pota180/p180_01_single_vs_ref.png -- red single loop rides the green author ring all around; one honest qualification: a small kink at the right-side curl (x~45-60, within the 1.83 max) -- visible, not walked around.

**3. Bundle slot-hygiene (md5, laptop reference bundle = 7x fetched 98-SXC rims + new Bl_0).** ONLY C01-Bl_0 differs (d4793a55 -> 8ab5bbf2); the other 7 slots bit-identical: Bl_1 fa3805fe, C02-Bl_0 cb5c2ec5, C02-Bl_1 7d48c6c7, C03-Bl_0 9d2d6183, C03-Bl_1 32541c25, C04-Bl_0 f04f5cf9b, C04-Bl_1 b5dcec46. Spartan build repeats this proof live vs 98-SXC (byte-diff + intact check in p180_build.py s5).

**4. Staged for lead relay (.scratch/pota180_repro/, 176 pattern).** p180_C01_single_walk.npy (220x3 mesh frame, md5 3a8909031978b2038da85cd00ed73ba2) + p180_build.py (py_compile OK; walk reproduce-or-stop, G0-donor tripwire, seg rescale, 98-SXC base + Bl_0 install, byte-proofs, manifests, veto-absence record) + run_pota180_stage_AC.sbatch (bash -n OK; 4 arms A_orig/A_fresh STEPS 8 + C_orig/C_180 STEPS 4, same asserts/shim/k5-b3/GT-stub contingency as 176, bundle guard vs pota180_C_180_BL_md5) + RELAY.txt runbook + p180_BL_md5.txt + p180_report.txt/p180_pcd.txt logs + p180_make_input.py/p180_make_pcd.py/p180_render.py (rerunnable) + ref_bundle/ reference + p180_C01_single_walk_seated.npy (gate transparency). Same-binary ORIG control (C_orig arm) is in-job. Lead runbook: ship 3 stage files -> login-node python3 p180_build.py (expect BUILD DONE, only-Bl_0-diff, 98-SXC ALL-OK) -> sbatch x3 + poll + sacct State/ExitCode -> tally vs 179 bar (Total 40 -> 100-125, pruned 8 -> 30-40, C01 pairs >=1 survivor, edges 1/3 -> >=2/3). FALSIFIER owned in advance: Total stays ~40 -> the gate is H/Theta or segment windows, proposal refuted, no further input-side iteration without new evidence.

**5. Evidence.** .scratch/pota180_repro/ (scripts + walk npys + reference pcd + md5 + logs + RELAY.txt) + artifacts/pota180/p180_01_single_vs_ref.png. No repo sources touched, dataset read-only, COMMIT NOTHING.

## Lead E2E verdict (2026-10-20, jobs 33470102/3/4, all COMPLETED 0:0)
- C_180 x3: Total 165/165/165 (179 predicted 100-125 -- beat it), pruned 27/28/27 (predicted 30-40, close), sherd 3/3 + edge 3/3 (100%) ALL runs, T_0to_0 present in every C_180_Result = C01 SEATED x3.
- 179 falsifier (Total stays ~40) NOT triggered -- gate was the doubled input, proposal CONFIRMED and exceeded.
- Controls hold: A 8/8+15/15 both arms (no regression from shared code path), C_orig 4/4+5/5.
- vs 176 (Total 40/pruned 8, C01 unseated) and 145: the single closed loop is the cure. Bar beaten: 2/3+1/3 -> 3/3+3/3.
- Status: DONE. Next: roll single-loop input to remaining pots per agreed order (m03411), then write full fixes ledger.

