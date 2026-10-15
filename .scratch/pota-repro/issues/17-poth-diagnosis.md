# 17: Diagnose the Pot H collapse (1/11)

**What to build:** a diagnosis, not a fix — one focused ticket answering why the frozen finder collapses wholesale on Pot H when it direction-passes 75% everywhere else.

**Answers:** E1

**Blocked by:** 10-axle-generalise (frozen cross-pot evidence below).

**Status:** ready-for-agent

**Starting position (from 10, jobs 33106488–33106709):** Pot H 1/11 — only H10 direction-passes (3.03°, position 21.97 over). H01/H03/H04 return nset=0 (finder finds nothing); the rest return 1–2 modes against 2–6 shipped axes, all direction-failed (13–85° off). Point counts 276–2119 throughout — small fragments, multi-axis everywhere. Frozen finder: `.scratch/pota-repro/p15-stage/axle_finder/` (committed). Compare with the passing small pieces that DO work (e.g. G pot 7/7, D01–D16) and with the D17–D32/J tails (same small-multi signature, partial passes) to isolate what makes H wholesale rather than partial.

**Hypotheses, in evidence order:**
1. **Below the span floor** — H fragments are smaller than anything in the fit set (V3b: ball patches catastrophic, thin slabs fail); check shape-span per H piece vs the passing smalls, and whether any H piece spans enough 2D shape to be identifiable at all (admission-test question).
2. **Multi-axis dilution** — 2–6 true modes split the vote below the minfrac/dedup floors (peel stops, modes killed by x1.1); check per-piece vote counts, peel traces, dedup kills vs shipped counts.
3. **Fragment-type difference** — H pieces are a different kind (base-heavy? trim? scrap?) whose geometry the wall-tuned vote cannot see; check surface classification + curvature profile vs wall pieces.

**Rules:** diagnose and propose — do not modify `p15-stage/axle_finder/` (experiment copies on Spartan only). One hypothesis at a time, each with the measurement that kills or keeps it. If H1 (span floor) survives, the deliverable includes the admission-test proposal (which fragments the finder should refuse, with thresholds) rather than a fix.

- [ ] Verdict: which hypothesis survives, with numbers (spans, counts, peel traces, curvature profiles)
- [ ] Fix or admission-test proposal: exact change/thresholds + re-validation protocol for the follow-up ticket
- [ ] Job IDs + sacct states; no commits; Comments-only ticket edits
