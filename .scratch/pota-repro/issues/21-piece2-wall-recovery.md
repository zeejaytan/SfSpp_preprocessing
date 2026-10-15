# 21: Recover the piece-2 exterior-wall surface

**What to build:** the actual fix — find where p2's wall collapses in the surface stage and recover it, closing Pot A at strict 8/8 + 15/15.

**Answers:** E1

**Blocked by:** 20-piece2-endgame (diagnosis below).

**Status:** results-in — SHORTFALL (wall recovered, gate met, E2E strict not met; see Comments).

## Comments (worker, 2026-10-16)

**Verdict: the exterior wall is recovered (gate 15/15), but the ticket bar is not met (E2E strict 2/15, forest 564 vs ~124).** The remaining failure is in the search, not the extraction — evidence below. No commits; tracked tree clean on laptop and Spartan (both jobs log "tracked tree clean"); SFS-T13 code untouched.

**1. Root cause, pinned.** The wall was never dropped as points — it was FUSED. RegionGrowing grows p2's BOTH walls into `clusters[0]` at every smoothness threshold, so the size-rank assignment feeds a merged double wall to Surface_0 and scrap to Surface_1:
- Fresh mesh log (`pota13_fresh/mesh_stage.log` p2 section): 8976 pts -> Cluster 1 = 7498, Cluster 2 = 51, 1427 unclustered. No retry (2 clusters >= 2).
- Laptop bidirectional NN (fresh S0 11263pt vs ORIG walls, co-framed): 7553 pts near ORIG-S1 only + 3680 near ORIG-S0 only + 4 both + 26 neither; normals agree 99.8%/99.9% with the nearer wall. Fresh S0 = 67% wall-1 + 33% wall-0 MERGED. Consequence chain: T04 guard rightly refuses the swap (winner ratio 0.015 < 0.10 — the "winner" is the 51-pt scrap), the rim walk runs on a double wall ~3mm off both true rims, Bl1 is an 18-pt stub.
- Fault file:line: `original_nurbs_preprocessing/mesh_processing_headless.cpp:1786` (size-desc sort) + `:1810-1812` (mergeClusters, then largest-two taken at `:1886-1891` with no degeneracy check). The retry loop (`:1664-1680`) only loosens on <2 clusters, so a merged pair + scrap never retries.

**2. One-variable fix (SFS-T21, normal-split).** Threshold sweep first (SFS_SMOOTHNESS_DEG, no source change, job 33118420): p2 top-2 = 7498+51 @4.5, 7546+92 @3.5 (iter-1 merged fully into ONE 7441-pt cluster, then loosened), 7498+51 @2.5, 6407+415 @1.5 (ratio 0.065, still degenerate). No threshold splits the walls — sweep direction REFUTED by evidence. Fix instead splits `clusters[0]` by sign of (normal . component-wise-median-normal) when `clusters[1]/clusters[0] < 0.10` (same 0.10 bar as the T04 guard), accepting only clean splits (both parts >= dynMinCluster, small/big >= 0.10, ambiguous |cos|<0.5 fraction <= 15%), else historic path untouched. Laptop proof before touching source: median-split of the merged S0 separates 100.0%/98.4% at 0.31mm median (script `artifacts/pota21/normsplit.py`). Fix lives as an UNCOMMITTED laptop edit: `original_nurbs_preprocessing/mesh_processing_headless.cpp` after line 1812 (`numberOfClustersCreated = clusters.size();`, +74 lines tagged SFS-T21) — for lead review/commit. Spartan ran it from the untracked copy `original_nurbs_preprocessing_t21/` (diff vs committed = only the 74-line block); committed binary rebuilt from `ce29448` for the baseline.

**3. Fix validation (job 33119652, COMPLETED 0:0 in 11:10).** T21 binary, default 4.5deg, full mesh+edge, 2-arm assembly same job:
- `[SFS-T21] degenerate second cluster (ratio 0.0068); normal-split n=7498 -> +3878/-3620 amb=0.0005; ACCEPTED` — fired EXACTLY ONCE (p2 only; all other pieces flow through the historic path).
- p2 surfaces: S0 = 8001pt, S1 = 7616pt (was 11263 merged + 171 scrap). Composition vs ORIG walls: **S0 100.0% wall-1, S1 100.0% wall-0** (laptop NN). T04 now EXCHANGES p2 (ratio 0.95, margin 15.0) like p3-8; p1 kept as before.
- Render + measurement pair: `artifacts/pota21/pota21_p02_slice.png` (XZ cross-section slice |y-40|<1.5mm: BEFORE one file holds TWO sheets ~3.5mm apart + black scrap; AFTER S0 = upper sheet only, S1 = lower sheet only) + `pota21_p02_before_after.png` (full view). Scripts: `render_slice.py`, `render_p2.py`, `wallcomp*.py`, `normsplit.py`, `p21_score.py`.
- GATE (laptop `gate_probe.py`, strict d<2mm & |n.n|>0.85, bar >=2): **15/15** — p2 pairs 1-2: 22, 2-4: 10, 2-5: 26, 2-8: 18 strict inliers (were 0/0/0/0 ablated, 2-3 patch-aided before). p2 Bl0 now 721 pts (was 179/48).
- ORIG control (same job, same binary): **8/8 + 15/15**, forest 124/70 — authors' result reproduced, control VALID.
- Fresh E2E (k=5/b=3): binary absolute **3/8 + 3/15**, relative-vs-ORIG (p19_score rule, 5deg/10mm): **pieces 0/8, edges 2/15**. Forest **564/65**. Bar NOT met; forest NOT toward 124.

**4. Why E2E fails: the search is poisoned by p2 content, not starved of it.** Controlled comparison (rim lengths identical except p2; surfaces drift run-to-run, see 5):
- t19 ablated (p2 48-pt stub, patch cut p2-p5): 7/8 + 11/15, forest 584/75.
- t06 patched (p2 stub + patch rims): 4/8 + 3/15, forest 522/57.
- t21 fixed (p2 721-pt TRUE wall rim, patch kept): 3/8 + 3/15, forest 564/65.
More true p2 content -> worse E2E: the beam seats p2 at the SAME ~102.7deg/232mm false seating with stub (t19), patch (t06: ~101-103deg x3 in t20's repeats) and full wall (now: rel-rot 102.71deg, rel-trans 232.73mm; pieces 1,6,7,8 dragged as a rigid ~74deg block, piece 3 unplaced). Ticket 20's "search exonerated" (swapped ORIG rim seats 4/4) does NOT generalize: the beam's ~102deg p2 attractor beats the true seating at k=5/b=3 regardless of rim quality. Category 1 (method genuinely fails at the search step on this fragment), building on t11's "patch load-bearing for gate but poison for search" — now true for the wall rim too.

**5. Two landmines found (NOT touched — out of scope, reported for the lead):**
- (a) Silent surface loss on any multi-iteration piece: `tmp_path` is basename-mangled at `:1915-1926` ("Getting file name without path"), so iteration >= 2 saves `tmpSurfaceCluster_*.ply` to CWD and the exists-check at `:2238` warns ("Source file not found: Temp/Temp/...") while the pipeline continues with NO surfaces for the piece. Bit the 3.5/2.5 sweep arms (stray `tmpSurfaceCluster_*.ply` at tree root prove it). Dormant at baseline 4.5 (zero retries Pot A) — no shipped numbers affected.
- (b) Mesh stage is nondeterministic run-to-run: committed-binary reruns (pota19 vs s4_5 sweep) give byte-different surfaces for p3/p5/p8 (byte-identity is the wrong acceptance bar; sizes/gate/E2E are the valid ones). p1 happens stable.
- (c) T21 Dataset order note: fixed p2 S0 = ORIG-S1 wall, S1 = ORIG-S0 wall (T04 exchange makes Bl0 interior-fed, consistent with p3-8).

**6. Jobs (sacct State/ExitCode):** 33118420 sweep COMPLETED 0:0 (~16min); 33119539 fix-attempt FAILED 1:0 in 4s (stale CMakeCache copied into the T21 source copy — infra, fixed by fresh cmake dir, no compute wasted); 33119652 fix+assembly COMPLETED 0:0 in 11:10. Laptop poll was via `sacct` directly. Spartan leftovers: `pota21_mesh_s{4_5,3_5,2_5,1_5}/` (sweep; s3_5/s2_5 p2 surfaces missing per 5a), `pota21_fixed/`, `pota21_bundle/SfS_pp`, `sfs_main/pota21_verify_33119652/` (orig+fresh arms, snapshots), untracked `original_nurbs_preprocessing_t21/`, sbatches `run_pota21_sweep`/`run_pota21_fix`. Laptop evidence: `artifacts/pota21/` (probes, gate bundle, snapshots, renders). Fix NOT committed (lead decision).

**Successor proposal for lead:** (i) T14-patch-ablated variant of THIS fixed bundle (t11 method) to separate wall-rim poison from patch poison — needs a bundle-surgery exception or a T14-disable flag as its own one-variable ticket; (ii) search-side ticket for the ~102deg p2 attractor (beam scorer prefers it over true seatings that gate 10-26 strict inliers); (iii) decide 5a/5b fixes (save-path reset per iteration; determinism seed).

**Starting position (ticket 20, jobs 33114754/33114755/33115534, ORIG controls valid):** the input meshes are byte-identical (md5 985e4eb1, 55,814 verts both sides), yet our p2 S1 surface is a 171-point scrap matching neither ORIG wall (median 2.8–3.4mm off, <1% coverage) while our p2 S0 is a full wall sitting on ORIG's S1 slot (labels swapped). Our Bl0 walk runs ~3mm off both true rims; our Bl1 is an 18-point stub covering 9.5% of the true path. The search is exonerated (ORIG p2 rim seats 4/4 strict in our bundle). Forest inflates 584 vs ORIG 124 — use it as the cheap signal.

Existing leads (do not re-derive, verify and pin): the size-rank surface assignment (`mesh_processing_headless.cpp:1755-1769`, ticket 02) and the +Z shift entering at the surface stage (ticket 01 gap G5). The fault is downstream of the mesh and upstream of the rim walk — pin the exact file:line where p2's exterior wall is dropped or mislabelled, fix minimally, one variable at a time.

**Measurement rule (ticket 20 finding):** the binary 15/15 bar is loose — it reports perfect with p2 ~10°/40mm off. Acceptance here is the STRICT bar only (5°/10mm relative-edge via `p19_score.py` rule): strict 15/15 on the fresh bundle, ORIG control 8/8+15/15 in the same job or void.

- [ ] Pin the extraction-stage file:line (surface assignment/labelling for p2's exterior wall), fix, rebuild from committed sources, same-binary ORIG control
- [ ] Fixed arm: gate + E2E k=5/b=3, strict 15/15; forest count back toward ~124 as corroboration
- [ ] Laptop poll per sbatch (`sacct` directly); before/after seating render + measurement pair; no commits; Comments-only edits

**Successor:** B–J E2E on admitted fragments (same protocol per pot), then the Juglet question re-opens with a working chain.
