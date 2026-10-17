# 73: Surface-branch selection — route the clean lip downstream

**What to deliver:** the S1-branch lip seated in the assembly path — E2E above zero.

**Answers:** E1

**Blocked by:** 72 (C02 Bl_1 203 pts / 0.78mm / 98.5%<2mm / zero jumps; C04 Bl_1 115 pts / 0.73mm / 93% / one 6.9mm link; assembler reads ONLY Bl_0 per asm/class/data_path.h; DENSE/NORMK refuted per-dose; C01 shredded at segmentation; jobs 33286361/33286648 COMPLETED) + 63 (Bl0-only loading proven per data_path.h:695 — Bl_1 file edits are runtime-inert; route must go through what the binary actually loads) + 62 (index_=1 semantics — recalled spans interact with matching/veto; watch for it).

**Status:** ready-for-agent

**Starting position:** the clean lip exists in-file (Bl_1) but invisible downstream. Options: swap Bl_1 content into the Bl_0 slot in scratch bundle copies (prep-side, zero ORIG points), or per-piece branch selection (C02/C04 from S1-branch, C03 stays, C01 needs segmentation work — flagged, not mandated). Bundle references pota72/pota39 C bundles (read-only). Zero ORIG points in any fix (44-asterisk rule); ORIG evidence-only.

**Rules:** land ONLY with gate recovery toward ORIG per-edge AND E2E above 0 ×3 same-binary + controls green (C ORIG 4/4+5/5, A 8/8+15/15) in same runs; renders (eye-check); prep-side scratch copies (no assembler source edits without a mechanism); E2E on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; no commits; sacct-direct polling; Comments-only ticket edits; repeats ≥3 per condition; no gate relaxation without a mechanism.

- [ ] Branch-selection arms, one variable each
- [ ] Gate + E2E rerun ×3 or measured why-not
- [ ] Job IDs + sacct states
