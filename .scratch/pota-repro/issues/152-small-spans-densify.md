# Small spans diagnosis + densify — why (169,171)/(179,181) stand empty

GOAL: NO HONEST SPAN LEFT UNEXAMINED.

**Answers:** E1

**Blocked by:** 151 (LIP-STRIP closed (102,120); remaining honest spans [(169,171),(179,181)]; mesh NOT starved there by assumption — never tested)

**Status:** ready-for-agent

**What to deliver:** (1) diagnosis per span — same starvation test as 151 (edge-face count per station, nearest-edge-face distance): is mesh material present but unadmitted (same letting-in disease) or is the mesh itself thin/hole here (true starvation)? (2) if material exists: LIP-STRIP-verbatim extraction (face-gated at source, mesh-sampled, dedup >=1.5mm) extended to these spans, dot audit (count/spacing/on-arc share); (3) re-walk with M144 machinery verbatim: uncovered/gate/topology vs 151's marks (6 / 1.27 / 17-18). If starved: numbers + fallback named (narrower license? chaining-class verdict like 137?).

**Starting position:** .scratch/pota151_repro/ (LIP-STRIP scripts verbatim), pota149 (thin bag). Login-node numpy only; Spartan-needing work stops with reasons. New scratch pota152_repro/; renders under laptop artifacts/pota152/.

**Rules:** ORIG Bl_0 ruler-only; control = reproduce 151's augmented-bag numbers first or stop; COMMIT NOTHING; Comments-only ticket edits.

- [ ] Per-span starvation verdict (material vs true hole, numbers)
- [ ] Extended extraction + dot audit (or fallback if starved)
- [ ] Re-walk vs 151 marks
