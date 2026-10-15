# 13: Genuine piece-2 rim fix (last blocker to 8/8)

**What to build:** a real rim for piece 2 — the only sherd unplaceable in every arm so far, and the last blocker between the current 7/7 + 11/11 and the full 8/8 + 15/15.

**Answers:** E1

**Blocked by:** 11-patch-ablation-e2e (evidence below). Runs alongside ticket 12 (different files, different machines).

**Status:** ready-for-agent

**Starting position (from 11, job 33061722):** ablated p2 wall rim is a 48-point stub (traced 141.5mm) ending in a 3-point terminal segment; the assembler silently drops piece 2 at load (log reads P02 Breakline_0 then jumps to P03, no error); gate pairs touching p2 are 0/4 strict (min_d 19.95/3.07/77.58/1.18mm). The patch points are NOT the answer (they poison the search). Guard-kept by design per ticket 04 — this ticket replaces the stub with a genuine rim or a principled second-chance rule, with numbers. Spartan leftovers: `pota11_bundle/`, `pota06_bundle/`, ticket-04 guard analysis.

- [ ] Diagnose first: is the stub short because the wall rim is genuinely missing from the surface extraction, or because segmentation/guards truncate it? Pin the stage with file:line + measurements (gate probe is the fast loop — laptop-legal)
- [ ] Fix, then prove: p2 loads (no silent drop) + gate pairs touching p2 pass strict + E2E 8/8 + 15/15 with the same-binary ORIG arm alongside
- [ ] If the fix is a guard second-chance rule rather than a longer rim, state the rule exactly (thresholds + file:lines) and show it fires only on genuine fragments, with the false-positive check
- [ ] Laptop poll per sbatch with sacct State/ExitCode; render before/after for the p2 rim (view resolves the millimetre scale) + measurement pair; no commits; Comments-only edits; E1 update proposal in Comments
