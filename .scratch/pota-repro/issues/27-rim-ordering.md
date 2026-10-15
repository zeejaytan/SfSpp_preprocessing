# 27: Rim-ordering fix for p3/p4/p5 breaklines

**What to build:** ordered rim polylines for the three scrambled pieces — the bundle-side root cause ticket 26 proved, and the last known barrier to strict 8/8 + 15/15.

**Answers:** E1

**Blocked by:** 26-rp-starvation (teleport evidence below).

**Status:** ready-for-agent

**Starting position (ticket 26, jobs 33135333/33136703, ORIG controls valid):** RP is exonerated — true edges survive it. The killer is `SingleOverlapTest` (thr 100) deleting 323 fresh vs 5 ORIG, and the faithful port proves why: at GT seating, fresh-vs-ORIG overlap areas are 4-8: 673/14, 1-3: 429/4, 3-5: 2563/10 (2-8 clean 16/22). Rim points agree <1mm — the defect is segment ORDER: fresh Bl_0 mid-run teleports (p3: 12 jumps ≤93mm; p4: 15 ≤29mm; p5: 7 ≤48mm; ORIG ≤5mm everywhere), eye-confirmed in `artifacts/pota26/pota26_p3_teleports.png`. No search-side threshold separates GT-true areas (to 2563) from false — this must be fixed in the rim walk, T24-pattern (minimal, piece-scoped, one variable).

**Rules:** fix the walk ordering for p3/p4/p5 Bl_0 (same discipline as SFS-T24: prove the walk guilty vs its appendages first, then the minimal piece-scoped fix). Rebuild from committed sources in a fresh Spartan-side experiment copy. Same-binary ORIG control in the same job (must reproduce 8/8+15/15 or void). Acceptance is the STRICT bar only (5°/10mm relative-edge): gate 15/15 + strict 15/15 fresh at k=5/b=3. If strict passes, report SFS-T24 + RP ablation + CheckGraph-150 + ordering fix as ONE landable set; if not, report — no partial claims.

- [ ] Teleport count per piece before/after (fresh ≤ ORIG's ≤5mm family max); composition check (rim within ~1mm of true wall)
- [ ] Rerun gate + E2E k=5/b=3 (with the staged relaxations from sfs_p22fix_src — verify diff first; PC_ untouched)
- [ ] Laptop poll per sbatch (`sacct` directly); before/after seating render + measurement pair; no commits; Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain.
