# Void map — where the bag has no dots, and which input step owns each gap

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 118 (presplit shatters the cleaned bag too: 35 islands; bag lacks chainable structure at honest stepping) + 110 (same on filtered bag) + 112 (REFUSAL at bridges) + 111 (lip not globally under-sampled, but gap tail max 12.43mm) + 103 (cleaned bag, gate 4.68)

**Status:** ready-for-agent

**What to deliver:** map every structural break. Take 118's 35 presplit components on the 103 cleaned bag: seat each component's end dots on ORIG Bl_0, list the ORIG index ranges with ZERO bag coverage (true voids — no dots at honest stepping range), and for each void read the mesh context: segmentation label (Surface_0/1?), boundary-test distance, fold/constriction proximity (99's (38,191)/(39,401)?), scan-border proximity, local mesh edge fineness. Then name an OWNER per void: which input step failed to produce dots there (segmentation cut it away? boundary test blind? ROR deleted? snap dragged off? mesh too coarse?). Distinguish VOID (no dots where the true arc passes) from EATEN-BRIDGE (dots present but consumed — 112's pattern) per break. Success bar: every one of the 35 breaks classified (void vs eaten, void extents in ORIG indices, owner named with file+line) AND at least one void-owning step with a stated one-variable fix direction. If all breaks turn out eaten-bridges with zero true voids, say so — that kills the structural story and re-points at the walker.

**Starting position:** pota103/110/112/118_repro/ (cleaned bag, presplit components, stall freezes, checkpoints), C01 fragment mesh + segmentation outputs. Login-node numpy only — no Slurm, no E2E. New scratch pota119_repro/; render under laptop artifacts/pota119/ (ORIG arc coloured by coverage: dotted vs void spans, owners labelled).

**Rules:** control reproduces 118-presplit first (35 comps, max 27, emit 21, all to 2dp) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; classify-first, fix-direction second.

- [ ] Presplit reproduced + every break seated on ORIG
- [ ] Void-vs-eaten classification with extents + mesh context per void
- [ ] Owner named per void (file+line) + fix direction
- [ ] Verdict + coverage render
