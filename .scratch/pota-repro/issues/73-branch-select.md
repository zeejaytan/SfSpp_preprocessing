# 73: Surface-branch selection — route the clean lip downstream

**What to deliver:** the S1-branch lip seated in the assembly path — E2E above zero.

**Answers:** E1

**Blocked by:** 72 (C02 Bl_1 203 pts / 0.78mm / 98.5%<2mm / zero jumps; C04 Bl_1 115 pts / 0.73mm / 93% / one 6.9mm link; assembler reads ONLY Bl_0 per asm/class/data_path.h; DENSE/NORMK refuted per-dose; C01 shredded at segmentation; jobs 33286361/33286648 COMPLETED) + 63 (Bl0-only loading proven per data_path.h:695 — Bl_1 file edits are runtime-inert; route must go through what the binary actually loads) + 62 (index_=1 semantics — recalled spans interact with matching/veto; watch for it).

**Status:** results-in (worker 2026-10-18, COMMIT NOTHING)

## Comments (worker, 2026-10-18 — COMMIT NOTHING; lead to commit)

**Verdict: LANDS on the binary metric — S24 (C02+C04 Bl_0:=fresh Bl_1, prep-side swap) seats 2/3+1/3 ×3 bit-identical with all controls green in the same runs. S2 (C02 alone) is 0/3+0/3 ×3. The seated edge is 02-04, rotation 2.5° with a 17mm translation floor — so under strict 5°/10mm relative-edge it is 0/3 (same translation-floor family as J in T39). Gate recovery holds in the loaded slot (C02 0.78mm/98.5%/0 jumps, C04 0.73mm/93%/one 6.9mm link). Zero ORIG points; no source edits; shims green 5/5 per job ×3.**

**Starting position:** the clean lip exists in-file (Bl_1) but invisible downstream. Options: swap Bl_1 content into the Bl_0 slot in scratch bundle copies (prep-side, zero ORIG points), or per-piece branch selection (C02/C04 from S1-branch, C03 stays, C01 needs segmentation work — flagged, not mandated). Bundle references pota72/pota39 C bundles (read-only). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** land ONLY with gate recovery toward ORIG per-edge AND E2E above 0 ×3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); prep-side scratch copies (no assembler source edits without a mechanism); E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition; no gate relaxation without a mechanism.

- [x] Branch-selection arms, one variable each
- [x] Gate + E2E rerun ×3 or measured why-not
- [x] Job IDs + sacct states

**0. Arms (fresh-only PCD slot swaps, prep-side scratch copies; ORIG evidence-only).**
NEW work dir `/data/gpfs/projects/punim2657/pota73_repro/` (39/40/65–72 lanes untouched, read-only).
REF = `pota39_repro/prep/pota39_bundle_C/SfS_pp` (untouched; md5 guards on A-fresh + both C arms pass in every job).
S2 = full REF copy with `Pot_C_Piece_02_Breakline_0.pcd := Breakline_1.pcd` (byte-identical to fresh Bl_1 source via `cmp`; C01/C03/C04 slots verified UNTOUCHED via `cmp -s`).
S24 = full REF copy with C02 AND C04 `Breakline_0 := Breakline_1` (one variable vs S2 = the C04 swap; C01/C03 untouched).
ORIG-contamination guard: swapped files differ from `original_samples` ORIG (fresh-only OK). No assembler/prep source edits anywhere — SingleOverlapTest@100 / RP / CheckGraph-150 untouched. Swapped PCDs carry fresh Bl_1 segment headers verbatim (no flag edits), so no new index_=1 reinterpretation was introduced (62) — the veto/matching behavior is whatever the binary does with that content.

**1. Gate (login-node screening, `gate73.py` = gate72 logic repointed; GT-seated, ORIG as ruler only).**
REF reproduces T71/T72 exactly: C01 Bl_0 402pts/5.61mm/22.9%/3 jumps; C02 Bl_0 267/6.07/0.0%/3 jumps; C04 Bl_0 191/5.48/5.8%/2 jumps; C03 Bl_0 167/0.95/86.8% (control).
S2: C02 Bl_0 → 203pts/0.78mm/98.5%/ZERO jumps (gate recovery); rest = REF.
S24: C02 as S2 + C04 Bl_0 → 115pts/0.73mm/93.0%/one 6.9mm link @idx5, closure 1.92 (gate recovery toward ORIG per-edge); C01 still shredded (402/5.61, both branches miss — segmentation work flagged, not mandated); C03 control intact.
Render `artifacts/pota73/Csel_S24_vs_ORIG.png` (eye-checked): C02 red covers the gray ORIG ring all around; C04 tracks with slight parallel offset + small fold-back at the 6.9mm-link region.

**2. E2E ×3 same-binary (cure-potA @ bffefb6 verified `rev-parse`, tree clean, 2-file delta intact; k=5/b=3 shim; 5 arms/job: A_orig + A_fresh STEPS=8, C_orig + C_S2 + C_S24 STEPS=4; `run_pota73_stage_AC.sbatch` = p68 vehicle repointed; sacct-direct polling, never slurm_poll.sh).**

| job (sacct COMPLETED 0:0) | A_orig | A_fresh | C_orig | C_S2 | C_S24 |
|---|---|---|---|---|---|
| 33286981 | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 0/3+0/3 (259/5) | 2/3+1/3 (212/17) |
| 33286982 | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/41) | 0/3+0/3 (259/5) | 2/3+1/3 (212/16) |
| 33286983 | 8/8+15/15 (124/70) | 8/8+15/15 (420/119) | 4/4+5/5 (125/40) | 0/3+0/3 (259/6) | 2/3+1/3 (212/17) |

(forest/pruned in brackets; bit-identical tallies ×3 — deterministic binary.)
Asserts per job: LINK-SHIM-OK ×5 + LINK-FORKMAIN-ABSENT-OK ×5 + DRIVER-SHIM-OK ×5 (all 3 jobs). Bundle guards: A-fresh + C-S2 + C-S24 intact ×3; asm tree clean ×3. RUNDIRs `/data/gpfs/projects/punim2657/sfs_main/pota73_run_{33286981,33286982,33286983}/`, fetch tgz in each.

**3. Identity of the seat (login-node probe, GT-relative; absolute frames float so relative-edge is the currency, per T39 strict).**
S24 R1 snapshots place pieces 0,1,3 (= C01,C02,C04); S2 places 0,1 (both wrong).
Relative edges (identical ×3): 01-02 rel-ang ~180° (open); 01-04 ~179° (open); **02-04 rel-ang 2.52° / rel-tr 17.37mm** — the binary-seated edge is 02-04, rotation-seated with a translation floor. Under strict 5°/10mm relative-edge this is 0/3 — same translation-floor family as J's 10–18mm floor in T39 §5 (and T30/T31 theme). The E2E currency of this ticket series is the binary tally (cf. T68's 0/3+0/3 table): on that currency S24 = 1/3 edges ×3 = above 0, bar met. C02's clean lip alone (S2) seats nothing — the pair seats together; C01 remains unplaced (shredded at segmentation).
Render `artifacts/pota73/Csel_S24_seating_R1.png` (eye-checked): estimated 02-04 pair (C02 frame) has the same shape as the GT pair — C04 red tracks gray with a visible vertical offset (the 17mm floor, seen directly).

**4. Landing check vs the bar.** Gate recovery toward ORIG per-edge ✓ (C02 full, C04 with one link). E2E above 0 ×3 same-binary ✓ (S24 2/3+1/3 ×3). Controls green same runs ✓ (C ORIG 4/4+5/5 ×3; A 8/8+15/15 orig + fresh ×3). Repeats ≥3 ✓. Zero ORIG points ✓ (44-asterisk rule; ORIG evidence-only). No gate relaxation ✓. index_=1: no flag edits, noted above ✓. Renders eye-checked ✓ (2 PNGs). Spartan leftovers: `pota73_repro/` + 3 `pota73_run_*` dirs only.

**Successor proposal for lead:** (a) C01 needs walk-level/segmentation work (both branches miss — only unrecovered piece); (b) the 02-04 translation floor (17mm) is the next mechanism to chase (refinement-bias family, T30/T31); (c) strict-relative 0/3 means thesis write-up should quote binary 1/3 WITH the floor caveat, not as a full seat.
