# 20: Piece-2 endgame

**What to build:** the last blocker — find why piece 2 cannot seat and fix it, closing Pot A at 8/8 + 15/15.

**Answers:** E1

**Blocked by:** 19-admitted-e2e (measurements below).

**Status:** results-in — worker run 2026-10-16: swap seats p2 4/4 strict, cause in our p2 rim (mesh identical, wall surface lost downstream); fresh never strict-seats (0/5). No source changes, no commits.

**Starting position (ticket 19, job 33113298, ORIG control valid 8/8+15/15):** everything seats except p2. Fresh-ablated arm: 7/8 + 11/15, p2 ~103°/232mm off, all other pieces within 1.3°/6.3mm of ORIG seatings. Patched arm: 7/8 + 7/15 with p2 unseated — the SFS-T13 second-chance rim poisons the search (3rd confirmation), so the fix is NOT more rim points. Per-piece rims seat cleanly (render `artifacts/pota19/pota19_orig_vs_fresh_seating.png`, lead eye-checked: closed ring both arms, p2 flung). The axle gate admits p2 (fresh 8/8 admitted) — rim shortness is invisible to it, noted as a gate-design observation, not this ticket's fix.

Suspects in order:
1. **p2 exterior wall at the mesh stage** — compare fresh vs ORIG p2 surfaces and rims point by point (the 171-pt scrap vs 11k wall from ticket 04 is the designed exception; check whether the mesh-stage exterior wall for p2 differs from ORIG beyond the rim walk). Swap experiment: ORIG p2 rim + fresh rest — if p2 seats, the fault is in our p2 rim/surface, not the search.
2. **The beam's 103°-off p2 preference** — if the swap still fails, the search prefers a false seating; probe why (p2's 4 gate pairs: which pass, which fail, and what the beam scores the true vs false seating).

**Rules:** no finder or pipeline source changes except the proven-minimal fix for the diagnosed cause (one variable at a time; SFS-T13 stays as-is — its search poison is measured, not debated). Rebuild bundles from committed sources only; same-binary ORIG control in the same job (must reproduce 8/8+15/15 or void).

- [ ] Swap experiment first (ORIG p2 rim into fresh bundle): seats → suspect 1 confirmed, fix our p2 surface/rim; still fails → suspect 2, probe beam scoring
- [ ] Fixed arm: gate + E2E at k=5/b=3, target full 8/8 + 15/15 fresh
- [ ] Laptop poll per sbatch (`sacct` directly); before/after seating render + measurement pair; no commits; Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain.

## Comments (worker, 2026-10-16)

Swap-first, no finder/pipeline source changes, no commits. Spartan pulled
`--ff-only` to b8ec4d5 (laptop HEAD; diff vs 84ba640 is ticket/spec/intent
only — bundle sources identical). Run scripts are new untracked files in
`Temp/potsac-p20-run/`; swap bundles `pota20_swap0/` (`swap01/`) are `cp -r`
of `pota19_bundle/` with ONLY the named p2 Breakline files replaced by the
authors' (md5-verified); `diff -rq` confirms nothing else differs. Laptop
staging under gitignored `artifacts/pota20/`. `slurm_poll.sh` still exits
immediately — all polling via `sacct` directly.

**Jobs (all `sacct` State COMPLETED ExitCode 0:0):**
33114754 p20A compare (numpy point-by-point, 7 s); 33114755 p20D assembly
(4 arms, 13:41); 33115534 p20E repeats (6 arms — orig + 3x fresh + both
swaps; the sed kept the swap lines, bonus repeats, no harm — 26:39).
Recipe = ticket-19 p19D verbatim (same SIF, same shim, k=5/b=3).

**Suspect 1 point-by-point (job 33114754, world frame via GT T2; GT files
bundle-identical, so cross-bundle comparison is valid):**
- Input meshes BYTE-IDENTICAL (md5 985e4eb1 both, 55814 verts). The wall is
  NOT lost at the mesh stage — it is lost downstream of the mesh.
- Fresh p2 S0 (11263 pts) IS a full wall: sits on ORIG S1 at med 0.40 mm,
  99.6% of ORIG S1 within 2 mm (S0/S1 labels are swapped vs ORIG).
- Fresh p2 S1 = 171-pt scrap matching NEITHER ORIG wall (med 2.78 vs ORIG
  S0 / 3.35 vs ORIG S1; <1% of either ORIG wall within 2 mm of the scrap;
  scrap bbox z 12.5–18.7 mm vs walls z −16…+19 mm). One wall's surface
  extraction collapsed to a ~3 mm-offset scrap.
- Fresh Bl0 (179-pt second-chance walk): full span (diag 133.1 vs 130.5 mm)
  but ~3 mm off BOTH ORIG rims (med 3.23 vs Bl0 / 3.02 vs Bl1; 24–48% <2mm).
- Fresh Bl1 = 18-pt stub sitting ON the true Bl0 path (med 1.42 mm, 78%
  <2mm) but covering only 9.5% of it; 0% near ORIG Bl1 (med 5.33 mm).

**Swap experiment (the decider):**
- Job 33114755: ORIG control 124/70, 8/8+15/15 (VALID). Fresh 584/75,
  binary 8/8+15/15 but STRICT (5deg/10mm relative-edge, p19_score.py rule)
  11/15 with p2 ~10.6deg/33–43mm off neighbours. swap0 (ORIG Bl0) 371/74
  STRICT 15/15. swap01 (ORIG Bl0+Bl1) 371/72 STRICT 15/15.
- Job 33115534 repeats (identical inputs): orig 124/70 8/8+15/15; r1
  584/70 binary 11/15, strict 10/15 (p2 ~101deg + borderline 6-7 at
  2.1deg/12mm); r2 584/74 binary 15/15, strict 11/15 (p2 ~10.8deg); r3
  584/72 binary 11/15, strict 10/15 (p2 ~101deg); swap0 371/73 binary
  15/15 strict 15/15; swap01 371/71 binary 15/15 strict 15/15.
- Scoreboard, identical-input fresh rim (forest always 584): 0/5 strict
  15/15 (p2 errors 10deg twice, ~101–103deg three times incl. ticket 19).
  ORIG p2 rim: 4/4 strict 15/15. Suspect 1 CONFIRMED — the fault is our p2
  rim/surface content, not the search. Suspect 2 not needed as cause (beam
  seats p2 correctly every time given a true rim); beam nondeterminism is
  real though: pruned counts 70/72/74/75 on identical inputs, and the false
  p2 pose varies 10deg vs 103deg run to run.

**Two measurement observations for the lead (not this ticket's fix):**
1. The binary's edge bar is loose: it reports 15/15 with p2 ~10.6deg /
  33–43 mm off (job-1 fresh, r2). Binary 15/15 ≠ p2 correctly seated —
  strict relative scoring is the ruler that sees p2.
2. The axle-observable gate (ticket 19) admits p2 while the E2E-relevant
  content (wall surface + rim path) is ~3 mm off — same blind spot.

**Fixed-arm target NOT met:** no fresh bundle reached strict 8/8+15/15
(0/5); the ticket's "fix our p2 surface/rim" is a surface-extraction repair
(stage downstream of the identical mesh — exact file:line not yet pinned,
so no source change was attempted: one variable at a time, nothing proven
yet). Swap arms are the existence proof the untouched chain seats Pot A
the moment p2's rim is true.

**Render:** `artifacts/pota20/pota20_orig_vs_fresh_vs_swap.png` — placed
fresh Breakline_0 rims under each arm's T (arms globally aligned on non-p2
pieces first, since global placement is arbitrary run to run: packs sat at
~2/93/177deg across runs). Eye-check: closed ring all arms; fresh p2
(orange) escapes the ring top (~10deg), swap p2 sits in the ring. Before =
`artifacts/pota19/pota19_orig_vs_fresh_seating.png` (p2 flung 103deg).
Measurement pair = strict tables above + `p20_score.py` rerun script.

**Leftovers:** Spartan `Temp/potsac-p20-run/` (scripts, `p20fetch*.tar.gz`
contents, job outs), `pota20_swap0/`, `pota20_swap01/`,
`sfs_main/pota20_verify_33114755/`, `sfs_main/pota20_verify_33115534/`
(4 + 6 arms: per-arm outer/binary/cmake/make logs + Result snapshots).
Laptop `artifacts/pota20/` (T files, rims, scorer, render, PNG).

**Proposed successor (not started):** ticket to recover p2's exterior-wall
surface at the extraction stage downstream of the mesh (start from the
171-pt scrap vs 13455-pt ORIG S1 + the ~3 mm rim offset above), then
rebuild-from-committed + same-binary ORIG control + strict 15/15 bar —
binary 15/15 alone must not be the acceptance.
