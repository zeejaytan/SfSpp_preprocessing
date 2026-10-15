# 14: Diagnose piece-6's direction miss

**What to build:** a diagnosis, not a fix — one focused ticket answering why the frozen finder misses P06's direction by 8.19° (24.7mm radial) when P06 is a mid-size single-axle piece that should have worked.

**Answers:** E1

**Blocked by:** 12-axle-finder-redesign (frozen finder + V5 evidence below).

**Status:** ready-for-agent

**Starting position (from 12, V5 job 33087310):** `af_find_all` = spatial split → raw-GM vote → frozen per-surface orientation → Huber W=1 refine → peel by inlier count → hard-IRLS×8 polish → position-aware dedup. P06: nset=1, direction 8.19° off, radial 24.7mm. Everything else held-out: P05 direction-right at the material floor (0.48°/2.77mm), P07 1-of-3 near, P08 both missed. Frozen code: `.scratch/pota-repro/p12-stage/axle_finder/` (committed) + Spartan `potsac-p12-run/`. Whatever this ticket finds rewrites the fit set for everything after — ticket 10 stays queued behind it.

**Three hypotheses, in evidence order:**
1. **Base fragment** — P06 may be base (not wall) geometry: different curvature regime, vote solving for the wrong shape family. Check: P06's surface classification + curvature profile vs wall pieces 01–05.
2. **Disjoint sub-parts** — P06 contains two disconnected point regions needing the `af_split` treatment (V2e proved split recovers both axes on synthetic 50/50; fit pieces showed 1 component). Check: run `af_split` diagnostics on P06's input; count components at eps 5/10/20mm.
3. **Vote poverty** — too few pure 6-pt samples from the true mode at 6000 iters (multi-part dilution). Check: inlier fraction of the shipped axle under the frozen cost + winner's margin over truth in vote counts.

**Rules:** diagnose and propose — do not modify `p12-stage/axle_finder/` (experiment copies on Spartan only). P06 may be inspected freely; any fix proposal must state its own re-validation protocol (which pieces stay sealed for it). One hypothesis at a time, each with the measurement that kills or keeps it.

- [ ] Verdict: which hypothesis survives, with numbers (vote counts, margins, component counts, curvature comparison)
- [ ] Fix proposal: exact change + file + re-validation protocol for the follow-up implementation ticket
- [ ] Job IDs + sacct states; no commits; Comments-only ticket edits
