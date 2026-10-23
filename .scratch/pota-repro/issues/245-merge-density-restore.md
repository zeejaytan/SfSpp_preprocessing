Status: done

Lead verdict (R6 2026-10-22): PASS. Jobs 33666465 + 33667102 COMPLETED 0:0. Binary byte-identical to 244 (b8eb3759) on the same node. P03 spot: S0 107304 (+0.18% thread-noise), cut 2396 EXACT, Bl0 0.72/97.8 same class as 244 (0.71/100.0); Bl1 tracer caveat reproduced. Merge 93c33bc on origin/main; decision recorded in message. Restored density is now the main-line default.

# Ticket 245: merge the 244 density restore to main

Answers: E1 — whether restored-density default is live on main with verified binary.
Needs-eye: no.

## Goal
Apply artifacts/pota244/restore244.diff to origin/main, rebuild, verify the binary, spot-check P03, commit + push.

## Boundary
- Fresh worktree of origin/main + fresh Spartan copy. The ONLY source change: apply C:/PR/SfSpp_preprocessing/artifacts/pota244/restore244.diff (21+/7-, downsamplePointCloud + call site). No other edits.
- User decision 2026-10-22: keep the restore; sample-dataset match (48fb588 motive) is knowingly broken ~3.4x on big pieces. Record this decision in the commit message.
- Main worktree (user 204-edit) off limits except ticket commit+push (lead lands). No other pieces touched.

## Constraints
- Spartan: pull --ff-only first, STOP and report on divergence.
- Standing rule: source change => rebuild + verify binary. Same build node as 244 for md5 comparison (expect b8eb37599bb222764f789eabb5dd798c BYTE-IDENTICAL: main source @a41fa6a == 244 base @8f27cf0 plus ticket-only commits; identical-or-explained).
- Spot-check: P03 mesh + dc472b0e trace reproduces 244 (S0 ~107k, cut ~2396, Bl0 0.71/100-class). Full verdict: PASS only if identical-or-explained AND spot-check class holds.

## Acceptance
- main contains the restore; rebuilt mesh binary md5 cited (identical to b8eb3759 or explained); P03 spot-check numbers; sacct COMPLETED; commit pushed.

## Required evidence to report
Applied diff stat; build job + binary md5; P03 spot numbers; job IDs + sacct states; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.

## Comments (worker, 2026-10-22 -- PASS: restore merged to main, binary byte-identical, P03 class holds)

**Verdict: PASS. The restored-density default is live on main with a verified binary.**

**Divergence/STOP note (brief rule): Spartan live checkout behind (f4add97 vs origin/main 3bb6615) + fetch clean, merge-base FF-POSSIBLE -- not history divergence. Left untouched per 239-244 precedent (skip-worktree live data + Juglet untracked dirs); worked in fresh worktree sfs-dense-245 @ 3bb6615 (detached). Laptop main == origin/main, no divergence. No other main commits.**

**Applied diff: mesh_processing_headless.cpp | 28 ++++---, 21 insertions(+), 7 deletions(-) -- exact match to restore244.diff stat. Base identity proven: git diff 8f27cf0..3bb6615 -- mesh_processing_headless.cpp EMPTY (ticket-only commits between); pristine cpp md5 556ef97aacedddadd4df283ccff01d15 both sides; patched cpp md5 b91cc036e1e9721114b7e11dc4a401e0 IDENTICAL to 244's sfs-dense-244 working tree; committed blob 14721a2 == diff postimage. Laptop artifact md5 26efda84a663f909c03f5fcf5f1cbd64, uploaded verbatim to Spartan as sfs-dense-245/restore245.diff.**

**Build (job 33666465, sacct COMPLETED 0:0, spartan-bm171 -- SAME node as 244 Phase B): binary md5 b8eb37599bb222764f789eabb5dd798c -- BYTE-IDENTICAL to 244. identical-or-explained: IDENTICAL, no explanation needed.**

**P03 spot-check (job 33667102, sacct COMPLETED 0:0, bm152; mesh binary md5-gated b8eb3759 + edge md5-gated dc472b0e87c934b6c487ff8637209864 in-job): downsample input 1616373 -> 164403 EXACT (244); 9 clusters (244); S0 107304 (244: 107109, +0.18% thread-noise class, bounds identical, dmin_cut 0.42); cut n_lt10 2396 EXACT + n_lt30 20827 EXACT; S1 111564 (244: 111534); Bl0 225pts med 0.72 cov 97.8 0 jumps (244: 220pts 0.71/100.0 -- same class); Bl1 358pts 0.98/52.8 + 47.1 jump reproduces 244's known tracer-side caveat EXACTLY (357pts 0.97/52.7 + 47.1). Class HOLDS.**

**User decision recorded (2026-10-22, in commit message): keep the restore; sample-dataset match (48fb588 motive) knowingly broken ~3.4x on big pieces.**

**Evidence: Spartan leftovers (all mine, sibling-safe): sfs-dense-245/ (@3bb6615 + restore applied uncommitted, build-245/, build245.sbatch, run245.sbatch, bin245_md5.txt), pota245_P03_RST/ (mesh.log, edge.log, faces, breaklines). 214/239/240/241/242/243/244 dirs untouched. Local fresh worktree SfSpp_preprocessing-245 removed after landing; this commit is the only main commit.**
