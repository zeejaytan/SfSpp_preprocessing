# 18: Refusal gate for unidentifiable fragments + H base-cap renders

**What to build:** the admission test ticket 17 prescribed — teach the finder to refuse fragments it cannot identify, and prove the refusal with a confusion matrix. Plus the eye-check on the base-cap claim.

**Answers:** E1

**Blocked by:** 17-poth-diagnosis (mechanism + thresholds + protocol below).

**Status:** ready-for-agent

**Starting position (from 17, jobs 33108716/33108743/33109148):** Pot H's collapse is a stack of three proven effects — base-type fragments (H01–H04: normals 2–25° off-axis, fragments touch the axis) with truth support 6–17% under the 10% minfrac floor; vote dilution + x1.1 dedup kills on multi-axis pieces; per-axis support below any identifiability floor (vote-best GM 1.6–1.85/pt on H vs ≤1.2 on all passing). Proposed gate (finder-observable only, no shipped key): REFUSE when BOTH (1) vote-best GM cost > 1.4/pt AND (2) round-1 peel-winner share < 0.20. Thresholds provisional — confirm on the full B–J distribution (especially J tails) in this ticket.

- [ ] Implement the gate in a Spartan-side experiment copy (new `p18-stage/`; `p15-stage/` stays frozen); run ALL B–J pieces (155); report the confusion matrix: refusals among current fails (want ≥9/11 H + D30/J-tail fails) vs refusals among current dirpass pieces (want ZERO — especially G07, D32, small-J passes)
- [ ] If thresholds need moving to meet the confusion bar, move once with the full matrix before/after; no second tuning round on your own
- [ ] Renders: H01–H04 meshes with shipped axis drawn, top + side views, mm scale, equal aspect, to `artifacts/pota18/` — the base-cap geometry claim needs the lead's eye before H3 closes (Needs-eye:)
- [ ] Job IDs + sacct states; no commits; Comments-only ticket edits

**Successor:** E2E gate proof on admitted fragments (refusals excluded by rule, not by hand).
