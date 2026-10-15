# 24: True-wall p2 rim walk + staged gate relaxations rerun

**What to build:** the cure test ticket 22 prescribed — a p2 rim that follows the recovered true wall, seated through the ORIG-validated relaxed gates.

**Answers:** E1

**Blocked by:** 21-piece2-wall-recovery (wall split committed), 22-beam-attractor (diagnosis + staged relaxations below).

**Status:** results-in — SHORTFALL (rim fixed, gate met, E2E strict 6/8+10/15; profile veto still eats true graphs, see Comments)

**Starting position:**
- Ticket 21 (committed SFS-T21): p2's two walls are split into their own Surface files; gate 15/15. But the RIM walk (Bl0) still runs ~3mm off both true rims — it follows the old merged geometry. The profile veto (ticket 22's binding gate) stands on rim content: merged-wall + offset pollution in the cylindrical profile/rim-gap test.
- Ticket 22 (jobs 33121906/33122802/33125896/33127092, ORIG controls valid throughout): beam scoring favors the true seating (vetoed graphs score 337–417 vs false winner ~287–330). Two relaxations proven ORIG-safe (ORIG holds 8/8+15/15): RP overlap-kill ablation (`feature_matching.cpp:1865`) and CheckGraph overlap veto 50→150. Staged sources: Spartan `sfs_main/sfs_p22fix_src/` (= diag prints + P22FIX + P22FIX2 + P22FIX3, keep for reuse — re-derive nothing, verify the diff first). Profile veto (PC_) must NOT be gutted — validity destruction, out of scope.
- Caution from ticket 23 (running separately): the mesh stage is nondeterministic run-to-run — build all comparisons within one bundle where possible, and rebuild from committed sources only.

**Rules:** rim-walk fix first (p2 Bl0 follows the recovered S1/S0 true wall; minimal, one variable), then the rerun with the two staged relaxations. Same-binary ORIG control in the same job (must reproduce 8/8+15/15 or void). Acceptance is the STRICT bar only (5°/10mm relative-edge): strict 15/15 fresh at k=5/b=3. If strict passes, the rim fix + both relaxations land together; if not, report what the profile veto still eats — no partial landing of gate relaxations on their own.

- [x] p2 rim follows the true wall (composition check: rim points within ~1mm of recovered wall, not the merged sheet)
- [x] Rerun with staged relaxations (verify sfs_p22fix_src diff = prints + P22FIX + P22FIX2 only; P22FIX3 prints reusable for diagnosis)
- [ ] Fixed arm: gate + E2E k=5/b=3, strict 15/15; forest count as corroboration
- [x] Laptop poll per sbatch (`sacct` directly); before/after seating render + measurement pair; no commits; Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain.

## Comments (worker, 2026-10-16)

**Verdict: SHORTFALL — the rim fix works (composition 98.7%, gate 15/15, p2 seated strict-OK), but E2E strict is 6/8+10/15, not 15/15. No landable set is claimed.** The profile veto still eats true-seating graphs (evidence below). No commits; laptop tree untouched except this file; sibling ticket-23 work never touched (built in a pinned worktree). Poll was via `sacct` directly throughout.

**1. Rim fault, pinned (not the walk — the T14 append).** The edge walk itself is fine: T21-bundle p2 Bl0's wall segments (pts 0–146) sit 98.6% within 1mm of the walked wall (median 0.44mm) = ORIG's 98.8% (median 0.33mm). The pollution is the SFS-T14 patch-rim append: 575 pts of decorative-groove loops at 49.4% within 1mm, concatenated as segment 147–721 with 7 teleport leaps (up to 107mm 3D steps) between arcs. Notebook: `edgeline_extraction_headless.cpp` T14 call site (~:3410); assembler parses segments but matches all rim-flagged ones (`data_structure.cpp` `BreakLine::ReadPCDFileWithInfo`).
- **One-variable fix (SFS-T24):** skip `ticket14_append_patch_rims` for `Pot_A_Piece_02` only (+10 lines, comment + `if` wrap). All other pieces byte-identical by construction. Laptop proof before touching source: wall-only strict inliers 22/7/14/10 on pairs 1-2/2-4/2-5/2-8 (probe-faithful rule, GT-placed), every pair ≥ 2 — gate stands without the append. Fix lives in Spartan worktree `sfs_preprocessing_pota24` (pinned at committed `1dd8c1d`, tracked diff = only the T24 block) — for lead review/commit. Vendored `alglib/` (gitignored) copied from the live checkout into the worktree; without it a fresh edge build fails (`dataanalysis.h`).
- **Composition check on the NEW bundle: 155 pts, 98.7% within 1mm of the walked wall** (median 0.44mm, p90 0.78mm, max 1.42mm) — bar met, matches ORIG.

**2. Cure run.** `run_pota24.sbatch` + `run_pota24_stage.sbatch` (both in the worktree): full mesh+edge from committed+T24 sources, fresh build dir, bundle `pota24_bundle/SfS_pp`, 2-arm assembly with the staged fix binary. Verified fix-source diff first: `feature_matching.cpp` + `ranking_system.cpp` only — diag prints + P22FIX (RP overlap-kill ablation) + P22FIX2 (CheckGraph 50→150) + P22FIX3 (p2c centroid print); `PC_` appears nowhere in the diff. In-job audits: T21 fired exactly once (p2, 8001/7616 pts — same split as t21); p2 EXCHANGED by T04 like p3–8; p2 Bl0 = 155 pts wall-only (4 splitter segments this run vs 3 in t21 — peak count varies run-to-run; the POINTS≤250 content bar governs). Pieces 1/6/7/8 rims byte-identical to the T21 bundle (p1 noted stable); p2–p5 differ (mesh nondeterminism as ticket 23 warns).
- **Jobs (sacct State/ExitCode):** 33131000 FAILED 1:0 in 5:51 — two infra faults, both fixed, mesh+edge output kept: (a) fresh edge build failed on missing vendored alglib (above); (b) my own over-strict guard (segments==3). 33131337 debug COMPLETED 0:0 (surfaced the alglib error). 33131736 FAILED 1:0 in 5:51 (mesh+edge COMPLETE and audited, exit on guard (b)). 33132499 (stage+assembly) COMPLETED 0:0 in 7:24.
- **ORIG control (same job, same binary): 8/8 + 15/15, forest 124/70 — VALID**, authors' result reproduced a third time with the relaxed gates. Nothing is void.
- **GATE on the new bundle (laptop, probe-faithful): 15/15**, every pair ≥ 6 strict inliers (p2 pairs: 22/6/14/10).
- **Fresh E2E (k=5/b=3): binary 6/8 + 10/15, forest 438/85; STRICT (5°/10mm relative-edge): pieces 6/8, edges 10/15.** p2 SEATED strict-OK (rel-rot 1.85°, rel-trans 4.43mm) — the ~102° attractor is gone. Pieces 1,4,5,6,7 OK; piece 3 UNPLACED; piece 8 flipped ~172°/410mm. Wrong edges: 2-8, 4-8 (both touch p8) + 3 unplaced (1-3, 3-5, 3-6).

**3. What the profile veto still eats (no partial-fix claims).** Fresh-arm trace (`sfs_main/pota24_cure_33132499/fresh_binary.log`): PLAUS-PC_ 33 total (20 with shard 2), PLAUS-Overlap_ 1 (relaxations hold — was 7 in t22-fix1). `nodes=1245678` (all-but-3) with p2 at truth (p2c within ~2.4mm of C_true) scoring 460–521 vetoed by PC_; the full `nodes=12345678` @363 vetoed by PC_; the passed winner is `nodes=1245678` @454 (p2 also at truth) with p8 flipped. So PC_ passes a true-p2 graph yet vetoes higher-scoring near-identical ones — the veto is pose/content-specific, not blanket. p3's only non-junk graphs: `13467`@250 (passed, orphaned) and the full assembly (vetoed) → p3 unplaced because its true completion is PC_-vetoed. Open for the lead: whether true-p8 graphs are vetoed or merely outscored (prints can't separate p8's pose inside vetoed graphs; p8's rim is unchanged from t21 — 3889B — so its flip is search-side).
- Render + measurement pair: `artifacts/pota24/pota24_seating_orig_vs_fresh.png` (placed Bl0 rims: ORIG closed ring vs fresh ring with p3 gap + flung p8; p2 correctly seated top) + strict numbers above. Composition renders: `t21_p2_rimcomp_pc12.png`, `t21_p2_rimorder.png`, `p2_radius_profile.png`. Laptop probes: wall/patch attribution + gate + strict scorer (`p24_score.py`, `snap/`).
- Spartan leftovers (all untracked, sibling-safe): worktree `sfs_preprocessing_pota24/` (source+`build_pota24/`, `pota24/`, `pota24_bundle/`, both sbatches, slurm logs), `sfs_main/pota24_cure_33132499/` (orig+fresh arms, snapshots, veto-traceable binary logs). Main-checkout tracked tree never modified (verified clean before submit); worktree registered in main `.git` metadata only.

**Successor proposal for lead:** (i) PC_-veto diagnosis on p8-true vs p8-flipped graphs (needs per-piece pose prints — P22FIX3 pattern extends to p8/p3); (ii) p3 starvation vs veto (PP/RP prints are p2-only); (iii) land T24 + staged relaxations only together with a veto fix that closes 15/15 — per this ticket's rules, nothing lands alone.
