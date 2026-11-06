# 312: Reverse engineer author axis extraction — isolate objective bias, profile constraints, and input cloud provenance

Answers: E1
Blocked by: none (ticket 311 landed; Pot E failure mechanism isolated to objective bias on small sherds)
Status: in-progress
Working in: worker sfs312 (2026-11-06)
Branch: 312-reverse-engineer-author-axes, in /c/PR/worktrees/sfs/312
Worker: sfs312
Budget: large 8
Hand-over: worker with Spartan access; needs MATLAB / Python / C++ access to SfSpp pipelines and Spartan scratch. Judgement stays with the lead.


## What to build

In ticket 311, we established on Pot E that:
1. **The reference axes are physically accurate:** On 9 of the 10 failing pieces (`Pieces 03, 09, 23, 24, 25, 26, 27, 28, 29`), the authors' released axis is within **0.91° to 14.46°** of the Ground Truth axis (`original_samples/SfS_pp/Ground Truth Axes/`), and seats all 31 sherds and 62 joins (100.0%) under the assembler in `E_MO`. Piece 31 is the single outlier (54.77° from GT).
2. **The method fails on isolated sherd clouds:** Our optimization of the paper's Cao/Mumford Huber loss on the shipped surface point clouds ($S0, S1$) converges to false local minima **17.5° to 58.7°** away from the true axis. Even when Levenberg–Marquardt is initialized directly at the true axis, it drifts **10.3° to 85.5°** downhill onto our false basins (`conv_nearest_310_deg = 0.000° to 0.003°`). In 10,000-draw MLESAC pools on the sherd clouds, 0 of 10,000 draws ever land within 10° on 8 pieces.
3. **The failure is (1) The Method:** The unconstrained Huber objective evaluated on isolated small sherd point clouds fails to place the true vessel axis at a local minimum.

While the user contacts the first author (Dominico Ryu), this ticket investigates how the authors obtained their seating axes from the data. Specifically, it tests four concrete hypotheses across Steps 2 through 5:
- **Step 2 (Diagnostic):** Energy landscape and lever-arm centroid bias — does the Cao/Mumford metric pull candidate axes toward the sherd centroid to minimize distance penalties?
- **Step 3 (Input perturbations):** Surface representation and cloud provenance — do full-mesh re-estimated normals, breakline edge trimming (1–3 mm), single-wall $S0$ vs $S1$ fitting, or raw mesh vertices alter the energy landscape?
- **Step 4 (Objective refinements):** Missing mathematical constraints — does re-enabling the polynomial cross-section profile consistency check ($V_{\text{poly}}$ from the authors' commented-out MATLAB `compute_potsac_v2_cost`) or a distance-invariant normal alignment loss restore the true axis basin?
- **Step 5 (Corpus-wide reference audit):** Benchmark-wide Ground Truth comparison — comparing authors' released axes against Ground Truth across all 163 pieces in Pots A–K to reveal whether released axes were derived from isolated sherds or assembled/whole-vessel geometry.

---

### Step 2: Energy Landscape & Lever-Arm Centroid Bias Audit (Diagnostic)

1. **Centroid Lever-Arm Distance:**
   For all 34 Pot E pieces, compute the orthogonal lever-arm distance $d(C, L)$ from candidate axis line $L$ to the sherd point cloud centroid $C = \frac{1}{|P|} \sum_{p \in P} p$:
   $$d(C, L) = \frac{\|(C - p_0) \times a\|}{\|a\|}$$
   Compare $d(C, L_{\text{true}})$ (using Ground Truth / Authors' released axis) against $d(C, L_{\text{min}})$ (using our Huber rank-1 basin). Determine whether the Huber optimizer systematically favors axes that pass close to or through the sherd centroid ($d(C, L_{\text{min}}) \ll d(C, L_{\text{true}})$) due to distance penalties in the Cao/Mumford metric.
2. **1D Geodesic Loss Profiles:**
   For the 10 failing pieces (`03, 09, 23, 24, 25, 26, 27, 28, 29, 31`), sample the Huber energy landscape along the geodesic path connecting the true axis $L_{\text{true}}$ and the Huber basin $L_{\text{min}}$:
   $$L(t) = \text{slerp}(a_{\text{true}}, a_{\text{min}}, t), \quad p_0(t) = (1-t) p_{0,\text{true}} + t p_{0,\text{min}}, \quad t \in [0, 1]$$
   Plot the loss profile $E(t)$. Determine whether $L_{\text{true}}$ is on a monotonic downhill slope toward $L_{\text{min}}$, or if an energy barrier separates them.

### Step 3: Input Cloud Perturbations & Surface Provenance

The authors' MATLAB script `read_surfaces.m` contains commented-out paths referencing alternate directories (`Surface_axis/`, `D:/240718/GT`, `Data_change/H(re)`, `obj_samples_Int/Ext.xyz`), indicating alternate surface processing. Test whether the energy landscape is sensitive to how the surface points and normals are represented:
1. **Mesh-Recomputed Normals:**
   Recompute surface normals directly from the original mesh files in `original_samples/SfS_pp/Meshes/Pot_E_Piece_*.obj` using varying neighborhood radii ($r \in \{1.0, 2.0, 5.0\}$ mm, with PCA plane and quadric surface fitting). Shipped normals in `Surfaces/` may have been smoothed or filtered. Test if re-estimated normals shift the Huber minimum toward the true axis.
2. **Breakline Edge Erosion Trimming:**
   Sherd boundaries near fracture surfaces often contain degraded normals or scanning chamfers. Trim points within $d_{\text{edge}} \in \{1.0, 2.0, 3.0\}$ mm of the breakline points in `original_samples/SfS_pp/Point cloud/`. Test whether excluding edge points eliminates the false minimum.
3. **Single-Wall vs Joint-Wall Optimization:**
   On the 10 failing pieces, independent Huber fits on $S0$ (interior) and $S1$ (exterior) disagree by 20.1° to 37.0°. Fit the Huber loss on $S0$ only and $S1$ only. Determine if either single wall contains a stationary point close to the true axis.
4. **Dense Mesh Vertices vs Downsampled Clouds:**
   Test optimization directly on raw mesh vertices without the equidistant downsampling to check whether downsampling aliased the surface curvature.

### Step 4: Objective Refinements & Missing Constraints

1. **Re-enabling Cross-Section Polynomial Profile Consistency ($V_{\text{poly}}$):**
   In the authors' released MATLAB script `run_potsac.m`, lines calling `compute_potsac_v2_cost` (which fits a polynomial profile $r(z)$ to the rotated points) are commented out.
   - Implement/re-enable the polynomial profile check $V_{\text{poly}}$ on candidate axes.
   - For an axis passing through or near the sherd centroid, the radial distances $r_i$ and heights $z_i$ produce a wildly distorted profile with huge polynomial fitting residuals. In contrast, the true vessel axis produces a smooth profile consistent with a surface of revolution.
   - Test whether adding a profile consistency penalty $E_{\text{total}} = E_{\text{Huber}} + \lambda V_{\text{poly}}$ eliminates the false centroid-hugging basins.
2. **Distance-Invariant / Normal Alignment Objective:**
   - Test an objective that decouples normal orientation from point-to-axis distance:
     $$E_{\text{normal}}(a, p_0) = \sum_{i} \rho\left( \frac{(p_i - p_0) \cdot (n_i \times a)}{\|(p_i - p_0) \times a\|} \right)$$
     or minimizing the variance of $(p_i - p_0) \cdot n_i$ without penalizing distance to the axis.
   - Test whether removing the distance penalty allows the true axis to become the global minimum.
3. **Rim Coplanarity Constraint:**
   - For pieces bearing rim segments, enforce that the rim plane normal is collinear with the rotation axis candidate.

### Step 5: Benchmark-Wide Reference vs Ground Truth Audit (163 Pieces)

1. **Full Benchmark Audit:**
   Compute the angular difference $\theta = \angle(L_{\text{released}}, L_{\text{GT}})$ and spatial distance $\Delta d$ at the vessel centroid for all 163 pieces in Pots A through K (`original_samples/SfS_pp/Axes/` vs `Ground Truth Axes/`).
2. **Categorization:**
   Group all 163 pieces into:
   - *High-concordance ($\theta < 3^\circ$):* axes consistent with whole-vessel geometry.
   - *Moderate concordance ($3^\circ \le \theta < 10^\circ$):* typical isolated sherd fits.
   - *Deviated ($10^\circ \le \theta < 25^\circ$):* marginal fits.
   - *Gross outliers ($\theta \ge 25^\circ$):* severe discrepancies (such as Pot E Piece 31 at 54.8°, or unscoreable reference pieces in Pot C and Pot J).
3. **Physical Correlates:**
   Correlate $\theta$ with piece surface area, bounding box aspect ratio, wall thickness, and sherd position (rim, body, base).
4. **Synthesis:**
   Synthesize findings to determine whether the released reference axes could have been produced piece-by-piece from isolated sherds or whether they were extracted from global registered scans.

---

## Acceptance Criteria

- [ ] A1: Lever-arm distance table $d(C, L)$ and 1D geodesic energy profiles for all 34 Pot E pieces comparing Ground Truth axes against Huber minima, confirming or refuting centroid proximity bias.
- [ ] A2: Input perturbation ablation table on the 10 failing Pot E pieces (mesh normals with varying radius, breakline trimming at 1–3 mm, single-wall $S0$ vs $S1$).
- [ ] A3: Objective refinement results on the 10 failing pieces: profile polynomial consistency ($V_{\text{poly}}$ from MATLAB `compute_potsac_v2_cost`) and distance-invariant normal alignment loss.
- [ ] A4: Full corpus audit table (all 163 pieces) comparing Authors' Released Axes vs Ground Truth Axes, with physical metrics (degrees, mm) and concordance categorization.
- [ ] A5: Before/after renders of candidate axes and reconstructed profiles relative to Ground Truth vessel geometry staged in `artifacts/pota312/renders/`.
- [ ] A6: All runs tracked by standard run directories, `substitution.tsv` / `acc.tsv` records on Spartan, corpus md5 unchanged.

## Instruments to reuse

- Surface and mesh tools: `SfSpp_preprocessing/` mesh processing, `scripts/` render utilities.
- MATLAB POTSAC code: `SfSpp_preprocessing/.scratch/pota-repro/matlab/` (`run_potsac.m`, `compute_potsac_v2_cost.m`, `read_surfaces.m`).
- Axes evaluation harness: `artifacts/pota311/stageCD/` (`pot_e_ref_stationarity.tsv`, `stagec_summary.tsv`).

## Operating rules

- Comments-only edits to this ticket during execution; worker reports, lead concludes and lands.
- Heavy jobs run on Spartan compute nodes; every `sbatch` gets a poll and its final `sacct` recorded.
- Visualizations required for all geometry claims; clickable workspace-relative links in comments.
- Never modify corpus files in `original_samples/SfS_pp`.
