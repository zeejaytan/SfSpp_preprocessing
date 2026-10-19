# Author-density parity — does author-spaced dots stop the jumping?

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 146 (doubling refuted; denser TRUE bags strand earlier) + 89 (author = uniform 1.8mm closed resample) + user eye verdict 2026-10-19 (author dots look MUCH denser in-render; density is why their walk never jumps)

**Status:** ready-for-agent

**What to deliver:** a direct test of the user's observation, in two halves. HALF 1 — measure, don't assume: inter-dot spacing distribution of author ORIG Bl_0 (211) vs OUR on-arc dots only (bag dots within 2mm of ORIG, not the whole scattered bag — the bag totals lie because wall dots inflate them). Report medians + tails: is the author actually denser on-arc, by how much, and where (void spans vs everywhere)? HALF 2 — parity test: build a density-matched input from OUR side only (interpolate OUR on-arc dots along the walk to the author's measured spacing — no ORIG point may enter the bag; ORIG is ruler-only). Walk it with the 144-form recovery. Bar: jumps/zigzag vs M144 — flips + selfint strictly down with coverage held (uncovered 0, gate at/below 3.9736). If the parity walk smooths out, density is confirmed as the mechanism and the follow-up is true dense extraction at author spacing. If it still zigzags at author spacing, density alone is refuted as the cause and the verdict must say what the parity walk proves instead (e.g. ordering, face-side).

**Starting position:** .scratch/pota144_repro/ (M144 rule-form, 314 bag), pota142_repro/ (topology counters), ticket 89 (author 1.8mm reference). Login-node numpy only — no Slurm, no E2E. New scratch pota147_repro/; renders under laptop artifacts/pota147/ (spacing histograms author-vs-ours; parity walk vs ORIG with topology counts on-plot).

**Rules:** zero ORIG points in any bag (ORIG Bl_0 ruler-only); control reproduces 144's M144 marks first or stop; interpolation is admitted ONLY as the parity instrument and the ticket must state that it adds zero new edge information; COMMIT NOTHING; Comments-only ticket edits.

- [ ] Spacing measurement (author vs our on-arc, medians + tails + where)
- [ ] Parity bag (our-side only, author spacing) + walk/gate/topology vs M144
- [ ] Verdict: density confirmed (=> true-extraction follow-up) or density refuted (=> what instead)
