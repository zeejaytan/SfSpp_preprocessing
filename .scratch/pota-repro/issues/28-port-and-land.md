# 28: Port the cure set into the tree, reproduce, land

**What to build:** the landable proof — every staged fix as committed source, reproducing the cure from a repo-built binary.

**Answers:** E1

**Blocked by:** 24, 27 (staged fixes below); 22 (relaxations); 23 (determinism, already committed).

**Status:** ready-for-agent

**Starting position:** the cure is proven but lives in Spartan worktrees, not the repo. Port each hunk into the laptop tree with its SFS-T tag and ticket reference, rebuild from the repo state, and reproduce ticket 27's numbers with a repo-built binary:
1. SFS-T24: skip `ticket14_append_patch_rims` for Pot_A_Piece_02 (ticket 24; Spartan worktree `sfs_preprocessing_pota24`, tracked diff = only T24)
2. SFS-T27: extend the skip to Pot_A 03/04/05 (ticket 27; worktree `sfs_preprocessing_pota27` @ 2465a47, +22 lines 1 file)
3. RP overlap-kill ablation (`feature_matching.cpp:1865`, P22FIX) + CheckGraph overlap veto 50→150 (P22FIX2) — both ORIG-validated repeatedly; staged in `sfs_main/sfs_p22fix_src/` (verify diff = prints + P22FIX + P22FIX2 only; port WITHOUT the diag prints)
4. Base already committed: SFS-T21 (wall split), SFS-T23a/b (tmp_path + determinism)

**Rules:** port hunks exactly (no drive-by changes; diag/print lines stay out). Rebuild the pipeline AND the assembly from the repo tree on Spartan (fresh clone/pull to the port commit — no worktree binaries). Same-binary ORIG control in the same job (must reproduce 8/8+15/15 or void). Acceptance: repo-built gate 15/15 + binary 8/8+15/15 + STRICT relative-edges 15/15 (gauge overlay as corroboration, not acceptance).

- [ ] Four hunks ported with tags; diff per hunk in the ticket
- [ ] Repo-built cure run: gate + E2E k=5/b=3, all three bars; ORIG control valid
- [ ] Laptop poll per sbatch (`sacct` directly); seating render + measurement pair; no commits (lead lands the set); Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain. Note the successor runs on the deterministic pipeline (T23b committed) — bundle-to-bundle comparisons are now signal.
