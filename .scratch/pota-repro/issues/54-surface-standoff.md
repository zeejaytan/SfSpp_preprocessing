# 54: Surface standoff — reshape the wall so it stands off the rim

**What to deliver:** a p2 Surface_1 that stands off the rim like ORIG — valid thickness, honest strengths, E2E lift.

**Answers:** E1

**Blocked by:** 53 (our p2 S1 hugs rim ~0.5mm noisy → 66% valid thickness vs 97%, med shift 1.2mm > 0.8mm Cond4 gate; p1 fine; SURFNORM destructive; trim refuted; point levers EXHAUSTED) + 21 (T21 split precedent — RegionGrowing fusion class fix) + 50 (gap corridor sheet — no new material; reshape existing).

**Status:** ready-for-agent

**Starting position:** the wall EXISTS (8001 pts) but sits wrong: noisy contact with the rim where ORIG keeps a structured standoff. This is pipeline-side surface regeneration work, not point editing: candidates include RegionGrowing parameter/merge behaviour on B-p2 (cf. T21 cluster split), surface denoising/smoothing that preserves the rim (50 proved raw sampling is matcher signal — do NOT resample the rim), re-fitting S1 from the mesh with standoff. Render reference: artifacts/t53_p2_surfrim.png (ours crowds, ORIG stands off). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** land ONLY with valid-thickness recovery toward ORIG (97% valid, med ~2.9) AND/OR honest strength lift AND/OR E2E lift ×3 same-binary runs + controls green (B ORIG 9/9+15/15, A 8/8+15/15) in same runs + gates green; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [ ] Standoff measurement + reshape arms, one variable each
- [ ] Thickness/strength/E2E lift or measured why-not
- [ ] Job IDs + sacct states

**Successor:** cross-pot generalization of the B recipe (C–J share the drowning shape).
