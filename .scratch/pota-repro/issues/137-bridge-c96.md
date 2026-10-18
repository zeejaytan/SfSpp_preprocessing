# Named-span bridge C96 — cross (96,97) without inventing dots

GOAL: MATCH AUTHOR'S INPUT.

**Answers:** E1

**Blocked by:** 136 (detection CLOSED — all 8 uncovered bridging-class) + 135 (hit-list #3: C96 bridge sketch — sequence the flanks, license a T13-class teleport across the named span only) + 118+117 (presplit-then-walk precedent: honest chaining needs licensed teleports) + 134 (M134d recovery form: envelope retreat <= walk's own max stride)

**Status:** ready-for-agent

**What to deliver:** the first bridging ticket. Problem: span (96,97) is filter-dead (rej81 r1-FAIL nnb=0) — no dot will ever be admitted there, so the walk must STEP across it. Rule (ORIG-free, stated before running): license exactly one teleport whose endpoints bracket ORIG[96..97] (flank slots on the [89..95]-side to the [98..]-side — concretize from the M134d freeze: nearest sequenced slots to each flank, stated first); the teleport is licensed ONLY across this named span (no general jump-shortening — all other jumps still gated as in M134d). Test: M134d-form walk + licensed C96 bridge on the 282 bag. Success bar (all must hold): uncovered below 8 AND the C96 span covered (O96/O97 within 5mm) AND gate at/below 4.2488 AND no UNLICENSED jump >=40mm AND the bridge stated as a general rule-form (named-span license derived from the walk's own flank slots — never ported coordinates). If the flanks cannot be sequenced into launch position (walk never reaches a flank), refute with the sequencing — that says bridging needs presplit-then-walk (118+117) and C96 waits for the presplit ticket.

**Starting position:** .scratch/pota134_repro/ (282 bag, M134d form, flank slots), pota135_repro/ (C96 precision: filter-dead rej81, flank geometry), pota118_repro/ (presplit precedent). Login-node numpy only — no Slurm, no E2E. New scratch pota137_repro/; render under laptop artifacts/pota137/ (bridge step on arc, walk vs M134d, gate, jump accounting licensed-vs-unlicensed).

**Rules:** control reproduces 134's marks first (290/278u/gate 4.2488/uncovered 8) or stop; read-only on all inputs (zero ORIG points; ORIG Bl_0 gate-evidence only); COMMIT NOTHING; Comments-only ticket edits; ONE licensed bridge, everything else gated.

- [ ] M134d reproduced + bridge rule stated (flank slots, license bounds)
- [ ] Bridged walk vs 134's marks (coverage, gate, jump accounting)
- [ ] Verdict + recipe or presplit-ticket refutation
