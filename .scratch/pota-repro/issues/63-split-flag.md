# 63: Split the flag — matchable-rim vs veto-rim

**What to deliver:** per-edge veto kill counts, then a split flag (rim-for-veto vs matchable) with E2E proof on D/I/J.

**Answers:** E1

**Blocked by:** 62 (index_=1 conflates veto-rim with do-not-match; channels code-verified: LCS zeroing + KD exclusion + H_rim veto boundary; per-edge veto kills NOT printed in BASE logs — VERBOSE arm needed first; blanket revert contra-indicated by J).

**Status:** ready-for-agent

**Starting position:** two phases: (a) VERBOSE arm — instrument or enable verbose logging of per-edge veto kills (H_rim veto at feature_matching.cpp:1228-1237, PC_ at ranking_system.cpp:1831-1837) on D/I/J flagged vs unflagged bundles; count which true edges the veto kills. Assembler-side scratch copies only (never repo source edits — stage patched copies per P22FIX precedent). (b) SPLIT — separate the matchable flag from the veto flag (match recalled true spans, veto only foot/base spans), E2E ×3 same-binary on D/I/J + controls green (per-pot ORIG + A 8/8+15/15) + gates green; cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** phase (a) may be login-node screening (T53 precedent); phase (b) needs full E2E ×3 + identities + renders (eye-check); no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [ ] VERBOSE kill counts per edge (flagged vs unflagged, D/I/J)
- [ ] Split-flag remedy + E2E ×3 with identities
- [ ] Job IDs + sacct states

**Successor:** roll the split flag across remaining pots if D/I/J prove it.
