# 82: E_G segfault cure

**What to deliver:** guarded Pot E bundle runs end to end.

**Answers:** E1

**Blocked by:** 78 (E2E 33300251/52/53 COMPLETED; E_G binary EMPTY — Hierarchy-Batch-P78 segfault ~0.4s at launch on E_G bundle while E_fresh/E_orig/A arms run in same RUNDIRs; E_G Bl_0 rims down to 15 pts vs 78-pt min in working E_BASE; two-loop check B–J stands) + 75 (SEL recipe that emitted the short fragments).

**Status:** results-in (worker 2026-10-18, lead write-back; renders eye-checked)

## Comments (lead write-back, 2026-10-18)

LANDED as crash-cure + honest partial. Crash cause BOUND (not rim size — long rims failed identically): all 31 E_G Bl_0 were bare xyz-only files; the reader (data_structure.cpp:245) leaves features empty, segfault at ranking_system.cpp:1113. Cures in pota82_repro/: v1 format-restore (cure82.py, 31/31 matched, max diff 3e-7) and v2 merge-cure (merge82.py, len>=15 + surface-anchored, zero refusals, E04 17 runs n=819). E2E (lead-verified COMPLETED 0:0): v1 33343794/95/96 = 0/6+0/2 x3 (short rims starve the beam, 139 hypotheses); v2 33349656/57/58 = 2/24+1/40, 2/24+1/40, 0/24+0/40 (17k hypotheses, below E_fresh 4-9/31). Renders eye-checked: ECURE red on-lip incl. tiny E10; EMERGE traces ORIG with visible parallel/teleport strands (residual doubling honestly reported). Controls green all 6 (A 8/8+15/15; asserts 5/5/5). No commits by worker; ORIG untouched.

**Starting position:** the guarded E bundle crashes the assembler at launch; prime suspect = sub-minimum rims in the loaded slot. In scratch copies of pota78_bundle_E_G: (a) identify the crashing piece (bisect by removal — one run per half, binary search); (b) cure per cause — pad/merge short fragments to a walkable loop, or refuse the piece explicitly (refusal-gate doctrine: refused pieces are declared, never silently dropped); (c) re-run E2E x3 same-binary. If the crash is not rim-size, bind the true trigger (malformed header? surface mismatch?) with evidence. Zero ORIG points in any fix; ORIG evidence-only.

**Rules:** land with E_G running + E2E at/above best fresh 7/31+3/62 x3 same-binary + controls green (E_orig 30/31+59/62, A 8/8+15/15) in same runs; renders (eye-check); E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats >=3; no gate relaxation without a mechanism.

- [ ] Crash-piece bisection + trigger bound
- [ ] Cure (pad/merge/refuse) + E2E rerun x3 or measured why-not
- [ ] Job IDs + sacct states
