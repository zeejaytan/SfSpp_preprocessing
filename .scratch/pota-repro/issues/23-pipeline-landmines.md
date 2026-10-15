# 23: Pipeline landmines — tmp_path wipe + mesh nondeterminism

**What to build:** two found hazards fixed, each proved by a rerun that used to fail silently.

**Answers:** E1

**Blocked by:** 21-piece2-wall-recovery (found, not touched, per one-variable discipline).

**Status:** ready-for-agent

**Starting position (ticket 21 Comments):**
- (a) Multi-iteration pieces silently lose ALL surfaces: `tmp_path` basename bug at `mesh_processing_headless.cpp:1915-1926`, dormant at baseline. Construct the triggering case (a piece needing >1 iteration), show the loss, fix, show the surfaces survive.
- (b) The mesh stage is nondeterministic run-to-run, so byte-identity is the wrong bar and every bundle-to-bundle comparison in the arc carries noise. Scope: find the nondeterminism source (threading? unordered map? unseeded sampling?), seed/fix it, and prove with two consecutive runs whose outputs are identical at the level the gate reads (rim files + surface composition, not just md5).

**Rules:** one landmine at a time (fix a, prove, then b); each fix minimal with the pre-fix failure demonstrated in the same ticket. Same-binary ORIG control wherever an assembly runs (must reproduce 8/8+15/15 or void). No behavior changes beyond the two fixes — the E2E numbers must not move (report gate + strict E2E before/after on Pot A as the no-regression proof).

- [ ] (a) trigger case + fix + surfaces-survive proof, exact file:line in the ticket
- [ ] (b) nondeterminism source + fix + two-identical-runs proof (gate-level identity)
- [ ] Pot A no-regression: gate 15/15 + strict E2E unchanged before/after
- [ ] Laptop poll per sbatch (`sacct` directly); job IDs + sacct states; no commits; Comments-only edits
