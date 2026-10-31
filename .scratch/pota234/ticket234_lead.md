# Ticket 234: plane-continuity split rule (user-specified)

Status: done
Answers: none (splitter repair; P22 bridge class; curvature-gate candidate from ledger)

## Goal
Replace the splitter's distance-blind angle gate ('do these two neighbouring dots agree within 4.5deg') with a plane-continuity rule the user specified (2026-10-22): keep growing along the SAME PLANE through gradual turns (curves, twists); SPLIT where the turn is sharp (~90deg = a break). Formalized: a dot joins the region if it agrees with the region's fitted plane (seed-plane reference, not last-dot -- so accumulated twist stays inside tolerance); a sharp departure from the plane opens a new face. Test piece: Pot D P22 (fork touch, tab bridge, 232 evidence).

## Boundary
Spartan experiment copy (fresh sfs-fix-234, off main + cure branches); the splitter settings File(s) + rebuild + P22 mesh re-split at the rule's natural operating point(s) + gap table (222 method) + UN/top2 health. No walk changes, no lane changes, no other pieces unless the rule needs a sanity second (P12@4.5 as control only). Do not touch: main worktree, cure branches, .scratch evidence of other tickets, any ticket but this one.

## Constraints
Compare against the region plane, not the last dot (else the twist re-shatters -- this is the load-bearing detail). Report the sharp-turn cutoff used and the plane-fit window. Slot-verify before grading any lane (231 amendment). If the rule cannot separate P22's fork without shattering (UN explodes, top2 collapses), report HONEST-NEGATIVE with the tradeoff numbers, don't tune past it.

## Acceptance criteria
- [ ] P22 fork zone single-face (0 S0 dots within 5mm of the 232 turn dot, 85-S1 pattern or better)
- [ ] Faces not shattered (UN share + top2 within the R6-healthy band: UN<=12%-class, top2>=70%-class -- or report the miss honestly)
- [ ] Control P12@4.5 still selects (no regression on the honest stop)
- [ ] Verdict line: SPLIT-CLEAN / HONEST-NEGATIVE-<tradeoff>

## Lead redirect (2026-10-22, user order -- overrides the plane-continuity spec above)
Park the plane-continuity code on your branch (do not delete). Implement the paper chain (SfS++ Sec IV-B1, lead-read verbatim): (1) region growing from the min-curvature point, n_b=10 neighbours, curvature < tau_kappa=1, normal angle < tau_theta=4deg -- separates interior/exterior/fractured; (2) cluster merging to fixpoint: kNN close pairs between clusters, patch-average normal similarity + boundary-point curvature comparison + internal-point verification, merge all passing pairs, repeat; then B-spline boundary refine + resample; then TWO LARGEST clusters = inner/outer; (3) axis-ray classification: per point, ray along normal to the symmetry axis; intersection on the positive normal side = interior; try both assignments, keep the one with most points satisfying. The paper's own over-segmentation answer is merging, not looser angles. The missing classification IS the swap disease: slot 0 must be interior (assembler reads only slot 0); the fork files surfaces arbitrarily. Acceptance amends: P22 fork single-face + classification labels P22 faces interior/exterior with the majority-vote count + ring control (annulus inner/outer stay the two largest, unmerged). Report which of the three steps carried P22.

## Lead verdict (2026-10-22)
ACCEPT SPLIT-CLEAN (paper arm). R6: 4/4 jobs sacct COMPLETED 0:0 with matching elapsed (53/14/14/10s); binaries + chaincheck byte-match cited; exam table + lane numbers + votes read verbatim; no merges on P22/Jug noted honestly -- carrier was grow-reference fix + classify, merge validated as harmless (one correct non-face merge on P12, zero swallows on four checks). Plane arm HONEST-NEGATIVE, record kept. Caveats carried: P22 Bl0 85.2 (fork-adjacent walk divergence), P22 0.27mm pinch (assembly watch), Jug resample dupe artifact (postamble, downstream ticket). Code-on-branch ordered as follow-up (worker revived via send_message).

## Required evidence to report
sacct COMPLETED for every Slurm job; binaries md5; the cutoff + window; gap table + UN/top2; control numbers; verdict in ticket Comments; leave Status for the lead.

## Comments

### 2026-10-22 — T234 exam report: paper arm v3 (Appendix-A merge) vs parked plane arm

**Binaries / jobs (all sacct COMPLETED 0:0).** Mesh v3 `d72979aaa0055885a4dc88bb51a172e7` (build 33616944, 53s; source md5 `556ef97aacedddadd4df283ccff01d15` = origin/main mesh + patch234.py/b/c/d, chaincheck byte-match TRUE). Edge bin reused `dc472b0e87c934b6c487ff8637209864`. Runs: 33617063 P22-paper3 (14s), 33617064 P12-paper3 (14s), 33617065 Jug1-paper3 (10s). Plane arm parked in the same file behind `SFS_PLANE_RULE` (bin `88b6f406`, full record `.scratch/pota234/plane_notes.md`).

**Operating point (paper arm).** Grow: min-curvature seed order, n_b=10, join iff curvature<1 AND angle-to-current-front-normal<4deg. Merge: Appendix-A Table I verbatim (rhoD=1.0, rhoN=0.95, rhoC=0.1, rhoInN=0.75, rhoInC=0.25, k1=10, k2=30), fixpoint cap 25. Classify: axis-ray vote, both assignments, max satisfying wins, Surface_0=interior. B-spline refine+resample = pre-existing postamble (not reimplemented).

**Provenance per criterion.** Grow params: paper main-text Sec IV-B1 verbatim; angle reference = Rabbani[35]/PCL current-front semantics (v2 correction — fixed-seed v1 over-segmented P12 into 85 grow clusters; current-front gives 11/14/5 for P22/P12/Jug at identical theta/kappa/nb). Merge criteria: Appendix A Table I + Alg 1 (arXiv HTML Appendix A, extracted to `.scratch/pota234/appendixA.txt`). Supplement repo github.com/SeongJong-Yoo/Pottery-Hierarchy-Clear 404s from laptop AND Spartan — implemented from Appendix A instead. CGAL-manual check: CGAL 5.0 shape-detection region growing is a shape-fitting family, not the paper's patch-segmentation params — params implemented directly from the paper text.

**Paper-arm exam (new policy: fragment count not graded; acceptance = post-merge top2 dominate + no break swallowed).**

| piece | grow → post-merge clusters | top2 (of clustered) | merges fired | classify vote (face0/face1) |
|---|---|---|---|---|
| P22 | 11 → 11: 6552/5240/403/143/116/115/101/83/70/57/50 | 11792/12930 = 91.2% | none | 100.0% / 0.0% (satA 11792 vs satB 0, kept) |
| P12 | 14 → 13: 6581/6321/2403/1047/872/262/199/142/91/89/88/60/55 | 12902/18210 = 70.9% | one: 494 → 1909 (both non-face) | 0.0% / 99.5% (satB 12871, swapped → S0=interior) |
| Jug1 ring | 5 → 5: 9279/6931/250/72/64 | 16210/16596 = 97.7% | none | 0.0% / 100.0% (satB 16210, swapped → S0=interior) |

UN (info only, rule retired): P22 5125, P12 3640, Jug 5971 (small-region drops + break go to UN; faces unaffected).

**No break swallowed (four checks).** (1) Votes clean 100/0, 0/99.5, 0/100 — a swallowed break chunk would vote mixed. (2) P22 fork-zone (<5mm turn [-4.15,18.58,439.21]): 0 S0 / 4 S1 — faces stop at the smooth/break boundary (vs plane's 383-dot bleed); the 85-dot @3 pattern was old-splitter face-bleed, not a target. (3) Gap: P12 symmin 5.46/p1 6.25/frac<2mm 0% — tab bridge OPEN; P22 symmin 0.27 pinch located 14.4mm from the fork (edge pinch, not fork overlap). (4) Lanes (slot-verified, bar med<2 + cov>=90): P22 STRAIGHT Bl0→o0 0.80/85.2 (n=135, below-bar cov) + Bl1→o1 0.41/91.6 (n=155, AT-BAR), 0 jumps; P12 STRAIGHT Bl0→o0 0.54/99.3 + Bl1→o1 0.58/99.4, max 2.3/3.4, 0 jumps. P22's 17 missed o0 dots (idx 3–36) form the fork-adjacent stretch 5.7–39mm from the turn — walk divergence at the fork, not swallowed break. P12's 2403/1047/872 tail = break correctly preserved (faces span the full boundary at 99%+ lane coverage, nothing missing to collect).

**Ring control.** Annulus inner/outer = two largest (9279/6931, 97.7%), unmerged, votes 0/100. (Note: filed Jug S0/S1 xyz overlap — 9172 exact-dupe points — a B-spline resample artifact on the ~1mm thin wall, downstream of the chain; cluster-level separation is clean. Plane arm quartered the same ring into 4762/3785/3649/3521.)

**Side-by-side (paper v3 vs plane join60/dist2/W100 vs 223 reference).**

| exam | paper arm | plane arm | winner |
|---|---|---|---|
| P22 fork | single-face 0/4, 1 lane AT-BAR (0.41/91.6), straight slots | single-face 0/383, single 40-dot stub (5.1/10) | PAPER |
| P12 control | both lanes AT-BAR STRAIGHT (0.54/99.3, 0.58/99.4), gap 5.46 | lanes garbage (7.12/0.6, 10.04/10.1), gap 0.0 | PAPER (also beats 223: swapped 0.63/89.0 + 0.77/98.8) |
| Jug ring | top2 97.7% unmerged, votes clean | 18 clusters, top2 35%, annulus quartered | PAPER |

**Which step carried P22.** Grow-reference fix (55 → 11 clusters; fixed-seed v1 shattered, current-front follows twist) + classify (100/0 vote → Surface_0=interior → straight slots, swap disease cured). Merge fired zero times on P22 — grow already separated cleanly; Appendix-A merge validated on P12 (1 merge, no face contamination).

**Verdict: SPLIT-CLEAN (paper arm).** Caveats: P22 Bl0 cov 85.2 below bar (fork-adjacent stretch); P22 0.27mm edge pinch 14mm from fork (watch in assembly); Jug filed-face overlap is a resample artifact (cluster level clean).
