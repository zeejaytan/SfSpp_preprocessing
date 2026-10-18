# 82: E_G segfault cure

**What to deliver:** guarded Pot E bundle runs end to end.

**Answers:** E1

**Blocked by:** 78 (E2E 33300251/52/53 COMPLETED; E_G binary EMPTY — Hierarchy-Batch-P78 segfault ~0.4s at launch on E_G bundle while E_fresh/E_orig/A arms run in same RUNDIRs; E_G Bl_0 rims down to 15 pts vs 78-pt min in working E_BASE; two-loop check B–J stands) + 75 (SEL recipe that emitted the short fragments).

**Status:** ready-for-agent

**Starting position:** the guarded E bundle crashes the assembler at launch; prime suspect = sub-minimum rims in the loaded slot. In scratch copies of pota78_bundle_E_G: (a) identify the crashing piece (bisect by removal — one run per half, binary search); (b) cure per cause — pad/merge short fragments to a walkable loop, or refuse the piece explicitly (refusal-gate doctrine: refused pieces are declared, never silently dropped); (c) re-run E2E x3 same-binary. If the crash is not rim-size, bind the true trigger (malformed header? surface mismatch?) with evidence. Zero ORIG points in any fix; ORIG evidence-only.

**Rules:** land with E_G running + E2E at/above best fresh 7/31+3/62 x3 same-binary + controls green (E_orig 30/31+59/62, A 8/8+15/15) in same runs; renders (eye-check); E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats >=3; no gate relaxation without a mechanism.

- [ ] Crash-piece bisection + trigger bound
- [ ] Cure (pad/merge/refuse) + E2E rerun x3 or measured why-not
- [ ] Job IDs + sacct states
