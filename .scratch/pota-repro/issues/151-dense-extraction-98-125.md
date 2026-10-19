# True dense extraction at stations 98-125 — fill the honest void from our mesh

GOAL: GIVE THE WALKER GROUND TO STAND ON.

**Answers:** E1

**Blocked by:** 149 (thin line walks calmer/gate 1.31, honest uncovered exactly [(102,120),(169,171),(179,181)], residual weave gap-driven) + 147 (void 98-125 = 48mm with no extraction; parity interpolation was instrument-only, not banked) + 150 (face-side rule keeps extraction clean: keep align<=+0.5)

**Status:** ready-for-agent

**What to deliver:** TRUE extraction (mesh-sampled edge material at ~1.8mm author spacing, NOT interpolation) aimed at honest span (102,120) within arc 98-125, from our own C01 mesh: (1) extraction method named + why its dots are edge not face (face-side rule from 150 gates admissions at the source); (2) new-dot audit — count, spacing, face-side mix, how many seat on-arc; (3) re-walk of thin bag + new dots with M144 machinery verbatim: report uncovered (bar: (102,120) closed, remaining only small honest spans), gate, and topology flips/selfint vs thin-M's 13/15 and parity's 2/0 (bar: at-or-better than parity with coverage held). If the mesh holds no further lip material in the span (cf. ticket-50 S1 precedent: prove with the same starvation test, don't just report emptiness), say so with numbers and name the fallback.

**Starting position:** .scratch/pota149_repro/ (thin bag + honest spans), pota147 (station frame, void map), pota150 (face-side rule). Login-node numpy only for prototyping the extraction rule; if the extraction itself needs Spartan compute, say so in Comments and stop (do NOT submit jobs — lead stages that separately). New scratch pota151_repro/; renders under laptop artifacts/pota151/.

**Rules:** ORIG Bl_0 ruler-only; control = reproduce 149's thin-bag numbers first or stop; COMMIT NOTHING; Comments-only ticket edits.

- [ ] True extraction at (102,120): method + edge-not-face proof + dot audit
- [ ] Re-walk: uncovered/gate/topology vs bars
- [ ] Starvation verdict if mesh is empty (with numbers + fallback)
