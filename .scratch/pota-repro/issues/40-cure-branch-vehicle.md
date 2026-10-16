# 40: Cure-branch vehicle — 3 hunks onto upstream base, repo-built 8/8+15/15

**What to deliver:** a clean, traceable cure branch that reproduces ticket-36 numbers from checkout.

**Answers:** E1

**Blocked by:** 38-land-cure-set (vehicle ruling: cure-tree recipe).

**Status:** results-in

## Comments (worker, 2026-10-16)

**Verdict: PASS — all acceptance bars met. Cure branch `cure-potA` (bffefb6) pushed; 2/2 repo-built E2E runs 8/8+15/15 both arms with valid ORIG controls; renders eye-checked; all jobs sacct-verified COMPLETED 0:0. NOTHING committed except the cure branch (laptop artifacts + this file left uncommitted for the lead).**

**0. Branch (laptop `structure-from-sherds-pp`).** `cure-potA` created from upstream @9195c01, pushed to `origin/cure-potA` as bffefb6. Cherry-pick of 9f432bc/89f771c/b35905b NOT applicable (fork contexts don't exist on upstream — fork carries +377 files vs upstream). Applied by hand, verified in-tree: (a) P22FIX `feature_matching.cpp:1860` drop `|| overlap_` ✓; (b) P22FIX2 `ranking_system.cpp:1785` 50→150 ✓; (c) C2-restore VACUOUS — upstream already carries `axis_angle_ > 0.436` at BOTH sites (FM:1715, FM:1853); the 0.610 drift exists only on the fork (11f4827 FM:1773 via ac64c3f's false "upstream 0.610" claim). So `git diff 9195c01..bffefb6` = exactly 2 files, 2+/2-, the two functional one-liners (the 3rd is already-correct upstream, no diff to show). Fork main untouched (still b35905b, verified). Upstream remote already present (`SeongJong-Yoo/structure-from-sherds-pp`).

**1. Pipe 33195491 (COMPLETED 0:0, 7:07).** Fresh Spartan clones `pota40_repro/`: prep @ f1fd6b4 (tracked clean) + asm @ bffefb6 (tracked clean, delta-vs-9195c01 guards green, PC_ 0), zero patches. alglib scaffold + `diff -rq` IDENTICAL guard reused from ticket 38 (nested `original_nurbs_preprocessing/alglib/` is untracked scaffolding; content = landed git content, build stays repo-built). Audits green: T21 fires exactly once (p2), T04 p1 KEPT rest EXCHANGED, zero T14 appends on 02–05, T27 4 skips, Bl0 155/146/140/135 exact, 16+16 bundle, **breaklines identical to recorded p28 md5s**.

**2. Gate 15/15 (laptop p40_gate.py on repo-built rims): teleports 0 on all Bl0; gate 15/15, min 7, pair 1-3 = 47 — matches the p27 wall-only prediction exactly.**

**3. E2E run 1 — 33195763 (COMPLETED 0:0, 7:04). VALID: LINK-SHIM-OK + LINK-FORKMAIN-ABSENT-OK + DRIVER-SHIM-OK both arms; 8 T-files each. ORIG 124/70 8/8+15/15; fresh 420/119 8/8+15/15.** Driver note: the cure tree carries no `hpc/tools` shim (upstream has no `hpc/` dir), so the shim is the fork host copy `sfs_main/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp` (TOP_k 5/BRANCH_b 3, byte-stable since 3b3e4d6) — the ticket-36 precedent (job 33191627), scratch driver, no gt_stub needed (shim includes only upstream-existing headers; link clean). Pruned counts match ticket-36 cure exactly (124/70 + 420/119; the "124/63" in this ticket's step 2 is the FORK-tree number from ticket 38, not the cure-tree number).

**4. E2E run 2 (repeat) — 33196240 (COMPLETED 0:0, 6:22). VALID, same asserts, 8 T-files each. ORIG 124/70 8/8+15/15; fresh 420/120 8/8+15/15.** One-count pruned wobble on fresh (120 vs 119) with identical binary selection and edge-identical strict tables (see below) — hypothesis-count noise, non-gating. Both runs hit 8/8+15/15 both arms: no miss, nothing chased.

**5. Strict (diagnostic, p40_strict.py 5°/10mm): R1 = R2 edge-identical at printed precision, and identical to the ticket-36 cure tables: ORIG 6/15 (fails 1-2/1-3/1-4/1-5/1-6/2-5/2-8/3-6/4-8), fresh 12/15 (fails 1-5/2-5/3-5).** Renders `artifacts/pota40/pota40_seating_R1.png` (job 33195763) + `pota40_seating_R2.png` (job 33196240) eye-checked: both rings closed, all 8 rim loops seated, no collapse; R1/R2 visually identical.

**6. Evidence.** Laptop `artifacts/pota40/`: run_pota40_pipe.sbatch, run_pota40_stage.sbatch, gt_stub.cpp (contingency copy, NOT used — link needed none), p40_gate.py, p40_strict.py, p40_render.py, gate_fetch(.tgz), pota40_fetch_R1/R2(.tgz), pota40_seating_R1/R2.png. Spartan `pota40_repro/` (fresh clones at exact heads, both sbatches, slurm logs) + `sfs_main/pota40_run_33195763/` + `pota40_run_33196240/` RUNDIRs. sacct (live): 33195491 / 33195763 / 33196240 all COMPLETED 0:0. Poll was `sacct` directly throughout. Live checkouts untouched except `git fetch` (remote-tracking only); prep live checkout holds untracked `Juglet_*` files beyond the 5 lines listed at dispatch — pre-existing or third-party, NOT mine (I wrote nothing outside `pota40_*` paths); lead may confirm. No intruder files in any `pota40_*` path. Successor ticket 39 is unblocked on this vehicle.

**Starting position (bar ruling 2026-10-16: cure-tree recipe).** Ticket 36 proved upstream@9195c01 + 3 staged hunks = 8/8+15/15 both arms. Ticket 38 proved the fork + same 3 hunks = fresh 7/8+10/15 in 3/3 runs (ORIG wobbles 7/8+7/15 ↔ 8/8+13/15 on identical pruned counts — beam variance, same binary). Remaining fork↔cure delta (refinement weighting et al.) is NOT chased piecemeal per the ruling. So the B–J vehicle is a cure branch, not the fork.

**Steps:**
1. In the `structure-from-sherds-pp` laptop clone, create branch `cure-potA` from upstream @9195c01 (add upstream remote if absent; DO NOT touch fork main — it stays at b35905b). Apply the 3 hunks (cherry-pick 9f432bc/89f771c/b35905b if contexts apply, else apply by hand from the ticket-28/abl2 record) — final diff vs 9195c01 must be exactly those 3 one-liners. Push the branch.
2. REPO-BUILT REPRODUCE on Spartan from fresh clones (prep @ f1fd6b4 + cure branch, zero patches): gate 15/15, then E2E k=5/b=3 shim both arms with LINK-SHIM-OK + DRIVER-SHIM-OK asserts, non-empty snapshots. Expect ticket-36 numbers: ORIG 8/8+15/15, fresh 8/8+15/15, pruned 124/63 + 420/119.
3. REPEATS (variance is proven — one run proves nothing): minimum TWO full E2E runs; both must hit 8/8+15/15 both arms. If either misses, stop and report (do not chase — hand back to lead).
4. Strict tables recorded as DIAGNOSTIC only. Seating render both arms (eye-check). sacct-direct polling. COMMIT NOTHING except the cure branch. Comments-only ticket edits.

**Acceptance:** cure branch pushed (diff = 3 one-liners vs upstream); 2/2 E2E runs 8/8+15/15 both arms with valid ORIG controls; renders; job IDs + sacct states.

**Successor:** ticket 39 (B–J E2E on this vehicle, repeats per pot).
