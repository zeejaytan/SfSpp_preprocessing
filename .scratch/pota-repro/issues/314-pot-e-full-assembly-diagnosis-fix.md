# 314: Pot E full 31/31 assembly — diagnose remaining 7 failing pieces and purge perpendicular decoys

**What to build:** Diagnose and fix the remaining shortfall on Pot E (currently seated at 24/31 sherds, 44/62 joins in Ticket 313, compared to the authors' released control of 31/31 sherds, 62/62 joins). In Ticket 313, distance-invariant normal loss eliminated the centroid collapse lever-arm bias and broke the 23/31 ceiling. However, 7 pieces (`03, 23, 24, 25, 26, 28, 31`) remain unseated under $K=2$. In this ticket, the worker will eliminate the `is_base_sherd` Trojan that misclassifies perpendicular wall-slicing decoys as base pieces, purge whole-sherd axial normal decoys, promote the true vessel rotation axes ($d \approx 70$–$80$ mm, $<10^\circ$ from GT) to top-2 candidate ranks, run the Pot E assembly to match 31/31 sherds (62/62 joins), and verify whole-corpus non-regression across Pots A, B, D, G, and I.

**Answers:** E1

**Blocked by:** none (Ticket 313 landed on main)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-07)
**Branch:** 314-pot-e-full-assembly-diagnosis-fix, in /c/PR/worktrees/sfs/314

**Worker:** unassigned

**Budget:** large 8

**Hand-over:** worker with Spartan access; needs `sfs_axes` Python package, Spartan Slurm access, and C++ SIF assembler harness. Judgement stays with the lead.


## Context & Diagnostic Findings

In Ticket 313, distance normalization $\hat{e}_i = \frac{(p_i - p_0) \cdot (n_i \times a)}{\|(p_i - p_0) \times a\|}$ eliminated the centroid lever-arm collapse on thin sherds, breaking the Pot E assembly from 21/31 (36/62 joins) up to 24/31 (44/62 joins) at $K=2$, and achieving a major breakthrough on Pot D (26/28 sherds, 63/69 joins vs paper's 23/28, 55/69).

However, Pot E did not reach 31/31. Investigation of Spartan run `20261106-1330_fe906ab_t313b-kladder-E` and raw candidate files reveals the exact mathematical cause of the remaining 7 unseated pieces:

### 1. The Seven Unseated Pieces Form an Interdependent Subgraph
The 7 unseated pieces in `E_K2R2` are `03, 23, 24, 25, 26, 28, 31`:
- Piece 31 is the single genuine base fragment of Pot E. Its only joins are with pieces `24, 25, 28`.
- Pieces `24, 25, 26, 28` form the lower wall ring adjacent to the base.
- Pieces `03, 23` connect to this lower ring and the upper walls.
Because pieces `24, 25, 26, 28` fail to seat, piece 31 has zero seated neighbors and cannot connect to the vessel assembly.

### 2. The `is_base_sherd` Trojan Misclassifies Perpendicular Wall Slicers
In `sfs_axes/potsac.py`, the base-detection heuristic was defined as:
```python
def is_base_sherd(X, vt):
    ...
    r = np.linalg.norm(dp - a[:, None] * (a @ dp)[None, :], axis=0)
    near = r < 20.0
    if np.sum(near) < 50:
        return False
    axial = np.abs(a @ N[:, near])
    return bool(np.mean(axial) > 0.80)
```
When a candidate axis slices directly through a wall sherd at a near-perpendicular angle ($a \approx n_{\text{wall}}$):
1. It passes within $r < 20$ mm of the wall points around the cut.
2. Because $a$ points parallel to the wall normal, $|a \cdot n| \approx 1.0 > 0.80$.

Consequently, `is_base_sherd` **classifies perpendicular centroid-slicing decoys as base sherds** on Pieces 03, 23, 24, 26, and 28!
When classified as a base sherd:
- The 25 mm clearance penalty is completely waived (`min_clearance_mm = 0.0`).
- Because a locally flat wall patch has near-zero normal deviation in the direction of its own normal vector, these perpendicular decoys achieve artificially tiny Huber costs ($0.009$–$0.02$).
- The perpendicular decoys claim Rank 0 and Rank 1 on Pieces 03 and 26, pushing the true rotation axes down or out of the pool.

### 3. The True Axes Already Exist in the Candidate Pool
Pottmann draws and Levenberg-Marquardt refinement already discover the true rotation axis on all failing pieces:
- **Piece 03:** Candidate exists at **5.75° from GT** ($d = 50.8$ mm, true vessel radius).
- **Piece 24:** Candidate exists at **8.28° from GT** ($d = 78.4$ mm, true vessel radius).
- **Piece 25:** Candidate exists at **13.69° from released** ($d = 67.1$ mm, true vessel radius).
- **Piece 26:** Candidate exists at **9.18° from GT** ($d = 66.8$ mm, true vessel radius).
- **Piece 28:** Candidate exists at **9.9° from GT** ($d = 67.0$ mm, true vessel radius).

Under $K=2$, the true axes on Pieces 24, 25, 26 were dropped because they were pushed to Rank 2, 3, or 5 by the Trojan decoys. Under $K=6$, the assembly failed because the Trojan perpendicular decoys were emitted into the C++ assembler, triggering combinatorial explosion in beam search.

---

## What to Implement and Verify

### Stage A: Clean Base Classification & Perpendicular Decoy Purge
1. **Intrinsic Base Detection:** Replace axis-dependent `is_base_sherd(X, vt)` with an intrinsic check on the sherd: only a sherd that genuinely contains the circular vessel base (e.g. points spanning azimuth $\Delta \theta \ge \pi$ around the axis with low radial variance, or an explicit base-flag) may have $d(C, L) < 25$ mm. Wall pieces (`03, 23, 24, 25, 26, 28`) must strictly enforce $d \ge 25$ mm.
2. **Whole-Sherd Axial Decoy Filter:** On any surface of revolution, the rotation axis is roughly parallel to the wall ($a \perp n$, so mean $|a \cdot n| \ll 1$). Reject candidate axes where the whole-sherd mean axial normal exceeds 0.50 (axes pointing out of the vessel wall).
3. **Physical Vessel Radius Band:** For wall sherds of Pot E ($R_{\text{vessel}} \approx 75$ mm), candidates in the physical radius band ($40 \le d \le 120$ mm) must be prioritized over degenerate infinite-radius lines ($d > 200$ mm).
4. **Diagnostic Check:** Verify that on all 7 pieces (`03, 23, 24, 25, 26, 28, 31`), the true rotation axes (angles $<10^\circ$ to GT or released) are ranked at Rank 0 or Rank 1.

### Stage B: Pot E C++ Assembly on Spartan
1. Generate cleaned axes for Pot E (`axes314`).
2. Run the C++ assembler harness (`sfspreproc.sif` / `CountResult`) across candidate ladders $K \in \{1, 2, 3\}$ for repeats R1 and R2.
3. Target: Break past 24/31 sherds and 44/62 joins toward **31/31 sherds (62/62 joins)**, matching the authors' released control.

### Stage C: Whole-Corpus Non-Regression Gate
Run the non-regression grid across all reference pots on Spartan compute nodes:
- Pot B: verify 9/9 sherds (15/15 joins, 100%).
- Pot G: verify 7/7 sherds (10/10 joins, 100%).
- Pot I: verify 25/26 sherds (59/62 joins, 95.2%).
- Pot D: verify $\ge 26/28$ sherds ($\ge 63/69$ joins), preserving the Ticket 313 breakthrough.
- Pot A: verify 8/8 sherds (15/15 joins), ensuring Piece 08 is seated with relaxed `MAX_CLEARANCE_MM = 250.0`.

### Stage D: Visual Proof and Artifacts
1. Render reconstructed vessel assemblies for Pot E (and any modified corpus pots) in `artifacts/pota314/renders/`.
2. Save raw score TSVs in `artifacts/pota314/`.
3. Verify byte-for-byte corpus integrity in `original_samples/SfS_pp` (`0 diff`).

---

## Acceptance Criteria

- [ ] `tests/test_normalized.py` and any new unit tests pass cleanly (100%).
- [ ] Trojan `is_base_sherd` bypass eliminated: wall pieces `03, 23, 24, 25, 26, 28` enforce $d \ge 25$ mm; perpendicular decoys ($|a \cdot n| > 0.50$) purged.
- [ ] On all 7 failing Pot E pieces, true rotation axes ($<10^\circ$ from GT/released, $d \approx 65$–$80$ mm) rank within the top $K \le 2$ candidates.
- [ ] Pot E assembly on Spartan compute node seats $\ge 28/31$ sherds and $\ge 55/62$ joins (targeting 31/31 sherds, 62/62 joins), matching or closely approaching the released reference.
- [ ] Zero regression across Pots A, B, D, G, I (Pot A 8/8, Pot B 9/9, Pot G 7/7, Pot I 25/26, Pot D $\ge 26/28$).
- [ ] Visual renders staged in `artifacts/pota314/renders/` with clickable workspace-relative links.
- [ ] Corpus integrity verified byte-identical (`0 diff` in `original_samples/SfS_pp`).
- [ ] Code tickets: branch merged into main and pushed, no job still running from it, worktree removed, branch deleted locally and on GitHub.
