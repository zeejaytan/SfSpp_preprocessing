# 57: NURBS lip-region refit — move the material, don't cut it

**What to deliver:** a refitted B-p2 S1 lip with ORIG-like standoff — valid thickness, honest strengths, E2E lift.

**Answers:** E1

**Blocked by:** 56 (lip-curl NURBS-fit error in ~3mm band, 8× excess hugging material; JOINT bound 66→7 — wall behind outside ray corridor; cut dead; ONLY a refit that moves material qualifies) + 54 (sheets fine off-lip at 0.34mm — refit must preserve the bulk).

**Status:** ready-for-agent

**Starting position:** the refit must (a) exclude the curled lip-band cluster points, (b) refit the lip region from honest neighbouring material (mesh + wall points), (c) preserve the innocent bulk (0.34mm agreement — gate on bulk drift), (d) keep rim spacing untouched (50: matcher keys off raw sampling). This reaches into the surface-fitting stage (RegionGrowing/NURBS pipeline) — work in scratch copies of the fitting chain, not the repo source. Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only. Render references: artifacts/t56_lip.png, artifacts/t56_depth.png.

**Rules:** land ONLY with standoff recovery toward ORIG (2.87) AND/OR valid-thickness recovery toward 97%/med 2.9 AND/OR honest strength lift AND/OR E2E lift ×3 same-binary runs + controls green (B ORIG 9/9+15/15, A 8/8+15/15) in same runs + gates green + bulk-drift gate (off-lip sheet must stay within ~0.5mm of current); renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [ ] Lip refit arms, one variable each
- [ ] Standoff/thickness/strength/E2E lift or measured why-not
- [ ] Job IDs + sacct states

**Successor:** cross-pot generalization of the B recipe (C–J share the drowning shape).
