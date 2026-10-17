# 61: Roll-out — Arm C recipe on Pots C/D/E/H/I/J

**What to deliver:** per-pot ORIG-valid + fresh ×3 + identities + ceilings on the five remaining pots — the cross-pot table.

**Answers:** E1

**Blocked by:** 60 (Arm C transfers to G: 4/7+3/10 ×3, ORIG-valid green, ceiling declared) + 59 (Arm C = F recipe) + 39 (per-pot ORIG baselines as validity bars) + 51 (ceiling doctrine).

**Status:** results-in (worker 2026-10-17, COMMIT NOTHING; lead owns checkboxes + roll-out call)

## Comments (worker, 2026-10-17 — Arm C rolled to C/D/E/I/J; H honestly not run)

**Verdict: Arm C transfers unevenly. J improves (0 → 2/10+1/18 ×3, first
above-zero transfer); C holds at zero; E shows no consistent gain (mixed
×3); D and I come in below their unflagged baselines (small but consistent
×3). ORIG-validity green on all 15 runs — cure-potA @ bffefb6 vehicle VALID
on all five pots. H was not run: no H bundle staged, no finder_axes_H, no
39 H baseline to compare against (evidence §5). No commits; tickets
39–60 untouched (read-only); original flaggers untouched (p61C copies live
on Spartan). Poll was sacct directly throughout; all 15 stage jobs + 5
flag jobs sacct COMPLETED 0:0.**

**0. Provenance.** Fresh Spartan work area pota61_repro/ only (39 lanes
read-only). All 5 bundles cp -a COPY-IDENTICAL (diff -rq) from
pota39_repro/prep/pota39_bundle_<P>. Flaggers p61C_<P>_flagger.py md5
1f2019b6c14d549a0e0589e8c5062856 = laptop p59C (chain p59C→p60C→p61
verified). Flag jobs COMPLETED 0:0: 33266319 C, 33266320 D, 33266321 E,
33266322 I, 33266323 J (sparse: C 1, D 6, E 4, I 6, J 3 files; foot-top
flags admitted where ORIG-tops matched). Stage sbatches generated from
60's G-stage via replace table (+ same-node /tmp collision fix, E
`// #define POT_E` typo-tolerant overlay sed, per-pot validity comment).
Gate asserts LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK green
in all 30 arms; DATA md5 asserted per file. Laptop artifacts/pota61/:
fetch tgz + extracted dirs, orig breakline tgz, p61_identities.py (POT/N
parameterised; no-GT pieces excluded from scoring), per-pot renders +
seating PNGs (all eye-checked).

**1. Tallies (binary-printed). ORIG-valid FIRST, then fresh flagged ×3.**

| pot | ORIG ×3 (39 bar) | fresh flagged ×3 | 39 unflagged fresh | verdict |
|---|---|---|---|---|
| C (88/54/56) | 4/4+5/5 ×3 (bar ✓) | 0/3+0/3 ×3 (forest 307, pruned 7–8) | 0/3+0/3 | AT (zero) |
| D (58/61/64) | 22+53, 23+55, 22+53 (bars ✓ = 39 R2,R1,R2) | 12+15, 13+14, 13+15 (forest 10836, pruned 846–862) | 15+17 | BELOW (~−2/−2, ×3 consistent) |
| E (59/62/65) | 31/31+62/62 ×3 (bar ✓) | 4+1, 7+3, 3+2 (forest 24889, pruned 209–216) | 5+3 | MIXED (no consistent gain) |
| I (60/63/66) | 25/27+59/65 ×3 (bar ✓) | 5+2, 6+2, 6+2 (forest 8304, pruned 333–340) | 9+4 | BELOW (−3/−2, ×3 consistent) |
| J (89/55/57) | 8/11+16/21 ×3 (bar ✓, pruned 197–202) | 2/10+1/18 ×3 (forest 1837, pruned 46–53) | 0/10+0/18 | ABOVE (+2/+1, ×3 stable) |

(E R1 edge prints "1/62 (2.42%)": k=3 directed — one edge correct
one-way only; integer-truncated print. Same one-way mechanism explains
odd-k prints elsewhere.)

**2. Identities (recompute from disk T files, CountResult port 0.35/50).**
ORIG recompute = binary EXACTLY on all 15 runs (validates file mapping +
formula). Fresh:
- C: seated [] ×3; P3 UNPLACED (refusal auto-exclusion works); 5 GT edges
  off by 360–730 mm. Ceiling 0 — nothing to attribute.
- J: seated [5,10] via (5,10) ×3 stable (unplaced set wobbles P1/P2, tally-
  identical); ORIG seated [1–7,10], missing [8,11,12] (39's cluster note).
  Ceiling 2/10+1/18.
- D: R1 [1,2,4,6,9,13,19,20,24,27], R2 [1,2,4,6,8,9,13,19,20,24,27], R3
  [1,2,4,5,6,9,13,19,20,23,27] (14–15 coarse edges; core [1,2,4,6,9,13,19,
  20,27] stable). Ceiling 13/27+15/66 (R3 binary max).
- E: R1 [3,23,24,26], R2 [1,3,6,23,24,26,30], R3 [3,17,26]; near-misses
  (3,17: 0.15 rad/60 mm; 11,12: 0.15/84). Ceiling 7/31+3/62 (R2 only —
  not stable).
- I: R1 [7,8], R2 [1,3,5,17], R3 [3,17] (run-varying; only (3,17) repeats).
  Ceiling 6/27+2/65 (binary max; coarse names vary).

**3. Seated ∩ flagged ≈ ∅.** Flagged pieces: D P05/P11/P21/P22/P26/P28,
E P07/P10/P16, I P02/P05/P06/P13/P23/P24/P26, J P01/P03/P04. Coarse-seated
sets above contain essentially NO flagged pieces (only D-R3-P05 and
I-R2-P05 overlap, single pieces). The flagger's recalled segments do not
themselves seat — outcomes move via beam dynamics (J gains 2 on unflagged
pieces; D/I lose a little the same way). Direct flagger-attributable
seating ≈ 0 on all five pots; J's transfer is real but indirect.

**4. Measurement notes (ruler caveats, same ruler as 39 throughout).**
(a) Binary denominators exclude ingest-off pieces — verified in the
GT_graph print + degree arithmetic: C03 (2 edges), J03 (3), D27 (3;
zeroed row 27 in D log); no-GT J09/D22/I28–30 carry 0 edges. E/I denoms
are full. (b) Binary fresh sherd numerators can exceed disk-recompute
(D +2, I +2..4; C/J/E-R1/R3 match): the binary scores in-memory
fine-branch T_result (multi-graph composition + T_axis for unplaced
pieces), disk files hold first-graph coarse poses. Tallies stay
arm-to-arm comparable; piece-NAMING on fresh carries this caveat.
(c) One run is incidence-inexplicable offline (I R3: 6 sherds from k=4
directed) — flagged as a binary-internal anomaly; I's verdict (below
baseline) does not depend on it. Recommend lead confirm 60's F/G fresh
identities carry no same-caveat exposure before citing names.

**5. Pot H: NOT RUN, declared honestly.** POT_H exists in data_path.h
(11 shards) but: no pota61/pota39 H bundle staged (prep/ has no H
bundle), no finder_axes_H on Spartan (B/C/D/E/F/G/I/J only), 0 Pot_H
mentions in data_structure.cpp, and no 39 H baseline exists — nothing to
run against, nothing to compare to. Ticket 17's H-family base-type note
stands untested by this worker.

**6. Evidence.** Laptop artifacts/pota61/: fetch_{C,D,E,I,J}_R{1,2,3}.tgz
+ extracted dirs + orig_{C,D,E,I,J}_bl.tgz, p61_identities.py,
p61_render_{C,J,I}.py + p61_render_DE.py, seating PNGs
pota61_seating_{C,J,I,D,E}_C1.png (all 5 eye-checked: green seated pieces
track gray GT vessel walls; red scatter elsewhere). Spartan
pota61_repro/ (flaggers, flag reports, stage sbatches) +
sfs_main/pota61_run_<P>_<jobid>/ ×15 (binary logs, snapshots, fetches).

**7. Recommendation for lead.** Arm C is not a general uplift: J-only
gain, D/I small regressions, C/E flat — and the gain is not ON flagged
pieces. If E1 needs the mechanism, the next question is beam-dynamics
attribution (51-pattern per pot), not more flagging. Successor per ticket:
per-pot attribution wherever short of a credible ceiling (D, I, E).


**Starting position:** same Arm C recipe unchanged per pot (flagger copy per pot, T48b pipeline, no resampling, cure-potA @ bffefb6, repeats ≥3, ORIG-validity FIRST per pot vs 39's baselines, GT keys in class/data_structure.cpp + data_path.h). Order by size (small first): C (7 pieces), E, H, D, I, J — or worker's judgement; report per pot as it lands. Pot H note: axle-finder H-family was base-type multi-axis (ticket 17) — expect weak seating independent of rims; declare honestly. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** per pot: (a) ORIG-valid FIRST (void if miss); (b) fresh ×3 + identities; (c) gate green; (d) ceiling with names; renders per pot (eye-check); no commits; sacct-direct polling; Comments-only ticket edits.

- [ ] C/E/H/D/I/J: ORIG-valid + fresh ×3 + identities + ceilings
- [ ] Cross-pot table
- [ ] Job IDs + sacct states

**Successor:** per-pot attribution (51-pattern) wherever a pot falls short of a credible ceiling.
