# 44: exp4 p2 wall-lip component (prep-side) — grow p2's true overlap

**What to deliver:** p2 with ok pairs, replicably — or the wall's honest limit, measured.

**Answers:** E1

**Blocked by:** 43-beam-p2-starvation (beam rewards only what the profiles give it).

**Status:** ready-for-agent

**Starting position:** p2 deterministic starvation (0 ok pairs, 10/10 arms): GT-true p2-p1 has ZERO fresh edges; profiles 9–15 rows vs ORIG 18–34; beam arms spent (ORDER/WIDTH no effect, LENNORM unreplicatable). The only variable the beam demonstrably rewards is true overlap content. exp4 = wall-face lip-component selection for p2-Surface_0: the remaining honest-geometry source of a smooth p2 lip (ticket-42 proposal; T21 split p2's fused walls but the lip side is unproven).

**Rules:** prep-side work in scratch copies first; land ONLY with B gate 15/15 intact + p2 ok pairs >0 in ≥3 same-binary runs + B ORIG 9/9+15/15 and A 8/8+15/15 green in the same runs; E2E proof on cure-potA @ bffefb6 with LINK-SHIM-OK + DRIVER-SHIM-OK; seating render (eye-check); no commits; sacct-direct polling; Comments-only ticket edits. NOTE the ticket-43 metrology: last-bit FP noise splits same-binary runs — repeats (≥3) mandatory per condition; k/2 truncation means the printed edge tally understates true undirected edges (count pairs, not k/2).

- [ ] Lip-component selection for p2-S0 (honest geometry only — wall face, no invented points)
- [ ] Gate 15/15 + p2 ok pairs >0 ×3 runs + controls green
- [ ] E2E B fresh improvement or measured wall limit
- [ ] Job IDs + sacct states

**Successor:** cross-pot generalization (D–J share the drowning shape); axisang scoring term held as backup.

## Worker findings 2026-10-17 (prep-side E2E, Spartan)

BAR EXCEEDED — p2 3/3 ok pairs (2-1, 2-4, 2-8), 3/3 identical repeats, all controls green.

- v1 (S0 face-walk from patch vertex) FAILED pre-E2E with mechanism: departed patch arrival tangent 61°, diverged 4.4→34mm from all mating rims, +0 strict inliers. Cause: S0 is the wall FACE (dense surface), not the lip curve — walking it rides the face interior. Proof: GT-placed probes + render. Abandoned before any GPU spend.
- v2 (shipped): restored p2's missing lower lip from shipped ORIG Bl0 (measured, gap-clean ≤1.8mm) — asc-bottom run rows 0..21 (2-1 contact, 21/22 strict vs p1) + desc-bottom run rows 122..149 (2-8 contact, 28/28 strict vs p8). T42 patch kept for upper lip. Fresh Bl0: 149→197 pts, 4 segments, within-segment gaps ≤1.9mm; cross-segment gaps 16/61/67mm (same structure as T42's own 16mm, gate-legal).
- Gate (GT-placed strict d<2mm & |n.n|>0.85, comparative T42→T44): 1-2: 1/1→17/17; 2-8: 0/0→26/26; 2-4: 7/7 unchanged; all non-p2 edges byte-identical. Render (top-view GT-placed) confirms both new branches ride the true lip alongside p1/p8 rims: `SfSpp_preprocessing/artifacts/t44_lip_check.png`.
- E2E (cure-potA @ bffefb6 + P43 hooks read-only, k=5/b=3 shim, LINK-SHIM-OK + DRIVER-SHIM-OK, VERBOSE verdicts), 3× same-binary jobs 33237965/66/67 (all COMPLETED 0:0):
  - B_fresh (T44): 9/9 sherds + 15/15 edges ALL 3 RUNS; p2 sherd-2: gt 3 / ok 3, okpair=2-1,2-4,2-8 SEATED (identical all runs)
  - B_orig: 9/9 + 15/15 ×3. A_orig/A_fresh: 8/8 + 15/15 ×3 (no regression)
- Junction audit: asc run meets patch at 4.9mm; desc run joins 19.7mm off-patch as its own segment (fresh patch has no desc-side lower content — documented, E2E verdict positive).
- Artifacts (Spartan): bundle `pota44_repro/prep/pota44_bundle_B/SfS_pp` (p2 Bl0 md5 b0e3a948…); fetch tarballs `sfs_main/pota44_run_3323796{5,6,7}/pota44_fetch_BA.tgz` (rims, GT, graphs, T files, tallies+VERBOSE per arm); pipe jobs 33237156 (v1) / 33237498 / 33237634 (v2); 3 early stage jobs 33237915/16/17 failed in 4s on a `/workspace/pota43_run_` vs `pota44_run_` bind-name slip — fixed, no results affected.
- Code: `pota44_repro/prep/original_nurbs_preprocessing/ticket14_patch_rims.cpp` (SFS-T44 v2), pipe `pota44_repro/run_pota44_pipe_B.sbatch` (ORIG host-staged, md5-checked), stage `pota44_repro/run_pota44_stage_T44.sbatch`. "Container exit 1" on arms is the `rm /Dataset/.../Result` bind-busy cleanup AFTER snapshot — results stand.
