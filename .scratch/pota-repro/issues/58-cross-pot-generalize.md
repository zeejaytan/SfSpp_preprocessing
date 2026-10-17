# 58: Cross-pot generalization — run the B recipe on C–J

**What to deliver:** per-pot fresh-vs-ORIG E2E tallies on Pots C–J using the banked B recipe — with per-pot ceilings, not 100% expectations.

**Answers:** E1

**Blocked by:** 49 (relaxed ≥10-pt flag rule → B 8/9+7/15; flagger p49_flagger.py) + 47 (paper-recipe flagger base, p47_flagger.py) + 48 (T48b direction-mirror pipeline) + 51 (8/9-shape ceiling doctrine: one weak contact missing is the realistic target) + 39 (ORIG-validity vehicle pattern: prove ORIG scores first per pot, then read fresh) + 40 (cure-potA vehicle @ bffefb6).

**Status:** ready-for-agent

**Starting position:** the banked recipe: (1) paper-recipe flagger + relaxed ≥10-pt recall rule, (2) T48b honest pipeline (no resampling — 50; raw sampling is signal), (3) cure-potA @ bffefb6 vehicle with LINK-SHIM-OK + DRIVER-SHIM-OK, (4) repeats ≥3 per condition (last-bit FP rule from 43), (5) same-binary ORIG control per pot must score like ticket 39's ORIG-valid baselines before any fresh tally reads. Per-pot GT keys from class/data_structure.cpp + data_path.h. Expect drowning-shape forests (39) and per-pot weak contacts (51-doctrine: ceiling = full seating minus weak contacts, declared per pot with names). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** per pot, in order: (a) ORIG-validity control FIRST (must match 39's per-pot ORIG baselines — else vehicle is void for that pot); (b) fresh E2E ×3 same-binary + identities; (c) gate 15/15-equivalent per pot; (d) declare per-pot ceiling with seated-piece names; renders per pot (eye-check); no commits; sacct-direct polling; Comments-only ticket edits. Start with ONE pilot pot (smallest: F or G — G was 7/7 on axle finder, F small), prove the recipe transfers, then roll to the rest. Do NOT touch tickets 49-57 files or flaggers (read-only reference; copy, don't edit).

- [ ] Pilot pot (F or G): ORIG-valid + fresh ×3 + identities + ceiling
- [ ] Roll-out C–J (minus pilot): same per pot
- [ ] Cross-pot table: recipe transfers or measured where-not per pot
- [ ] Job IDs + sacct states

**Successor:** per-pot weak-contact attribution wherever a pot falls short of its ceiling (51-pattern).
