# 249: Pot C diagnosis — why fresh seats 2/4 vs author 4/4

**What to build:** diagnosis only — explain the fresh-vs-author Pot C seating gap (C01 placed-but-wrong + C03-Bl1 ridge-lock), unchanged pre/post density restore. No repair.

**Answers:** E1

**Blocked by:** 246 (Pot A 8/8+15/15 + Pot C 2/4+1/5 bar on restored-density main), 197 (D-only 2/4+1/5 bar), 98 (SXC 2/3+1/3, C01 placed-but-wrong signature), 34 (assembly-side floor).

**Status:** results-in
**Working in:** subagent session-61c820f6 (2026-10-22)

- [ ] C01: lane coverage/length vs author per lane + pose error (rot deg, offset mm/cm) vs GT with physical reading
- [ ] C03-Bl1: ridge-lock evidence (which points lock, where on rim)
- [ ] Verdict per piece: method-failed vs measurement-broken vs reference-wrong
- [ ] Weight statement (pots/runs); Pot A 8/8+15/15 guard re-verified or drift noted

## Comments (worker, 2026-10-22 — diagnosis only, COMMIT NOTHING)

### Setup (boundary deviations stated, read-only honored)
- Laptop: fresh detached worktree C:/PR/SfSpp_preprocessing-249 @ 4e9283b (== origin/main). Main worktree untouched except this ticket file (204-edit still M, uncommitted).
- Spartan: live checkout /data/gpfs/projects/punim2657/sfs_preprocessing is BEHIND (f4add97 vs origin/main 4e9283b) with skip-worktree/untracked state — left untouched per 239-246 precedent, NO pull (would need conflict resolution). Fresh clone /data/gpfs/projects/punim2657/sfs-potC-249 @ 4e9283b clean instead of "under sfs_preprocessing" (that path IS the live checkout; sibling follows the 246 sfs-potAC-246 pattern). No builds, no edge/assembly/mesh/splitter writes anywhere: scoring-only login-node python over 246's recorded outputs + fresh-vs-ORIG lane PCDs.
- Scoring scripts (login node, read-only): sfs-potC-249/score249.py (lanes+jumps), score249b.py (reverse coverage, excursion location), score249c.py (pose attempt — superseded, see frame note).

### (a) C01 lanes — full rim captured PLUS ~45% off-rim excursion (corrects the "short lanes" premise)
- Bl0: fresh n=319 vs author n=211; arc length 670.2mm vs 378.2mm (1.77x). Forward med/cov 0.74mm/66.5% (reproduces 246 to the decimal); reverse coverage 100% — every author point within 2mm of fresh, zero author gaps. 1 jump>10mm (idx 126).
- Bl1: fresh n=360 vs author n=230; length 745.8mm vs 413.5mm (1.80x). Forward 0.73mm/64.2%; reverse 100%. 1 jump>10mm (idx 9).
- Where the extra length goes (side view + ranges): Bl0 fresh z-max 444.5 vs author 433.3 (+11mm above rim top), radius dives to r=1.1mm vs author r-min 24.3mm — the trace leaves the lip, climbs over the top edge and runs across the interior toward the vessel axis. Bl1 same shape: z-max 451.2 vs 436.0 (+15mm), r-min 0.9 vs 30.1. Eye-checked overlays: black author ring tracked then long blue excursion (see PNGs below).
- Physical reading: the tracer walks the whole true rim correctly, then keeps walking off it — ~292 of 670mm (Bl0) is non-rim interior/top-edge path. The matching stage sees a lane that is the right rim with a long wrong tail, and seats C01 wrong. Pose error (246 strict kabsch recipe, authoritative — see frame note): C01 rot 93.42deg trans 440.57mm (44cm). A right-angle-plus turn with the piece nearly half a metre from its seat: visibly, grossly wrong — not a near miss.
- Verdict C01: (1) METHOD-FAILED — the tracer, not the ruler, not the reference. Measurement sound (gate reproduces 246 exactly; rev-cov 100% proves the mesh contains the full rim). Reference sound (ORIG C seats 4/4+5/5 in the same vehicle, same run).

### (b) C03-Bl1 — smooth runaway on the wrong path, locks onto almost nothing (quantified "ridge-lock")
- Fresh n=366 vs author n=120; length 709.8mm vs 273.7mm (2.6x). Forward med/cov 12.36mm/13.1% (== 246); cross-lane vs author Bl0 6.35mm/0.5% — far from BOTH author lanes. Only 1 jump>10mm (idx 10): the trace is smooth/coherent, not a jittery braid — it confidently walks the wrong ridge.
- Which points lock: within 2mm of author Bl1 just 48/366 (13.1%); within 2mm of author Bl0 just 2/366 pts (idx 229-230, mid-rim) — i.e. essentially NO lock onto either true lane. Reverse: only 38.3% of the author rim captured; author gaps at nearly every segment (1-2, 9-10, 14-18, 22-27, 32, 36-46, 51, 53-54, 56, 58-94, 96-99, 102-103 of 120) — misses spread around the whole rim, no single occluded patch.
- Where it goes: fresh z-range [453.0,525.5] vs author [453.2,480.8] — climbs ~45mm above the rim top; radius out to 74.0 vs author max 50.5 — leaves the break edge onto the outer wall/upward. Side-view overlay shows the blue trace ringing the black author loop only in patches then sweeping high and wide.
- Verdict C03-Bl1: (1) METHOD-FAILED — tracer follows a non-break ridge (exterior wall/lip), smooth runaway. Measurement sound, reference sound (same ORIG control). The word "ridge-lock" is kept as: locked onto A ridge, just not the break ridge.

### Guards + controls (no drift)
- C02 Bl0 0.65/94.5, Bl1 0.47/95.3; C04 Bl0 0.75/89.2, Bl1 0.55/99.3; C03-Bl0 0.76/91.7 — clean, == 246. All 12 Pot C lanes re-verified STRAIGHT-class except C03-Bl1.
- Seat tallies re-read from pota246_e2e/pota246_run_33673764/*_binary.log on disk (no new jobs): A_fresh 8/8+15/15, A_orig 8/8+15/15, C_fresh 2/4+1/5, C_orig 4/4+5/5 — == 246, no drift. sacct: 33669861/33670678/33670885/33673764 all COMPLETED 0:0.
- Full strict table (246 recipe, kabsch keep [1,2,3] Pot C / [1..7] Pot A): C_orig 4/4 (all <=2.05mm/0.69deg); C_fresh 0/4 — C01 93.42deg/440.6mm, C02 134.55deg/316.9mm, C03 93.90deg/100.9mm, C04 125.08deg/259.0mm. Every fresh piece turned a quarter- to half-turn (93-135deg) and displaced 10-44cm (a vessel diameter or more).
- Frame note (why strict, not naive): direct est-vs-GT per-piece comparison is INVALID — assembly world frame differs from GT frame (naive C_orig shows a uniform ~152deg/33mm global offset on all 4 seated pieces). GT bundle-vs-original md5 identical (e6209ecb), so the gap is frame, not data. Strict alignment is the honest pose metric; 246's triplet enumeration (all triplets >=60deg off) confirms no rigid subset exists in C_fresh.

### (c) Classification summary
- C01: method-failed. C03-Bl1: method-failed. Neither measurement-broken (gate reproduces 246 to the decimal on both lanes) nor reference-wrong (ORIG 4/4+5/5 same vehicle/run; GT md5-identical).
- Density restore exonerated for Pot C: failure mode identical pre/post restore (98 SXC signature + 246 fresh == 197 D-only 2/4+1/5 bar).

### (d) Weight
- One pot (C, 4 pieces), one E2E run (246 job 33673764) + deterministic tally logs + login-node rescoring. Single-object lead, not a conclusion. Pot A guard (8 pieces, 8/8+15/15 both arms same run) carries the "pipeline sound" half of the claim.

### Overlays (author black #222222, fresh blue #0072B2; titles carry med/cov/length numbers)
- C:/PR/SfSpp_preprocessing-249/artifacts/pota249/C01_Bl0_vs_author.png (3D + x-z side; excursion over top edge + interior dive)
- C:/PR/SfSpp_preprocessing-249/artifacts/pota249/C01_Bl1_vs_author.png (same pattern, +15mm z, r-min 0.9mm)
- C:/PR/SfSpp_preprocessing-249/artifacts/pota249/C03_Bl1_vs_author.png (smooth runaway +45mm z, r-max 74mm; only patches on author ring)

### Verdict
Pot C fresh 2/4 vs author 4/4 is a TRACER failure on two lanes, unchanged by the density restore: C01's lanes capture the full true rim but grow ~1.8x tails off the rim (interior/top-edge excursion), corrupting matching (C01 seated 93deg/44cm off); C03-Bl1 never finds the break ridge at all (2.6x runaway, 13% near author). C02/C04/C03-Bl0 lanes are clean and the ORIG control seats fully — the mesh, the metric, and the reference are all sound. STAGED FOR LEAD: no fix proposed, nothing committed.

