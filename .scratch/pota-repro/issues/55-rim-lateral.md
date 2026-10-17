# 55: Rim lateral position — walk the sheet edge, not the mid-wall

**What to deliver:** a B-p2 rim path that rides the sheet edge like ORIG — valid thickness, honest strengths, E2E lift.

**Answers:** E1

**Blocked by:** 54 (wall sits ON ORIG sheets NN 0.34mm — innocent; OUR rim runs mid-wall ~1.1mm off ORIG rim at GT seating, bad-thickness flags idx 1-186; smooth/swap/flip/trim measured-dead) + 50 (length settled; position still wrong) + 48 (T48b direction-mirror pipeline).

**Status:** ready-for-agent

**Starting position:** the walk must move LATERALLY (across the wall to its edge), not along length. Candidates: seed the walk at the sheet edge (edge-aware initialization from surface geometry), edge-seeking walk cost (prefer rim points at sheet boundary), post-walk lateral snap (project rim rows onto the sheet edge, honestly — same material, corrected position). Constraint from 50: do NOT resample rim spacing (matcher keys off raw sampling). Render reference: artifacts/t54_anatomy.png (ORIG rides edge, ours cuts mid-sheet + top loop). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** land ONLY with rim-on-edge recovery (per-index GT-seated distance toward ORIG) AND/OR valid-thickness recovery AND/OR honest strength lift AND/OR E2E lift ×3 same-binary runs + controls green (B ORIG 9/9+15/15, A 8/8+15/15) in same runs + gates green; renders (eye-check); prep-side scratch copies; assembler E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition.

- [ ] Lateral-position arms, one variable each
- [ ] Edge-riding proof or measured why-not
- [ ] Job IDs + sacct states

**Successor:** cross-pot generalization of the B recipe (C–J share the drowning shape).
