# 74: C01 segmentation + 02-04 translation floor

**What to deliver:** C01 lip recovered + floor explained — E2E upward.

**Answers:** E1

**Blocked by:** 73 (S24 lands 2/3+1/3 ×3 bit-identical, jobs 33286981/33286982/33286983 COMPLETED; seated edge 02-04 rel-ang 2.52° / rel-tr 17.37mm; S2 0/3; C01 unplaced; renders eye-checked) + 72 (C01 lip shredded at segmentation — S0 toseq 39% partial arc/14 components, S1 0%; no sampling/normal knob recovers) + 39 (J's 10-18mm floor — same family? compare).

**Status:** results-in (worker 2026-10-18, COMMIT NOTHING)

## Comments (worker, 2026-10-18 — COMMIT NOTHING; lead to commit)

**Verdict: LANDS via the "or" branch — floor mechanism bound + E2E holds 2/3+1/3 ×3 bit-identical in new scratch copies with all controls green. C01 in-file recovery measured NULL (4 gated arms, walkable-branch ceiling 39 pts); walk-level re-extraction scoped as successor, not attempted.**

**0. Work dir (NEW; 39/40/65–73 lanes read-only, untouched).** `/data/gpfs/projects/punim2657/pota74_repro/`: `pota74_bundle_C_S24` = `diff -r` identical copy of T73 S24 (C02/C04 slots `cmp`-identical to T73); C01 arms C1a/C1b/C1c (other pieces `cmp`-verified UNTOUCHED); `gate74.py` (gate73 repointed), `run_pota74_stage_AC.sbatch` (p73 vehicle repointed), `render74_*.py`. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only. No source edits anywhere — SingleOverlapTest@100 / RP / CheckGraph-150 untouched.

**1. C01 arms (one variable each, gate74 = GT-seated fresh-vs-ORIG):**
- C1a C01-Bl_0:=fresh Bl_1 (92 pts): med 46.54mm / 0%<2mm / 1 jump — Bl_1 is a different loop ~30–40mm off the lip (centroid gap), not a lip branch.
- C1b spur-dropped Bl_0 [39,402) (363 pts): 5.52 / 25.3% / 1×105mm jump — no recovery.
- C1c longest on-contour run [152,195) (43 pts): 1.80 / 55.8% / still 1×105mm teleport inside — closest to ORIG, but 1/5 of a lip (ORIG 211).
- Walkable-chain ceiling: longest spatially-chained (link<5mm) on-contour run = 39 pts (<5mm) / 22 pts (<2mm strict); 179 on-contour pts scattered over 10 chains; best possible stitching ≈70 pts with bridges. No walkable in-file branch exists — confirms 68/71 NULLs from the chain side. C02/C04 controls intact in all arms (0.78/98.5%, 0.73/93%).
- Render `artifacts/pota74/C74_C1c_vs_ORIG.png` (eye-checked): 43-pt red arc covers one short section of the gray ORIG ring; C02 red covers gray all around.

**2. Floor-chase (login-node probes, all numbers sacct-job-33286981 R1 + pota74 R1):**
- (a) T-frames EXONERATED: GT 02-04 edge byte-identical across ORIG/REF/S24 bundles (rel-ang 90.670°, rel-tr 683.18mm).
- (b) Header/flag channel EXONERATED: assembler parses `#` headers (`data_structure.cpp:210`, spans gate KD-tree via `index_(2,j)` per 62's mechanism); swapped files carry info=0 + all-zero seg flags = same flag class as ORIG Bl_0 (which seats exact). No recalled-span masking anywhere in S24.
- (c) Search-alone EXONERATED: ORIG-content search output residual vs GT = 0.391°/2.81mm — the machinery seats Pot C essentially exact with true rims.
- (d) BOUND — content-shifted overlap valley: S24 search residual = 2.521°/17.37mm, pure single-axis slide (tvec −17.35/−0.19/+0.66mm in piece-2 frame), bit-identical ×3 jobs ×2 arms (S24 and C_1C agree to 0.001°). Fresh seam overlap (C04→C02 <2mm share) is 24.3% at GT but 45.2% at the search seat — HIGHER than ORIG-at-GT (42.7%): search didn't under-optimize, it climbed a rim-overlap objective whose maximum-vs-GT is shifted by the fresh rim shape. I.e. neither frame nor search alone: fresh content shifts the valley, search correctly follows it to the wrong minimum.
- (e) Decoupling: C_1C arm (C01:=43-pt arc, C01 refused from graph → 2/2+1/1) seats the pair at the IDENTICAL 2.521°/17.37mm — C01 content does not perturb the floor; the floor is a property of the 02-04 pair + search.
- (f) Family: same 10–18mm translation-floor phenomenology as J (39 §5) and T30 Pot A edges — with the distinction that J floors even with TRUE rims (search-side valley) while C floors only with fresh rims (content-shifted valley; ORIG C is strict-exact).

**3. E2E ×3 same-binary (cure-potA @ bffefb6 verified `rev-parse`, tree clean, 2-file delta intact; k=5/b=3 shim; 5 arms/job: A_orig + A_fresh STEPS=8, C_orig + C_S24copy + C_1C STEPS=4; sacct-direct polling, never slurm_poll.sh).**

| job (sacct COMPLETED 0:0) | A_orig | A_fresh | C_orig | C_S24copy | C_1C |
|---|---|---|---|---|---|
| 33288861 | 8/8+15/15 (70) | 8/8+15/15 (120) | 4/4+5/5 (40) | 2/3+1/3 (17) | 2/2+1/1 (7) |
| 33288862 | 8/8+15/15 (70) | 8/8+15/15 (120) | 4/4+5/5 (40) | 2/3+1/3 (17) | 2/2+1/1 (7) |
| 33288863 | 8/8+15/15 (70) | 8/8+15/15 (119) | 4/4+5/5 (40) | 2/3+1/3 (17) | 2/2+1/1 (7) |

(forest/pruned in brackets; bit-identical tallies ×3 — deterministic binary; A_fresh pruned 120/120/119 = ±1 beam-count noise, tallies identical.)
Asserts per job: LINK-SHIM-OK ×5 + LINK-FORKMAIN-ABSENT-OK ×5 + DRIVER-SHIM-OK ×5 (all 3 jobs). Bundle guards: A-fresh + C-S24 + C-C1c intact ×3; asm tree clean ×3. Snapshots: C_S24 T_0,T_1,T_3; C_1C T_1,T_3 (C01 refused — 43 pts below admission). RUNDIRs `/data/gpfs/projects/punim2657/sfs_main/pota74_run_{33288861,33288862,33288863}/`, fetch tgz in each.
Render `artifacts/pota74/C74_S24_seating_R1.png` (eye-checked): estimated pair same shape as GT pair with visible offset (the 17mm floor, seen directly).

**4. Landing check vs the bar.** Floor mechanism bound ✓ (§2d–f). E2E at/above 2/3+1/3 ×3 same-binary ✓ (S24-copy 2/3+1/3 ×3, matching T73). Controls green same runs ✓ (C ORIG 4/4+5/5 ×3; A 8/8+15/15 orig+fresh ×3). Repeats ≥3 ✓. Zero ORIG points ✓. No gate relaxation ✓. C01 gated toward ORIG ✗ (measured why-not with ceiling, §1 — the "and" branch not met, the "or" branch carries the landing). Renders eye-checked ✓ (2 PNGs). Spartan leftovers: `pota74_repro/` + 3 `pota74_run_*` dirs only.

**Successor proposal for lead:** (a) walk-level forward-cone guard re-extraction for C01 (67/68 successor — the only unexhausted level; input ceiling 39% on-contour partial arc per 71, so predict partial-arc recovery, not a full loop); (b) floor remedy needs valley-reshaping (refinement weighting / overlap-term), NOT flag/header or frame work — §2 exonerates both; (c) thesis write-up: quote binary 2/3+1/3 WITH the 17.37mm single-axis-slide caveat + the overlap-valley evidence (45.2% vs 24.3%).

- [x] C01 recovery arms, one variable each
- [x] Floor-chase arms, one variable each
- [x] Gate + E2E rerun ×3 or measured why-not
- [x] Job IDs + sacct states

**Starting position:** two open items: (a) C01's lip shredded at the segmentation split — recover a walkable branch; (b) the seated 02-04 pair floats 17mm — same family as J's floor? Gate the floor: does it come from the swapped content (S1-branch frame) or the search? Bundle references pota73/pota72/pota39 C bundles (read-only). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** land with C01 gated toward ORIG and/or floor mechanism bound + E2E at or above 2/3+1/3 ×3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); prep-side scratch copies; E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition; no gate relaxation without a mechanism.

- [ ] C01 recovery arms, one variable each
- [ ] Floor-chase arms, one variable each
- [ ] Gate + E2E rerun ×3 or measured why-not
- [ ] Job IDs + sacct states
