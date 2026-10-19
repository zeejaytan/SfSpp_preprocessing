# Drop the hole-ring, close the true-edge gaps

GOAL: THE CURATED EDGE IS THE TRUE BREAKING EDGE ONLY, AND THE WALK TRACES ALL OF IT.

**Answers:** E1

**Blocked by:** 166 (hole + flake + crumb in source data as received), 167 (through-hole not pipe),
168-cut (lead-run planar section: wall stops at rim both sides, air between),
149 (thin-line walk + honest uncovered spans), 144 (M144 recovery), 161 (mesh overlay).

**Status:** ready-for-agent

**User ruling (verbatim, 2026-10-20):** the mesh is not watertight -- it is an imperfect scan with unseen areas left open (not solid clay). Call the hole a special case: the mesh itself is defective. Remove the second ring (the false loop around the hole) and use what is left. Remaining problem: the walker still cannot trace the whole real breaking edge -- gaps are left. Solve that.

**What to deliver:** (a) CURATION: drop the hole-ring dots from the edge bag (dots attributed to loop1 -- nearest-loop == loop1 per 166, ~73 FAR; verify none sits on ORIG first: ORIG stays >=35mm from every loop per 166, so the cut cannot eat true rim). Re-gate the curated bag vs ORIG: every kept dot within tolerance, every dropped dot justified by loop attribution. (b) COVERAGE: walk the curated bag (thin-line + M144 recovery as starting recipe, NO retune without evidence) and score ORIG-rim coverage: which ORIG stations are visited, which gaps remain, each gap named (span / veto-eaten / admission-missing). (c) Close -- or honestly bound -- every remaining gap: admission, trigger, or upstream cause per gap. A gap that cannot close lands with its owner, not silence.

**Bar:** curated edge contains no hole-ring dots (count 0 within loop1 footprint + rim band) AND walk covers the full ORIG rim at gate at-or-better-than fresh (5.61/22.9) with zero unowned gaps. Failing that: honest negative with per-gap owners.

**Starting position:** 166 Comments (loops, flake, distances, scripts), 167 Comments (depth numbers), 149/144 Comments (thin walk + recovery recipe), 160/162 Comments (labels, gate scripts). Lead-run cut scripts in .scratch/pota168_repro (p168_cut.py, p168_cut2.py -- MINE, read-only, do not overwrite; use own scratch pota168b_repro/). Renders artifacts/pota168b/.

**Rules:** dataset read-only (the DS mesh IS the source -- no full-res exists, verified byte-identical both sides); same-binary ORIG control alongside or void; COMMIT NOTHING; tickets 39-167 read-only; Comments-only ticket edits; sacct recorded; eye-check renders.

- [ ] hole-ring dots dropped, curation gated (0 in footprint, ORIG untouched)
- [ ] curated-bag walk + ORIG coverage score
- [ ] every gap closed or owned with cause
- [ ] Verdict + render paths
