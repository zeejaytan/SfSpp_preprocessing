# Revive the dead code — apply the 150 patch to prep sources

GOAL: THE TAP CLOSED IN PRODUCTION, NOT IN PROTOTYPE.

**Answers:** E1

**Blocked by:** 150 (production patch named not applied: face gate at edgeline_extraction_headless.cpp:949 angle gate + un-kill :1032 ROR reload-over; GridX secondary: SURF-C1 veto at p143_step2.py:124 / p143_step5.py:106)

**Status:** ready-for-agent

**What to deliver:** (1) apply the patch to the prep sources in a working tree (face-discrimination gate at the :949 boundary admission + remove the :1032 raw-cloud reload-over so cloud_Filtered survives; GridX SURF-C1 veto); (2) rebuild whatever the patch touches — if the build needs Spartan or otherwise exceeds login-node/login-laptop means, STOP after staging the exact diff + build instructions and say so (do NOT submit jobs); (3) if built: re-run the C-base extraction and prove the outer loop blocked at source (outer share vs 150's 182/195 baseline, inner kept count) with the 148/150 counters. Production-illegal shortcuts forbidden: no ORIG-derived constants anywhere in the patch; the gate must be mesh-observable only.

**Starting position:** 150 Comments (file:line + prototype numbers), prep sources per 150 §1. New scratch pota153_repro/; renders under laptop artifacts/pota153/.

**Rules:** ORIG Bl_0 ruler-only everywhere; worker COMMIT NOTHING (diff staged as files in scratch, lead lands); tickets 39-152 read-only; Comments-only ticket edits.

- [ ] Patch applied in working tree (diff staged, ORIG-free)
- [ ] Build result (binary or stop-with-instructions)
- [ ] Re-extraction proof vs 182/195 baseline (or staged for lead)
