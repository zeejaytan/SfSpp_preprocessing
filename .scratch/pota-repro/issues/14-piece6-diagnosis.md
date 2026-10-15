# 14: Diagnose piece-6's direction miss

**What to build:** a diagnosis, not a fix — one focused ticket answering why the frozen finder misses P06's direction by 8.19° (24.7mm radial) when P06 is a mid-size single-axle piece that should have worked.

**Answers:** E1

**Blocked by:** 12-axle-finder-redesign (frozen finder + V5 evidence below).

**Status:** results-in

## Comments (worker, 2026-10-15)

**Starting position (from 12, V5 job 33087310):** `af_find_all` = spatial split → raw-GM vote → frozen per-surface orientation → Huber W=1 refine → peel by inlier count → hard-IRLS×8 polish → position-aware dedup. P06: nset=1, direction 8.19° off, radial 24.7mm. Everything else held-out: P05 direction-right at the material floor (0.48°/2.77mm), P07 1-of-3 near, P08 both missed. Frozen code: `.scratch/pota-repro/p12-stage/axle_finder/` (committed) + Spartan `potsac-p12-run/`. Whatever this ticket finds rewrites the fit set for everything after — ticket 10 stays queued behind it.

**Three hypotheses, in evidence order:**
1. **Base fragment** — P06 may be base (not wall) geometry: different curvature regime, vote solving for the wrong shape family. Check: P06's surface classification + curvature profile vs wall pieces 01–05.
2. **Disjoint sub-parts** — P06 contains two disconnected point regions needing the `af_split` treatment (V2e proved split recovers both axes on synthetic 50/50; fit pieces showed 1 component). Check: run `af_split` diagnostics on P06's input; count components at eps 5/10/20mm.
3. **Vote poverty** — too few pure 6-pt samples from the true mode at 6000 iters (multi-part dilution). Check: inlier fraction of the shipped axle under the frozen cost + winner's margin over truth in vote counts.

**Rules:** diagnose and propose — do not modify `p12-stage/axle_finder/` (experiment copies on Spartan only). P06 may be inspected freely; any fix proposal must state its own re-validation protocol (which pieces stay sealed for it). One hypothesis at a time, each with the measurement that kills or keeps it.

- [x] Verdict: which hypothesis survives, with numbers (vote counts, margins, component counts, curvature comparison)
- [x] Fix proposal: exact change + file + re-validation protocol for the follow-up implementation ticket
- [x] Job IDs + sacct states; no commits; Comments-only ticket edits

## Comments (worker, 2026-10-15)

**Verdict: H1 killed, H2 killed, H3-as-stated killed — but a refined H3′ survives:
the vote finds the truth; the Huber refine walk destroys it.**
P06's 8.19°/24.73mm miss is a selection↔refinement cost mismatch, not a base
fragment, not disjoint parts, not sample poverty. One job, no finder edits.

**H1 base fragment — KILLED.** P06 is wall geometry, on every number:
radius-to-shipped-axis median 84.2/86.7mm (S0/S1) vs wall pieces P02–P05 at
78–85mm; normal-vs-axis |T3| median 0.702/0.705 vs 0.66–0.69 on P02–P05
(normals perpendicular to the axis = wall-like); flat-like fraction
(|T3|<0.3) 0.019/0.003 — the *least* flat of all pieces measured (P02–P05:
0.03–0.13, P01: 0.37–0.94). P06 is a tall narrow wall strip (span 37×116×39mm,
radius IQR only 11–12mm vs 18–20mm on P02–P05). Aside: P01 is the real
curvature outlier (Rmed 38–44mm, S0 flat-like 0.94) yet its direction passes —
worth knowing, not this ticket's question. Shipped-axle orientation on P06 is
unanimous-pattern rev=[1 0] (S0→REV, S1→fwd), so orientation-freeze is not the culprit.

**H2 disjoint sub-parts — KILLED.** `af_split` on P06's full cloud (n=13891):
1 component at eps 5, 10 and 20mm (all points in one component), identical to
the P05 wall control (1 component, n=19107, at all three eps). No `af_split`
treatment applies — there is nothing disjoint to split.

**H3 vote poverty — killed as stated; the truth is not starved, it is
abandoned.** Shipped axle holds 6529 tight inliers (frac 0.470 — a strong mode,
not a weak one). In a faithful round-1 replica vote (6-pt, 6000 iters, seed 1,
GM cost on the same 10% subsample): shipped cost 1477 vs best-candidate cost
1516 — **truth ranks 1/6000**, 2.7% better than anything random sampling found;
min candidate angle to truth 0.30°, 165 candidates within 5°, 584 within 10°.
Sampling is ample. But the frozen chain still outputs 8.19°/24.73mm off with
winner inliers 6527 vs truth's 6529 — a 2-point near-tie the peel never gets to
judge, because **refine-from-shipped walks to 8.21°/24.75mm**: the fixed-orient
Huber-W=1 refine (`af_refine_raw`) drains away from the GM-cost minimum to the
same spurious pocket the finder reports. Truth is the selection cost's minimum
but not the refinement cost's fixed point — the handoff crosses two different
costs, and on P06's narrow-strip geometry (weak axis constraint along the
strip) the Huber basin minimum sits ~8° away. Consistent with V1f (refine
walked away on all four fit pieces too): a general refine-basin mismatch,
worst on P06.

**Fix proposal (for the follow-up implementation ticket, not this one):**
align the refine cost with the selection cost. Candidates in evidence order:
(a) refine under the GM robustifier instead of Huber (same stationary points
as the vote that ranked truth #1) — touches `axle_finder/af_refine_raw.m`
residual only; (b) multi-start refine of top-K diverse vote modes, winner by
GM cost rather than post-refine inlier count — touches `af_find_seq.m`;
(c) guard: reject refine walks that increase GM cost beyond a tolerance.
Recommend (a) first: smallest change, directly targets the measured mechanism
(refine-from-shipped stability). Re-validation protocol: develop on fit pieces
01–04 with a new bar — refine-from-shipped must stay ≤5°/≤2mm on all four
(currently walks away on all four per V1f) — then one confirmation run on P06;
**pieces 05, 07, 08 stay sealed** until the frozen validation (P06 is
inspection-open per this ticket's rules; 05/07/08 were run once in V5 and must
not be tuned against).

**Jobs:** 33092580 (p14-diag: H1 profile 01–06 + H2 split P06/P05 + H3 vote,
refine-from-shipped, finder repro) — sacct State COMPLETED, ExitCode 0:0,
Elapsed 00:01:16. Finder repro inside it confirms V5 P06 (nset=1, 8.19°/24.73mm).
No commits made; `p12-stage/axle_finder/` untouched (diagnostic lives in
`.scratch/pota-repro/p14-stage/` + Spartan `potsac-p14-run/`).
