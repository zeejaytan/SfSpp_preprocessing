# Gate-form: credit crossings, not just dots

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 137 (floor proof: 8 is the floor on 282 under POINT-gate; licensed C96 segment passes 2.51/2.99mm from O96/O97; forwards: gate-form ticket on crediting crossings) + all gate tickets (5mm cover standard already in use)

**Status:** ready-for-agent

**What to deliver:** a gate-form ruling with measurements. Question: the campaign's cover standard is "within 5mm" — the point-gate credits an ORIG point when the nearest walk POINT is within 5mm. A licensed bridge SEGMENT passing 2.51mm from O96 is within the same 5mm by the same standard — is crediting it moving the goalposts, or applying the standard to the walk's actual geometry (segments, not just vertices)? Rule (stated before running): segment-credited cover = min over walk SEGMENTS of segment-to-ORIG distance, same 5mm threshold, licensed segments only (unlicensed jumps never credit). Measure on the M134d walk + R137 licensed bridge: recompute uncovered-8 under segment-credit, state which spans bank (expect C96 at 2.51/2.99; check C36/C46/C165/C173 segments too — M134d already bridges all 8 per 135, so every bridging segment gets measured). Success bar: segment-credit definition stated with its principled grounding (same 5mm, vertices-vs-segments argument for/against) AND recomputed uncovered list with per-span segment distances AND an explicit statement of whether the gate change is honest measurement or goalpost-moving (falsifiable: would segment-credit also bank spans on the 279/270 walks? check at least one earlier walk — if it banks everywhere, it's inflation; if it banks only genuinely-crossed spans, it's measurement).

**Starting position:** .scratch/pota137_repro/ (licensed bridge, segment distances), pota134_repro/ (M134d walk), pota128_repro/ (279 walk for the falsifiability check). Login-node numpy only — no Slurm, no E2E. New scratch pota138_repro/; render under laptop artifacts/pota138/ (per-span segment distances, recomputed coverage, falsifiability check).

**Rules:** reproduce 137's segment distances first (2.51/2.99) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; gate-form honesty first (report inflation if found).

- [ ] Segment distances reproduced + credit rule stated with grounding
- [ ] Recomputed uncovered (M134d + bridge) with per-span numbers
- [ ] Falsifiability check on an earlier walk
- [ ] Verdict: honest measurement or inflation, with evidence
