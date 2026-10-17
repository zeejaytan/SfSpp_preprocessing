# 64: Pot C null diagnosis — why zero, when A scores full marks

**What to deliver:** the measured reason Pot C fresh seats 0/3+0/3 while the same chain scores 8/8+15/15 on A — prep, search, or material.

**Answers:** E1

**Blocked by:** 61 (C: ORIG 4/4+5/5 ×3 green; fresh flagged 0/3+0/3 ×3, forest 307 pruned 7–8; seated [] ×3; P3 UNPLACED; 5 GT edges off 360–730mm; ceiling 0) + 39 (C unflagged baseline also 0/3+0/3 — flagging is NOT the cause on C) + 41 (B-diagnosis pattern: kill-site per true edge) + census (C per-pot counts in ticket 01).

**Status:** ready-for-agent

**Starting position:** C is the extreme case: same vehicle, same chain, A perfect, C null. Candidate causes: (a) PREP — C rims fail the gate or C axles wrong (check: gate per-edge strict on C fresh rims; axle errors vs shipped); (b) SEARCH — true edges die in filtering (forest 307 vs ORIG's?; pruned only 7–8 — where do the 5 GT edges die: RP, pairwise, beam?); (c) MATERIAL — C03 ingest-off (denominator already excludes it); small pot (3 scored pieces?) so one kill = total zero; P3 UNPLACED (refusal — why?). Bundle reference: pota39 C bundle + pota61 C flagged bundle (read-only); C census counts in issues/01. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** diagnosis FIRST (login-node screening per T53 precedent; E2E only to confirm a mechanism); no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 for any E2E claim.

- [ ] Gate + axle check on C fresh (prep verdict per piece)
- [ ] Kill-site per GT edge (where each true edge dies, with numbers)
- [ ] P3-unplaced reason (refusal statistics)
- [ ] Verdict: prep / search / material — with the single binding cause if one exists
- [ ] Job IDs + sacct states (or explicit screening-only)

**Successor:** remedy ticket per verdict (C is small — the fix may be one kill-site).
