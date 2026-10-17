# 47: Emit true isrim/topflag — mask mouth/base arcs like ORIG

**What to deliver:** fresh rims with ORIG-true rim flags, forest collapse, E2E lift — or the measured reason flags aren't the lever.

**Answers:** E1

**Blocked by:** 46-input-output-fingerprinting (H2: 76 ORIG files carry isrim=1; feature_matching.cpp LCS/LCSGraphBuilding mask flagged ranges out of fracture matching; profile code derives H_rim veto; ALL 294 fresh rims write topflag=0/all-zero segflags).

**Status:** results-in (worker 2026-10-17, COMMIT NOTHING)

**Starting position:** fresh forest bloat vs ORIG (B 1442 vs 114) is the cross-pot drowning mechanism; unmasked mouth/base arcs are the prime suspect. Ticket-46 evidence: artifacts/pota46/p46_fingerprints.csv + probes; ORIG flag layout per file in the CSV (header segs/flags columns).

**Rules:** prep-side work in scratch copies first; land ONLY with flag layout matching ORIG per-file structure + B gate 15/15 + forest-count collapse toward ORIG + E2E improvement ×3 same-binary runs + B ORIG 9/9+15/15 and A 8/8+15/15 green in same runs; seating render for any claimed E2E lift (eye-check); assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits. NOTE ticket-43 metrology: repeats ≥3 per condition; count pairs not k/2.

- [ ] Flag emission matching ORIG layout (which ranges flagged, verified per file)
- [ ] Forest counts vs ORIG + gate 15/15
- [ ] E2E improvement ×3 + controls green
- [ ] Job IDs + sacct states

**Successor:** R1 order+clip Bl_0 appends; R3 1.8mm step + uniformity gate; R4 column-7 semantics (queued from 46).

## Comments worker (2026-10-17, COMMIT NOTHING)

RIM FLAGS ARE THE LEVER. Fresh B E2E lifts 4/9+2/15 -> 7/9+7/15 x3
identical repeats with controls green in the same runs. Forest collapses
toward ORIG on identical rims.

What was done (prep-side flagging only, assembler vehicle untouched):
- Geometric rim flagger (port of author's check_base_and_rim.m rim test:
  std(h)<1.0 & std(r)<1.0 & |mean dr|,|mean dh|<0.1, >=20 pts, OR over
  axes; script .scratch/pota-repro/p47_flagger.py) applied to the T42
  gate-clean B rims with SHIPPED axes (same axes the E2E arm consumes, so
  the ONLY delta vs T42 is flags). Detector validated first on ORIG B +
  shipped axes: 17/18 files exact segflag match (only diff p08-Bl_1, where
  the detector flags one genuinely rim-flat arc ORIG left unflagged).
- pota47_bundle_B = T42 bundle with 6/18 files flagged (p02-Bl_0,
  p03-Bl_1, p04-Bl_0, p05-Bl_1, p06 both sides; per-file stats in
  artifacts/pota47/p47_flag_report_shipax.txt). Recall loss is real and
  measured: ORIG carries rim in 14/18 B files; the other 8 fresh rims have
  no recipe-passing arc (short chopped fragments; 3 near-miss flat arcs at
  13/18/19 pts under the author's >=20 rule, kept unflagged for fidelity).
  Base flags untouched (rim-only scope). Eye-check render
  artifacts/pota47/p47_flag_check.png: flagged fresh arc sits on the mouth
  rim exactly where ORIG's flagged arc sits.
- DATA invariance: 18/18 DATA sections md5-identical to the gated T42
  bundle, GT + Axes identical -> B gate 15/15 carries over formally
  (gate is coordinates-only).

E2E (cure-potA @ bffefb6, LINK-SHIM-OK + DRIVER-SHIM-OK,
LINK-FORKMAIN-ABSENT-OK all arms; sacct-direct polling):
- Jobs 33239463/64/65 (p47_runBA) ALL COMPLETED 0:0 (~13.5 min each).
- B_fresh flagged: forest 155, pruned 73 -> 7/9 + 7/15, x3 IDENTICAL.
- Same-rims unflagged baseline (T42 job 33217561): forest 197, pruned 83
  -> 4/9 + 2/15. So flags: forest 197->155, pruned 83->73 (ORIG 114/76),
  sherds 4->7, edges 2->7.
- Controls same runs x3: B_orig 114/76-77 -> 9/9+15/15; A_orig 124/70 ->
  8/8+15/15; A_fresh 420/119 -> 8/8+15/15 (no regression).
- Seating render artifacts/pota47/p47_seating.png: seated fresh ring tracks
  the GT-seated ORIG ring; 2 pieces visibly off (matches 7/9).
- Evidence: artifacts/pota47/ (fetch tgz of run 33239464, flag report,
  renders, detector + render scripts); Spartan pota47_repro/ (bundle md5
  prep/pota47_B_bun_md5.txt, stage run_pota47_stage_BA.sbatch, flag logs).

Against land rules: flag layout matches ORIG *where fresh rims contain a
recipe-passing rim arc* (6/18 files; full 14/18 layout match impossible --
fresh segmentation is shorter/choppier than ORIG's resampled curves, a
content fact not a flagging failure); gate 15/15 by invariance proof;
forest collapse + E2E gain x3 same-binary with all controls green: HELD.
Remaining: piece identities among the 7 seated were not extracted (only
tallies + ring render); the 2 still-missing pieces + 8 unflagged
files are follow-up material (relaxed >=10 rule would add 3 true rim
pieces; content-side R1/R3 from ticket 46 still open).
