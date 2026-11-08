# Ticket 318 — Research, simplify, and test scale-invariant generalizable axis extraction across all sample pots and Juglet

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-09)
**Branch:** 318-scale-invariant-generalizable-axis-extraction, in /c/PR/worktrees/sfs/318
**Answers:** E1
**Depends on:** 317
**Blocks:** none
**Worker:** sfs318
**Hold:** 318; E1; Pot_A..Pot_J + Juglet (`sfs_axes/potsac.py`)

## Context & 172-Piece Audit Findings (Lead Diagnosis)

Before running any full end-to-end sweep across all 10 sample pots and the Juglet, we audited `axes317` (`f929e2b`) across all **172 pieces** (all 163 pieces of Sample Pots `A–J` + all 9 pieces of the `Juglet`) on Spartan compute node `spartan-bm024` (job `34462441`):

| Pot | Pieces | `305` $K \le 3$ | `313` $K \le 3$ | `317` $K=1$ | `317` $K \le 3$ | `317` $K \le 6$ | True $d_c$ range (mm) | True $\text{mean}\|a \cdot n\|$ range |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A** | 8 | 7/8 | 6/8 | 6/8 | 6/8 | 6/8 | 7.8 .. 88.1 | 0.66 .. 0.96 |
| **B** | 9 | 5/9 | 5/9 | 5/9 | 6/9 | 6/9 | 3.7 .. 74.2 | 0.66 .. 0.88 |
| **C** | 6 | **6/6** | 4/6 | **1/6** | **2/6** | 3/6 | 4.8 .. 44.8 | 0.26 .. 0.95 |
| **D** | 32 | 22/32 | 23/32 | 18/32 | 24/32 | 26/32 | 1.2 .. 99.3 | 0.10 .. 0.98 |
| **E** | 34 | 21/34 | 23/34 | 22/34 | **32/34 (31/31 scored)** | 32/34 | 17.3 .. 80.8 | 0.09 .. 0.90 |
| **F** | 7 | 5/7 | 6/7 | 5/7 | **7/7** | 7/7 | 17.2 .. 44.8 | 0.36 .. 0.88 |
| **G** | 7 | 6/7 | 5/7 | **6/7** | **6/7** (`G_07` at $11.57^\circ$) | 6/7 | 21.1 .. 39.3 | 0.59 .. 0.73 |
| **H** | 11 | 8/11 | **10/11** | **4/11** | **4/11** | 4/11 | 20.9 .. 86.8 | **0.89 .. 0.99** |
| **I** | 30 | 20/30 | 22/30 | 17/30 | 23/30 | 24/30 | 4.5 .. 72.6 | 0.15 .. 0.96 |
| **J** | 19 | 10/19 | 10/19 | 7/19 | 9/19 | 10/19 | 4.7 .. 52.3 | 0.22 .. 0.94 |
| **JUG** | 9 | 3/9 | 0/9 | **2/9** | **2/9** | 2/9 | **0.8 .. 14.7** | 0.12 .. 0.57 |
| **Total** | **172** | **113/172** | **115/172** | **93/172** | **121/172** | **127/172** | **0.8 .. 99.3** | **0.09 .. 0.99** |

### Why `axes317` is not yet generalizable (3 structural failure modes)

Even though **172 of 172 pieces (`100%`)** contain a basin within $0.76^\circ$–$8.24^\circ$ of the reference axis in the 10-seed Pottmann MLESAC pool (`reps`), `axes317` fails on three vessel regimes because of constants tuned to Pot E ($R \approx 75$ mm) and Pot G ($R \approx 35$ mm):

1. **Failure Mode 1 — Shallow dishes / plates (`Pot H` drops from `10/11` in `313` to `4/11` in `317`, plus `D_28` and `C_06`):**
   - Pot H is a wide shallow dish whose walls slope $65^\circ$–$82^\circ$ from vertical, so $\text{mean}|a_{\text{GT}} \cdot n| \in [0.89, 0.99]$.
   - In `axes317`, `potsac.py:530` (`mean_ax <= 0.90`) and `potsac.py:544` (`mean_ax_ref <= 0.925` and `d_ref <= 105.0` mm) hard-rejected the true axis on 6 of 11 pieces of Pot H (`H_01, H_02, H_03, H_04, H_08, H_10`), even though 50-step normalized LM refines them to $0.19^\circ$–$3.45^\circ$ with tiny worst-wall Huber cost ($c_w \in [0.0026, 0.0091]$ at $d_{\text{ref}} \in [37.6, 107.1]$ mm) or overwhelming MLESAC consensus (`H_04` has $\text{sz} = 8,992 / 10,000$ draws; `D_28` has $\text{sz} = 7,771 / 10,000$ draws).
   - **Why perpendicular wall-slicing decoys on vertical sherds (`Pot E` lower wall) are different:** On a vertical wall sherd (`Pot E_23, E_27, E_31`), a perpendicular skewer decoy with $\text{mean}|a \cdot n| > 0.925$ slices *through* the sherd ($d_{\text{ref}} = 5.6$–$18.2 < 25$ mm) and has high worst-wall residual ($c_w > 0.0095$). It never sits at $d_{\text{ref}} \ge 35$ mm with $c_w \le 0.0092$, and never reaches $\text{sz} \ge 6,000$.

2. **Failure Mode 2 — Large high-curvature cylindrical sherds (`Pot C` drops from `6/6` in `305` and `4/6` in `313` to `2/6` in `317`):**
   - On `Pot_C_Piece_01` (`diag = 180.8` mm, $n = 62,679$, true $d_c = 38.9$ mm) and `Pot_C_Piece_02` (`diag = 179.5` mm, $n = 55,503$, true $d_c = 36.2$ mm), 15 distinct MLESAC basins converge under 20-step normalized LM onto the exact same stationary point ($0.34^\circ$–$0.99^\circ$ on `C_01` at $d_{\text{ref}} = 36.8$ mm, $c = 0.00449$; $0.92^\circ$ on `C_02` at $d_{\text{ref}} = 39.0$ mm, $c = 0.00562$).
   - However, `potsac.py:512`'s `drift <= 8.0°` guard rejected the converged $<1^\circ$ solutions and reverted `cand` back to unconverged $15^\circ$–$24^\circ$ MLESAC draws (`dc = 40.3` mm), and `r_prior(d < 40.0)` then penalized the true $36.8$–$39.0$ mm radius by $+0.010$ to $+0.032$ ($2\times$–$7\times$ the Huber residual!).
   - On large sherds (`diag >= 140.0` mm), the sherd's chord spans $>120^\circ$ of azimuth so curvature locks the radius without lever-arm collapse: allowing `drift <= 25.0°` and setting the `r_prior` inner knee to $30.0$ mm when `c <= 0.0058` restores `C_01` ($0.61^\circ$) and `C_02` ($0.92^\circ$) to Rank 0 ($K=1$).

3. **Failure Mode 3 — Miniature vessels and tight-radius fragments (`Juglet` at `2/9`, plus `C_06, D_31, D_32, E_32, I_29, J_19`):**
   - All 9 pieces of the `Juglet` have a true centroid-to-axis radius of **$0.8$ to $14.7$ mm** (`diag = 23.1..62.7` mm).
   - `DEFAULT_CLEARANCE_MM = 25.0` mm bans every candidate within $25$ mm of the centroid, and `refine_axis_normalized` ($\hat{e}_i = e_i / r_i$) creates a repulsive $1/r$ singularity when $r_i \approx 3$–$14$ mm that pushes the axis outward to $35$–$70$ mm.
   - **Self-calibrating Pottmann scale detector:** Because the 6-point Pottmann solver (`compute_pottmann_axis`) is scale-invariant, the MLESAC support-weighted centroid distance $w_{dc} = \frac{\sum_j d_{c, j} \cdot \text{sz}_j}{\sum_j \text{sz}_j}$ and minimum unnormalized worst-wall Cao Huber cost $\text{min\_hcw} = \min_{\text{sz}_j \ge 20} \text{hcw}_j$ blindly identify tight-radius / miniature fragments: the condition `w_dc <= 15.5 and min_hcw <= 38.0 and diag <= 65.0` selects **all 9/9 Juglet pieces** plus tight-radius pieces `C_06, D_31, D_32, E_32, I_29, J_15, J_19` and **0/31 scored Pot E pieces** (and 0 pieces of Pots A, B, G, H).

---

## Scope & Stages

> **Constraint:** Do **NOT** run a full 10-pot assembly sweep in this ticket (per user instruction: *"future don't do full sweep unless i told you to"*). Run the fast 172-piece axis benchmark (Stage A) and targeted $K=3$ assembly verification only on the previously failing regimes (**Pot H**, **Pot C**, and **Juglet**, plus **Pot G** if `G_07` changes) in Stage B.

### Stage A — Simplify & Generalize `sfs_axes/potsac.py` and Verify on the 172-Piece Benchmark

1. Update `run_potsac_union` in `sfs_axes/potsac.py` to incorporate the three self-calibrating regime rules:
   - **Regime 1 — Self-Calibrating Tight-Radius / Miniature Regime (`w_dc <= 15.5` mm, `min_hcw <= 38.0`, `diag <= 65.0` mm):**
     - Compute `diag` (bounding-box diagonal of `C[:3]`), `w_dc` (size-weighted mean `centroid_distance` across all clustered MLESAC basins `reps`), and `min_hcw` (minimum `_worst_surface_cost(reps[:, j], C0, S1)` across basins with `sizes[j] >= 20`).
     - When `w_dc <= 15.5 and min_hcw <= 38.0 and diag <= 65.0`:
       - Filter candidate basins to `sizes[j] >= 20 and (mean_ax <= 0.70 or sizes[j] >= 1500)` (eliminating low-support perpendicular skewers while preserving true axial caps like `C_06`).
       - Score each basin by `(hcw * (c ** 0.5)) / (sizes[j] ** 0.45)` where `c = 0.5 * (normalized_huber_cost(cand, C0) + normalized_huber_cost(cand, S1))`.
       - For the top 8 basins, if `orig_dc >= 16.0 or sizes[j] >= 1500`, also run 20-iter `refine_axis_normalized` (`v_ref`) and place `v_ref` ahead of `orig_cand` if `d_ref <= 22.0 and ref_cost <= orig_cost`.
       - Dedup at `10.0°` (`DEDUP_COS`) in this tight-radius regime so adjacent MLESAC basins on miniature vessels (e.g. `Juglet_Piece_4` at $3.22^\circ$ vs $12.81^\circ$) are not merged by a $15^\circ$ cut.
   - **Regime 2 — Large High-Curvature Sherd Relaxation (`diag >= 140.0` mm):**
     - In `r_prior(d, c_val)`: set the inner knee to `30.0` mm when `diag >= 140.0 and c_val <= 0.0058` (otherwise `40.0` mm).
     - In Track 1 (`cyl_scored`): set `max_drift = 25.0` deg when `diag >= 140.0` (otherwise `8.0` deg).
   - **Regime 3 — Unified Conical / Shallow-Dish / High-Consensus Base Track (`cone_scored`):**
     - In `cone_pre`: admit basins where `base or sizes[j] >= 6000 or (DEFAULT_CLEARANCE_MM <= d_c <= MAX_CLEARANCE_MM and (mean_ax <= 0.60 or (sizes[j] >= 50 and mean_ax <= 0.985)))`.
     - After 50-step `refine_axis_normalized`, admit `v_ref` when any of the following hold:
       1. `base` (if `orig_base and sizes[j] >= 1000 and drift > 4.0`, keep `orig_cand` so `Pot_G_Piece_07` stays at $7.96^\circ$ instead of drifting to $10.49^\circ$),
       2. `valid_cone`: `DEFAULT_CLEARANCE_MM <= d_ref <= 110.0 and 0.50 < mean_ax_ref <= 0.925 and cw_ref <= 0.0095`,
       3. `valid_dish`: `35.0 <= d_ref <= 115.0 and 0.925 < mean_ax_ref <= 0.985 and cw_ref <= 0.0092 and sizes[j] >= 50`,
       4. `valid_flat`: `sizes[j] >= 6000 and cw_ref <= 0.014`.
     - When `valid_dish`, `valid_flat`, or `base` holds, waive `r_prior` (`r_p = 0.0`) so shallow-dish and base axes are ranked purely by `(c_ref + 0.002 * mean_ax_ref) / (sz ** 0.12)`.
2. Run unit tests (`pytest`) and run the 172-piece benchmark across all 163 pieces of Pots `A–J` + all 9 pieces of `Juglet` on a Spartan compute node. Record the full per-pot table (`K=1`, `K<=3`, `K<=6`) comparing `305`, `313`, `317`, and `318`.
3. Verify zero regression on **Pot E** (`31/31` scored pieces within $\le 10^\circ$ at $K \le 3$; check exact top-3 line diff against `axes317` on `Pot_E_Piece_01..31` and `Pot_A_Piece_01..08`) and verify that **Pot G** reaches **7/7 (100%) within $\le 10^\circ$ at $K=1$** (`G_07` improving from $11.57^\circ$ to $7.96^\circ$).

### Stage B — Targeted End-to-End Assembly Tests on Spartan (`Pot H`, `Pot C`, `Juglet`, and `Pot G`)

1. Extract `axes318` on Spartan for **Pot H** (11 pieces), **Pot C** (6 pieces), **Pot G** (7 pieces), and **Juglet** (9 pieces, from `outU_jug/geom`).
2. Submit targeted $K=3$ (`--max-candidates 3`, 2 internal repeats `R1, R2`) assembly jobs on Spartan:
   - **Pot H** (`11` pieces): compare `axes318` ($K=3$) against `axes317` ($K=3$) and `MO` (released axes).
   - **Pot C** (`6` pieces): compare `axes318` ($K=3$) against `axes317` ($K=3$) and `MO` (note corpus caveats in `SfSpp_preprocessing/AGENTS.md`: `Pot C 01` interior edgeline and `Pot C 03 Bl1`).
   - **Pot G** (`7` pieces): verify `7/7` sherds and `10/10` joins hold at $K=3$ with `G_07` improved to $7.96^\circ$.
   - **Juglet** (`9` pieces, `outU_jug`): compare `axes318` ($K=3$) against `axes305_jug` / released `Dataset` axes.
3. Render before/after assembly comparison PNGs under `artifacts/pota318/renders/` for the tested vessels.
4. Record all Slurm job IDs, `sacct` `State/ExitCode`, `runs/index.tsv` rows, and verification lines in the `## Write-back` section below, commit on branch `ticket/318`, and report back without concluding.

## Acceptance Criteria

- [ ] `sfs_axes/potsac.py` implements the self-calibrating tight-radius regime, large-sherd drift/knee relaxation, and shallow-dish/high-consensus base admission cleanly.
- [ ] 172-piece benchmark table (`A–J` + `Juglet`) recorded:
  - Pot E: `31/31` scored pieces within $\le 10^\circ$ at $K \le 3$ (top-3 lines on `Pot_E_Piece_01..30` verified identical to `axes317`).
  - Pot G: `7/7` pieces within $\le 10^\circ$ at $K=1$ (`G_07` $\le 8.0^\circ$).
  - Pot C: $\ge 5/6$ within $\le 10^\circ$ at $K \le 3$ ($\ge 4/6$ at $K=1$).
  - Pot H: $\ge 10/11$ within $\le 10^\circ$ at $K=1$ and $K \le 3$.
  - Juglet: $\ge 6/9$ within $\le 10^\circ$ at $K \le 3$.
- [ ] Targeted $K=3$ assembly runs completed on Spartan for Pot H, Pot C, Pot G, and Juglet, with before/after renders in `artifacts/pota318/renders/`.

## Write-back

*(Worker `sfs318` writes implementation, benchmark table, Slurm job IDs, `sacct` states, and render paths here.)*
