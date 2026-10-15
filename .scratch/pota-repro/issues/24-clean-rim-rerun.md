# 24: True-wall p2 rim walk + staged gate relaxations rerun

**What to build:** the cure test ticket 22 prescribed — a p2 rim that follows the recovered true wall, seated through the ORIG-validated relaxed gates.

**Answers:** E1

**Blocked by:** 21-piece2-wall-recovery (wall split committed), 22-beam-attractor (diagnosis + staged relaxations below).

**Status:** ready-for-agent

**Starting position:**
- Ticket 21 (committed SFS-T21): p2's two walls are split into their own Surface files; gate 15/15. But the RIM walk (Bl0) still runs ~3mm off both true rims — it follows the old merged geometry. The profile veto (ticket 22's binding gate) stands on rim content: merged-wall + offset pollution in the cylindrical profile/rim-gap test.
- Ticket 22 (jobs 33121906/33122802/33125896/33127092, ORIG controls valid throughout): beam scoring favors the true seating (vetoed graphs score 337–417 vs false winner ~287–330). Two relaxations proven ORIG-safe (ORIG holds 8/8+15/15): RP overlap-kill ablation (`feature_matching.cpp:1865`) and CheckGraph overlap veto 50→150. Staged sources: Spartan `sfs_main/sfs_p22fix_src/` (= diag prints + P22FIX + P22FIX2 + P22FIX3, keep for reuse — re-derive nothing, verify the diff first). Profile veto (PC_) must NOT be gutted — validity destruction, out of scope.
- Caution from ticket 23 (running separately): the mesh stage is nondeterministic run-to-run — build all comparisons within one bundle where possible, and rebuild from committed sources only.

**Rules:** rim-walk fix first (p2 Bl0 follows the recovered S1/S0 true wall; minimal, one variable), then the rerun with the two staged relaxations. Same-binary ORIG control in the same job (must reproduce 8/8+15/15 or void). Acceptance is the STRICT bar only (5°/10mm relative-edge): strict 15/15 fresh at k=5/b=3. If strict passes, the rim fix + both relaxations land together; if not, report what the profile veto still eats — no partial landing of gate relaxations on their own.

- [ ] p2 rim follows the true wall (composition check: rim points within ~1mm of recovered wall, not the merged sheet)
- [ ] Rerun with staged relaxations (verify sfs_p22fix_src diff = prints + P22FIX + P22FIX2 only; P22FIX3 prints reusable for diagnosis)
- [ ] Fixed arm: gate + E2E k=5/b=3, strict 15/15; forest count as corroboration
- [ ] Laptop poll per sbatch (`sacct` directly); before/after seating render + measurement pair; no commits; Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain.
