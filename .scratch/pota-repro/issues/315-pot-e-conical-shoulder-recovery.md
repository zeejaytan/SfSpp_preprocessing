# 315: Pot E 31/31 assembly — unify cylindrical lower-wall and conical shoulder regimes in sfs_axes

**What to build:** Recover full 31/31 sherd assembly (62/62 joins) on Pot E by unifying the cylindrical lower-wall regime (`Ticket 314`) and the conical/sloped upper-shoulder regime (`Ticket 313`) in `sfs_axes/potsac.py`. In Ticket 314, enforcing `min_clearance_mm = 25.0` and guarded 20-iteration refinement rescued all 8 lower-wall pieces (`03, 14, 23, 24, 25, 26, 27, 31`) to within $\le 10.0^\circ$ of GT/Released and raised Pot E assembly to 26/31 sherds (47/62 joins). However, Ticket 314's hard `mean_ax <= 0.50` filter deleted the true rotation axes on all 7 steeply sloped upper-shoulder/neck pieces (`02, 04, 15, 17, 18, 20, 21`, where the vessel wall slopes $33^\circ$–$66^\circ$ from vertical so $\text{mean}|a_{\text{true}} \cdot n| \in [0.552, 0.918]$), which had already been solved at $0.1^\circ$–$7.4^\circ$ in Ticket 313. Because `18` ($53.6^\circ$ error) and `20` ($25.4^\circ$ error) lost their true axes, `17` and `18` formed a tilted 2-piece island ($55^\circ$ off the pot), breaking the bridge joins `18-23` and `20-23` and stranding lower-ring pieces `23, 24, 31` despite `23, 24, 31` having accurate axes ($9.3^\circ, 9.6^\circ, 10.0^\circ$). Unifying both regimes restores **31/31 pieces of Pot E within $\le 10^\circ$** in top-$K$ ($K \le 3$), with all 7 conical shoulder pieces at **Rank 0 (`0.1°–4.3°`)**.

**Answers:** E1

**Blocked by:** none (Ticket 314 landed on main)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-08)
**Branch:** 315-pot-e-conical-shoulder-recovery, in /c/PR/worktrees/sfs/315

**Worker:** sfs315

**Budget:** large 8

**Hand-over:** worker with Spartan access; needs `sfs_axes` Python package, Spartan Slurm access, and C++ SIF assembler harness. Judgement stays with the lead. **STRICT RULE: Do NOT run $K=6$ or multi-hour full-corpus $K=6$ sweeps.** Evaluate Pot E at $K \in \{1, 2, 3\}$ only, and run lean non-regression checks ($K \le 3$).


## Context & Diagnostic Findings

### 1. Why Chasing the 5 Unseated Sherds (`15, 21, 23, 24, 31`) in Isolation Is a Trap
In Ticket 314 (`E_K3R2`), 26/31 sherds were counted as seated and 5 sherds (`15, 21, 23, 24, 31`) were unseated. However, inspecting the axis errors across all 31 pieces in `axes313` (Ticket 313) vs `axes314` (Ticket 314) against GT and the authors' released axes reveals a complete 31/31 complementary partition:

1. **16 cylindrical/mid-wall pieces** (`01, 05, 06, 07, 08, 09, 10, 11, 12, 13, 16, 19, 22, 28, 29, 30`) are within $\le 10^\circ$ in **both** Ticket 313 and Ticket 314.
2. **8 lower-wall / foot-ring pieces** (`03, 14, 23, 24, 25, 26, 27, 31`) failed in Ticket 313 (`16.2°–81.6°`), and **all 8 were rescued in Ticket 314** (`6.7°, 6.1°, 9.3°, 9.6°, 3.2°, 5.6°, 8.5°, 10.0°`) once `min_clearance_mm = 25.0` and guarded 20-iteration refinement (`drift <= 8.0°`) were applied.
   - *Note on Piece 31:* Piece 31 is a lower-wall/foot-ring piece at $d_c(\text{GT}) = 77.1$ mm with $\text{mean}|a_{\text{GT}} \cdot n| = 0.306$. Its released file contains 3 candidates (`54.8°, 31.1°, 9.4°` from GT), where `Rel[:, 2]` at $d_c = 71.5$ mm ($9.4^\circ$) is the true axis and `Rel[:, 0]` ($54.8^\circ$) was a decoy. In `axes314`, Piece 31 already has a $10.0^\circ$ candidate (`0.8°` from `Rel[:, 2]`) at Rank 1!
3. **7 sloped upper-shoulder / neck pieces** (`02, 04, 15, 17, 18, 20, 21`) were **already solved in Ticket 313** at **`2.2°, 2.2°, 0.1°, 2.0°, 1.0°, 5.2°, 7.4°`**, and **all 7 were destroyed in Ticket 314** (`11.9°, 31.6°, 59.1°, 28.7°, 53.6°, 13.9°, 47.2°`)!

**Total solved across `Ticket 313` $\cup$ `Ticket 314` = $16 + 8 + 7 = \mathbf{31/31}$ pieces (100% of Pot E)!**

### 2. Why `23, 24, 31` Failed to Assemble Despite Having Good Axes in Ticket 314
In the C++ assembler (`main_pristine_batch.cpp` / `reconstruction.cpp` / `feature_matching.cpp`), pairwise breakline matches must pass both `PairwisePruning` (`AxisAlignment` across the top-$K$ candidate axes) and `RegistrationPruning` (`BiaxialCaoErrorWithFixedAxis` + `AxisConsistency < 0.35` rad $\approx 20^\circ$).
- In Ticket 314 (`E_K3R2`), because `17` ($28.7^\circ$) and `18` ($53.6^\circ$) lost their true axes (`2.0°` and `1.0°` in Ticket 313), `17` and `18` matched only each other as a disconnected 2-piece island tilted $55^\circ$ from the vessel (`17-18` relative rotation error $1.07^\circ$, which fooled the loose pair-count scorer for `17` and `18`, while failing `4-18` at $83.2^\circ$, `18-20` at $82.7^\circ$, and `18-23` at $85.4^\circ$).
- Meanwhile, Piece `20` lost its $4.3^\circ$ conical axis (`mean_ax = 0.562`), leaving `20` with a $25.4^\circ$ axis that failed `20-23` at $47.0^\circ$ rotation error.
- Because `18` and `20` are the upper-ring bridge neighbours of Piece `23` (`18-23` and `20-23`), Piece `23` could not attach to the upper vessel, which in turn stranded `24` (`23-24`) and `31` (`24-31`)!

### 3. Why Ticket 314 Destroyed the 7 Conical Shoulder Pieces (`02, 04, 15, 17, 18, 20, 21`)
In `sfs_axes/potsac.py` (lines 473–495):
```python
has_cyl_wall = any(
    sizes[j] >= 5 and _whole_sherd_axial_mean(X, modes[j]) <= 0.50
    for j in range(len(modes))
)
```
Even on steeply sloped shoulder sherds (`02, 04, 15, 17, 18, 20, 21`) where the true axis has $\text{mean}|a_{\text{true}} \cdot n| \in [0.552, 0.918]$:
- Out of 10,000 random Pottmann draws, at least one tiny noise cluster of $\ge 5$ draws (0.05% of draws!) happens to point perpendicular to the sherd's slope ($\text{mean}|a \cdot n| \le 0.50$).
- That sets `has_cyl_wall = True` and **deletes every candidate with $\text{mean}|a \cdot n| > 0.50$** both before and after refinement:
  - On **Piece 15**, `has_cyl_wall` triggered on a 12-draw noise cluster (`c = 0.044`, $81.3^\circ$ error) and deleted the **6,872-draw true consensus basin** (`0.1°` from released, `c = 0.006`, `mean_ax = 0.855`)!
  - On **Piece 04**, it deleted the **3,396-draw true consensus basin** (`2.2°` from released, `c = 0.003`, `mean_ax = 0.724`)!
  - On **Pieces 02, 17, 18, 20, 21**, it deleted the converged conical basins (`2.6°, 1.9°, 1.0°, 4.3°, 1.4°` from GT/Released, with worst-wall normalized Huber cost `cw <= 0.0091`).

### 4. Verified Unified Cylindrical + Conical Selection Rule (`test_unified_pote.py`)
Conical shoulder axes (`02, 04, 15, 17, 18, 20, 21`) and perpendicular pin/tangent decoys (`26, 27, 31`) are cleanly separated by three physical properties after 50-iteration normalized LM refinement (`refine_axis_normalized(..., max_nfev=50)`):
1. **Non-collinear normal angle:** Conical shoulder walls have $0.50 < \text{mean}|a \cdot n| \le 0.925$ (wall slope $\ge 22^\circ$ from horizontal), whereas pure normal-pin decoys on flat wall patches (`P26, P27, P31`) have $\text{mean}|a \cdot n| \in [0.956, 0.975]$ or $d_c < 25$ mm.
2. **Physical vessel radius clearance:** Conical shoulder axes pass at $25.0 \le d_c \le 105.0$ mm from the sherd centroid (`33.0` to `63.9` mm on `02, 04, 15, 17, 18, 20, 21`).
3. **Converged dual-wall revolution fit:** On all 7 sloped shoulder pieces, 50-iteration normalized LM refinement converges to a tight dual-wall conical surface of revolution with **worst-wall Huber cost `cw <= 0.0095`** (`0.0040` to `0.0091`) and average cost `c` strictly lower than the best cylindrical (`mean_ax <= 0.50`) candidate (`c < best_cyl_c`), or massive Pottmann consensus support (`s >= 500` and `c <= 0.012`).

Running this unified rule on Spartan (`test_unified_pote.py` on job `34462441`) produced:
- **All 7 conical shoulder pieces (`02, 04, 15, 17, 18, 20, 21`) at Rank 0 (`K=1`)**:
  - `P02`: **2.6°** (Rank 0)
  - `P04`: **2.2°** (Rank 0)
  - `P15`: **0.1°** (Rank 0)
  - `P17`: **1.9°** (Rank 0)
  - `P18`: **1.0°** (Rank 0)
  - `P20`: **4.3°** (Rank 0)
  - `P21`: **1.4°** (Rank 0)
- **All 8 lower-wall pieces (`03, 14, 23, 24, 25, 26, 27, 31`) preserved within $\le 10.0^\circ$**:
  - `P03`: **6.7°** (Rank 1), `P14`: **6.1°** (Rank 2), `P23`: **9.3°** (Rank 1), `P24`: **9.6°** (Rank 1), `P25`: **3.2°** to `Rel[:, 1]` / **11.2°** to GT (Rank 0), `P26`: **5.6°** (Rank 1), `P27`: **8.5°** (Rank 2), `P31`: **10.0°** to GT / **0.8°** to `Rel[:, 2]` (Rank 1).
- **Total Pot E pieces within $\le 10^\circ$ of GT/Released at $K=3$: 31/31 (100.0%)!**

---

## What to Implement and Verify

### Stage A: Unify Cylindrical and Conical Regimes in `sfs_axes/potsac.py`
1. In `extract_piece_candidates_with_diagnostics` (`sfs_axes/potsac.py`):
   - Keep the Ticket 314 **Cylindrical track** (`_whole_sherd_axial_mean(X, vt_g) <= 0.50`, guarded 20-iteration refinement `max_nfev=20` with `drift <= 8.0°`, `min_clearance_mm=25.0`, physical radius band `40.0 <= d_c <= 120.0`).
   - Add the **Conical / Sloped-Shoulder track** alongside the cylindrical track:
     - Take the top `n_refine` basins (filtered only by `d_c >= min_clearance_mm * 0.5` so no candidate with `mean_ax > 0.50` is prematurely discarded before refinement).
     - Refine each with 50-iteration normalized LM (`refine_axis_normalized(X, modes[idx], delta=huber_delta, max_nfev=50, min_clearance_mm=min_clearance_mm)`).
     - Accept a refined candidate into the conical pool if:
       - `0.50 < _whole_sherd_axial_mean(X, vt) <= 0.925`,
       - `25.0 <= d_c <= 105.0` mm, and
       - `(cw <= 0.0095 and c < best_cyl_c)` OR `(s >= 500 and c <= 0.012)`.
   - Merge the accepted conical candidates and the cylindrical candidates (deduplicating within `dedup_deg` by keeping the candidate with lower average cost `c` when a conical candidate beats a cylindrical candidate), so that converged conical shoulder axes (`02, 04, 15, 17, 18, 20, 21`) take **Rank 0** while lower-wall cylindrical pieces (`03, 14, 23, 24, 25, 26, 27, 31`) retain their Ticket 314 cylindrical candidates untouched.
2. Add a unit test in `tests/test_normalized.py` verifying that a synthetic conical/sloped-shoulder sherd ($45^\circ$ wall slope, radius $55$ mm) retains its true rotation axis at Rank 0 without being deleted by a minor perpendicular noise cluster.
3. Verify on Spartan that `axes315` achieves **31/31 pieces of Pot E within $\le 10^\circ$ of GT/Released in top-3 ($K=3$)** and **all 7 sloped shoulder pieces (`02, 04, 15, 17, 18, 20, 21`) within $< 5^\circ$ at Rank 0 ($K=1$)**.

### Stage B: Lean Pot E C++ Assembly on Spartan ($K \in \{1, 2, 3\}$ ONLY)
1. Generate `axes315` on Spartan compute nodes (`srun` on existing allocation `34462441` if still active, or a short compute job).
2. Run the C++ assembler harness (`sfspreproc.sif` / `CountResult`) on **Pot E across $K \in \{1, 2, 3\}$, repeats R1 and R2 ONLY**.
   - **STRICT CONSTRAINT:** Do **NOT** run $K=6$!
3. Record Both:
   - The standard `CountResult` sherd and join counts (`E_K1`, `E_K2`, `E_K3`), and
   - The true connected-component assembly check (confirming whether `15, 17, 18, 20, 21, 23, 24, 31` join the main Pot E vessel component).

### Stage C: Lean Non-Regression Check ($K \le 3$ ONLY)
1. Check axis retention and lean assembly ($K \le 3$, **never $K=6$**) on the reference pots (`Pot A`, `Pot B`, `Pot G`, and optionally `Pot D` / `Pot I` at their winning $K \le 3$ arm only if fast) to verify zero regression.
2. Render before/after Pot E assembly views into `artifacts/pota315/renders/pote_kladder_assembly.png` and save score TSVs in `artifacts/pota315/`.
3. Verify byte-for-byte integrity of `original_samples/SfS_pp` (`0 diff`).
