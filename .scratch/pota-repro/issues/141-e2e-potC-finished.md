# E2E Pot C with the finished bundle — does the traced rim seat sherds?

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 134 (finished walk M134d 278/282, gate 4.2488) + 138 (segment-credit honest, 7/8 banked, O37 the honest single) + 98 (last Pot C E2E: 2/3+1/3 with swapped C02/C04, C01 placed-but-wrong — the mark to beat) + 89 (author-regime recipe)

**Status:** results-in (worker 2026-10-19 — COMMIT NOTHING; lead to commit)

**What to deliver:** end-to-end Pot C assembly with the finished C01 bundle. Bundle: C01 = M134d 282-bag trace (frozen from 134, byte-verified) + C02/C04 swapped per 98 + C03 control + Pot C ORIG + A controls (same controls as 98). Bar (same as 98, must beat): seating above 2/3+1/3 with C01 seated AT GT (not placed-but-wrong). E2E x3 runs (nondeterminism noted in 90). Slurm via established pattern (sbatch + laptop-side poll record + sacct State/ExitCode in ticket). Render: seating view eye-checked (green seated / red miss, GT gray, same style as 98).

**Starting position:** .scratch/pota134_repro/ (frozen 282 bundle + M134d sequence), pota98_repro/ (Pot C E2E recipe, controls, bar). New scratch pota141_repro/; renders under laptop artifacts/pota141/.

**Rules:** bundle byte-verified against 134's frozen files first or stop; same-binary ORIG control alongside; COMMIT NOTHING; Comments-only ticket edits; sacct-verified jobs.

- [ ] Bundle frozen + verified, controls stated
- [ ] E2E x3 with job records
- [ ] Seating vs 98's bar (C01 at GT?)
- [ ] Verdict + render paths

## Comments (worker, 2026-10-19 — COMMIT NOTHING; lead to commit)

**Verdict: MISS. The finished M134d rim does NOT seat C01 — C_FIN lands exactly AT 98's bar (2/3+1/3 x3 bit-identical), not above it, with C01 unplaced in all 3 runs (no T_0; 98 had it placed-but-wrong). Controls green, asserts green, renders eye-checked.**

**0. Bundle frozen + verified (reproduce-or-stop PASSED).** Laptop .scratch/pota134_repro/ md5s: G282 fca04009 / seq_d 49ab9c9a / G279 8abbdbff / freeze 24013a32 / walk_d 62025b42 / trigger_d b7748f22 / control c226f3dd — all 7 uploaded to /data/gpfs/projects/punim2657/pota141_repro/frozen/ and md5-identical Spartan-side. seq_d re-parsed: len 290, unique 278, range 0..281, missing slots [133,160,197,200] = 134's 4 zero-payoff isolated pockets (honest, not hidden). Frame test (Spartan python): 270-bag -> fresh C01 Bl_0 med 1.21mm (SAME frame) vs ORIG Bl_0 med 4.31 — walk points used as-is in fresh frame, normals donor = nearest fresh C01 Bl_0 U Bl_1 (med 1.25/max 13.05/52>5mm). Build: 98 SXC bundle cp -a -> pota141_bundle_C_FIN, ONLY C01 Bl_0 replaced (278 unique-in-walk-order pts, 13 segs 402->278 proportionally rescaled per 95 precedent, info 0, WIDTH/POINTS 278, single DATA ascii). One-variable proof: diff + recursive diff vs 98 SXC show ONLY C01-Bl_0 differs (new md5 6288beff); 98-SXC BL manifest ALL-OK (no drift); fresh C01 md5s match 98 source guard (e1e59c/fa3805). Self-caught header bug: first build wrote a 12-line head slice that swallowed DATA + 2 fresh point rows (gate n=280) — caught at gate, fixed to 9-line head, rebuilt, re-verified (303 lines, 1 DATA, n=278). Loader ingests 277 unique (slots 0/26 coordinate-identical dup-shadowed pairadjacent in walk order — stated, not hidden). Tickets 39-140 read-only; nothing committed.

**1. Gate (FIN-Bl_0 @GT vs ORIG Bl_0, 98 logic repointed).** C01 n=278 med 4.25 / <2mm 30.2% (walk-gate 4.2488/29.3% reproduced in bundle form; vs fresh C01 F0-O0 5.61 in 98 census — rim is CLOSER to ORIG, honestly). Walk-order steps max 35.4 (retreat strides, 0 >= 40mm). C02 0.78/98.5 j0, C03 0.95/86.8, C04 0.73/93.0 — all 98-exact, SXC preserved. Render eye-checked: artifacts/pota141/C141_FIN_vs_ORIG.png (C02/C03/C04 red tracks gray tightly; C01 red follows gray ring with top-arc excursions + scatter, matching med 4.25).

**2. E2E (cure-potA @ bffefb6 asserted in-job, k=5/b=3 shim, POT overlays, STEPS 8/4; stage = run_pota141_stage_AC.sbatch = 98's with renames only, bash -n + zero-pota98-leftover verified; sacct-direct throughout; NO pilot failures, first submissions ran):**

| job (sacct COMPLETED 0:0, worker-verified) | A_orig | A_fresh | C_orig | C_FIN |
|---|---|---|---|---|
| 33397808 (17:15) | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 2/3+1/3 (46/8) |
| 33397835 (16:46) | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 2/3+1/3 (46/8) |
| 33397836 (15:56) | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 2/3+1/3 (46/8) |

Asserts 12/job x3 (4x LINK-SHIM-OK + 4x LINK-FORKMAIN-ABSENT-OK + 4x DRIVER-SHIM-OK); all containers exit 0; bundle guards green in every job. Forest 187/17-18 (98 SXC) -> 46/8 (FIN): cleaner rim prunes harder, same tally. Rule: AT bar x3, not above (sherds 2 vs 2, edges 1 vs 1); C_orig reproduces 98 EXACTLY in-vehicle.

**3. Identity (p141_identity.py; binary EXACT all 3 runs; direct est-vs-GT is the wrong metric — assembly world frame differs — so GT-relative rel-edge per 98 s4).** C_FIN seats pieces {1,3} = C02,C04 all 3 runs; C01 has NO placement (no T_0to_0 any run — not even 98's placed-but-wrong); C03 missed. Rel-edge 02-04: est (88.918deg, 672.2mm) vs GT (90.67deg, 683.2mm) = dAng 1.75deg / dTrans 11.0mm — the 98/73 pattern (translation-floor caveat stands, same family). Seating render eye-checked: artifacts/pota141/C141_FIN_seating_R1.png (green 02/04 placed off-vessel per floor, orange C01 FIN at GT unplaced, red-x C03 missed, gray vessel).

**4. Evidence.** Spartan pota141_repro/ (frozen/ 7 files + build/identity/render x2 scripts + sbatch + 7 slurm outs + bundle + 2 manifests + 2 PNGs + p141_build.txt) + sfs_main/pota141_run_{33397808,33397835,33397836}/ (binaries, snapshots, pota141_fetch.tgz in each). Laptop artifacts/pota141/ (C141_FIN_vs_ORIG.png, C141_FIN_seating_R1.png, p141_numbers.txt, 3 fetch tgzs). 39-140 lanes untouched; COMMIT NOTHING.

**5. Recommendation.** The 134/138 walk banked honestly as a RIM (gate 4.2488, segment-credit 7/8) but does not convert to a SEAT: C01 unplaced x3 with the 02-04 edge intact. Do not re-roll the rim — the miss is assembly-lane (search basin / translation floor ~11-17mm family / 4 unsequenced isolated slots), same family as 98's 02-04 floor note. If the lead wants a next probe: seat C01's FIN rim standalone against GT (placement-basin test, no reassembly) before spending more E2E.
