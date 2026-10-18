# Void-map refresh on 279 — name every span's owner, pick the cheapest

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 129 (279-ABSOLUTE: all distinct groups sequenced, leftovers twins, stall refusal identical; honest road = greedy 206) + 119 (7-void taxonomy + per-void owners on the 270 bag) + 127/128 (chaining list [173]/[96..97]; [25] banked)

**Status:** ready-for-agent

**What to deliver:** the 119 analysis re-run on the 279 walk. Classify each of the 15 uncovered ORIG spans: VOID (no near-bag dots) vs EATEN (dots exist, walk consumed/ignored) vs BRIDGED (walk jumps over); name the owner per span from the known taxonomy (ROR deletion / boundary-blind / snap-drag / chaining-class / walk-refusal); state which spans the 128 admission + 129 freeze moved vs 119's map. Then PRIORITIZE: rank the spans by cheapest-next-yield (single-dot admission like 128 > span-localized detection like 123 > chaining like [173]) with a one-line rule-sketch per span. No new dots admitted, no walks beyond the 279 greedy/guard already on file — this is a reading ticket that ends with an ordered hit-list. Success bar: every one of the 15 uncovered spans classified with an owner AND an ordered hit-list with rule-sketches, OR an explicit statement that a span's owner is unknown (which itself becomes the next ticket).

**Starting position:** .scratch/pota119_repro/ (void taxonomy + owners), pota128/129_repro/ (279 walk, coverage deltas, uncovered-15 list). Login-node numpy only — no Slurm, no E2E. New scratch pota130_repro/; render under laptop artifacts/pota130/ (uncovered-15 map with per-span owners, hit-list order).

**Rules:** reproduce 128's uncovered-15 list first or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits.

- [ ] Uncovered-15 reproduced + 119 taxonomy restated
- [ ] Per-span classification with owner
- [ ] Ordered hit-list with rule-sketches
