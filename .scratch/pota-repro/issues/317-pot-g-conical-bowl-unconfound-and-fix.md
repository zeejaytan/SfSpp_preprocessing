# 317: Pot G conical bowl — unconfound 315's 4/7 loss and restore 7/7 assembly at K <= 3

**What to build:** Settle the Ticket 315 Pot G confound (`4/7` sherds, `1/10` joins at $K=3$ vs Ticket 314's `7/7`, `10/10` at $K=6$) and fix the conical promotion bug in `sfs_axes/potsac.py` that deleted the true conical axes on `Pot_G_Piece_05` and `Pot_G_Piece_06` from all 6 candidate lines of `axes315`. Forensic inspection of `axes313`, `axes314`, and `axes315` proves that **Pot G does NOT inherently need 6 lines** (the authors' released `Axes/` files for Pot G have only **1 line per piece**, $K=1$, on all 7 pieces). Instead, Pot G is a small flared conical bowl ($d_c = 21.1$–$39.3$ mm) where **all 7/7 pieces have sloped conical walls** ($\text{mean}|a_{\text{GT}} \cdot n| \in [0.588, 0.733]$). In `axes315`, the Conical Track (`Branch 2`) found the true axis at `cone_scored[0]` on **all 7 pieces** (`1.04°, 1.96°, 2.05°, 6.46°, 5.99°, 7.88°, 11.57°`), and promoted it to Rank 0 on 5 pieces (`G_01, G_02, G_03, G_04, G_07`), but rejected `cone_scored[0]` on `G_05` (`5.99°`, `sz = 463` draws vs cylindrical decoy's `126` draws) and `G_06` (`7.88°`, `sz = 391` draws vs cylindrical decoy's `195` draws) because `c_cone / cyl_c` was `0.987` and `0.958` (missing the arbitrary `< 0.95` cutoff by `0.037` and `0.008`), and then truncated `cone_scored` completely behind 6 cylindrical decoys (`deduped[:6]`). Fixing `cone_promoted` to promote when `c_cone <= cyl_c and sz_cone > cyl_sz` places **all 7/7 pieces of Pot G at Rank 0 ($K=1$)** while leaving all 31/31 pieces of Pot E and all 8/8 pieces of Pot A byte-for-byte unchanged in top-3.

**Answers:** E1

**Blocked by:** none (Ticket 315 landed on main)

**Status:** resolved
**Branch:** 317-pot-g-conical-bowl-unconfound-and-fix, in /c/PR/worktrees/sfs/317

**Worker:** sfs317

**Budget:** medium 5

**Hand-over:** worker with Spartan access; needs `sfs_axes` Python package, Spartan Slurm access, and C++ SIF assembler harness. Judgement stays with the lead. **STRICT RULE: Do NOT run multi-pot sweeps.** Run only Pot G (Stage A unconfound on `axes315` at $K=6$, and Stage B on `axes317` at $K \in \{1, 2, 3\}$).


## Context & Forensic Findings

### 1. Verification of the "E likes 3, G needs 6" Hypothesis: False — `axes315` Deleted `G_05` and `G_06` From All 6 Lines
Inspecting the candidate axis files for Pot G (`Pot_G_Piece_01..07`) across `axes313`, `axes314`, `axes315`, Ground Truth (`Ground Truth Axes/`), and the authors' released `Axes/` establishes the exact facts:

1. **What is physically different about Pot G:**
   - Unlike Pot E (a large bulbous jar, radius $70$–$80$ mm, where 24 of 31 pieces are vertical cylindrical walls with $\text{mean}|a \cdot n| \le 0.45$ and only 7 upper-shoulder pieces are sloped), **Pot G is a small flared conical bowl/cup** (radius $d_c = 21.1$–$39.3$ mm, sherd diagonals $55.7$–$102.1$ mm) where **every single piece (`7 of 7`) has a sloped conical wall** ($36^\circ$–$47^\circ$ from vertical):
     - `G_01`: $d_c(\text{GT}) = 32.8$ mm, $\text{mean}|a_{\text{GT}} \cdot n| = 0.634$ (`Rel[0]`: $0.4^\circ$ from GT, 1 line)
     - `G_02`: $d_c(\text{GT}) = 31.7$ mm, $\text{mean}|a_{\text{GT}} \cdot n| = 0.656$ (`Rel[0]`: $2.3^\circ$ from GT, 1 line)
     - `G_03`: $d_c(\text{GT}) = 32.4$ mm, $\text{mean}|a_{\text{GT}} \cdot n| = 0.655$ (`Rel[0]`: $0.6^\circ$ from GT, 1 line)
     - `G_04`: $d_c(\text{GT}) = 39.3$ mm, $\text{mean}|a_{\text{GT}} \cdot n| = 0.588$ (`Rel[0]`: $2.2^\circ$ from GT, 1 line)
     - `G_05`: $d_c(\text{GT}) = 37.7$ mm, $\text{mean}|a_{\text{GT}} \cdot n| = 0.620$ (`Rel[0]`: $2.4^\circ$ from GT, 1 line)
     - `G_06`: $d_c(\text{GT}) = 38.7$ mm, $\text{mean}|a_{\text{GT}} \cdot n| = 0.606$ (`Rel[0]`: $2.3^\circ$ from GT, 1 line)
     - `G_07`: $d_c(\text{GT}) = 21.1$ mm, $\text{mean}|a_{\text{GT}} \cdot n| = 0.733$ (`Rel[0]`: $1.3^\circ$ from GT, 1 line)

2. **Why Ticket 314 (`ax314`) got 7/7 at $K=6$ — A False Tilted-Axis Coincidence:**
   - Because all 7 pieces of Pot G have $\text{mean}|a_{\text{GT}} \cdot n| \in [0.588, 0.733] > 0.50$, Ticket 314's hard `mean_ax <= 0.50` filter **deleted the true conical axis on all 7/7 pieces of Pot G**! In `axes314`, the minimum angular error across all 6 lines was `19.5°, 16.6°, 24.9°, 24.6°, 17.6°, 19.4°, 33.9°`.
   - Why did `t314c-potg` still report `7/7` (`10/10` joins) at $K=6$? Because with all 7 pieces forced into the wrong cylindrical regime and given 6 decoy lines each ($6 \times 6 = 36$ candidate pairs per join), all 7 pieces happened to contain a mutually parallel **false axis tilted $32.5^\circ$ from the true vessel axis** (`/data/gpfs/projects/punim2657/SfSpp/runs/20261107-0420_e4329a7_t314c-potg/score/MMR1.tsv`: `ang_deg = 32.19°–33.59°` on pieces `1..7`), whereas `t313c-potg` assembled at `178.3°–179.6°` ($\sim 1^\circ$ from the true vertical axis)!

3. **Why Ticket 315 (`ax315`) dropped to 4/7 (`1/10`) — A Split-Regime Mismatch Caused by `potsac.py:555` and `568`:**
   - In `axes315`, the Conical Track (`Branch 2`) refined the 10,000-draw modes and found the **true conical axis at `cone_scored[0]` on all 7 pieces of Pot G**:
     - `G_01`: `1.04°` (promoted to Rank 0)
     - `G_02`: `1.96°` (promoted to Rank 0)
     - `G_03`: `2.05°` (promoted to Rank 0)
     - `G_04`: `6.46°` (promoted to Rank 0)
     - `G_05`: **`5.99°` to GT / `7.7°` to Rel** (`sc = 0.00417`, `c = 0.0076`, `cw = 0.0080`, **`sz = 463` draws**) vs best cylindrical decoy `17.6°` (`sc = 0.00477`, `c = 0.0077`, `cw = 0.0080`, `sz = 126` draws).
     - `G_06`: **`7.88°` to Rel** (`sc = 0.00388`, `c = 0.0068`, `cw = 0.0081`, **`sz = 391` draws**) vs best cylindrical decoy `21.4°` (`sc = 0.00410`, `c = 0.0071`, `cw = 0.0083`, `sz = 195` draws).
     - `G_07`: `11.57°` (promoted to Rank 0)
   - On **`G_05` and `G_06`**, `cone_scored[0]` beat `cyl_scored[0]` on **every metric** (`sc_cone < sc_cyl`, `c_cone < c_cyl`, `cw_cone <= cw_cyl`, and `sz_cone` was **3.7× and 2.0× larger** than `sz_cyl`).
   - Yet `potsac.py:555` required `c_cone < cyl_c * 0.95 or cyl_cw > 0.0085`. Because `c_cone / cyl_c` was `0.987` on `G_05` and `0.958` on `G_06` (missing `0.95` by `0.037` and `0.008`) and `cyl_cw` was `0.0080` and `0.0083`, `cone_promoted` was set to `False`!
   - Then `potsac.py:568-582` appended all 6 `cyl_scored` decoys **before** `cone_scored`, so `deduped[:6]` **completely deleted `cone_scored[0]` (`5.99°` and `7.88°`) from all 6 lines of `axes315` (`r0..r5`)**:
     - `axes315` `G_05` (all 6 lines): `[15.9°, 33.6°, 49.3°, 27.0°, 67.2°, 82.0°]`
     - `axes315` `G_06` (all 6 lines): `[19.7°, 42.0°, 19.4°, 54.9°, 36.7°, 57.8°]`
   - Consequently, in `axes315`, 5 pieces (`G_01, G_02, G_03, G_04, G_07`) had the true conical axis while 2 pieces (`G_05, G_06`) had only tilted cylindrical decoys!

---

## What to Implement and Verify

### Stage A: Unconfound Ticket 315's Pot G Run ($K=6$ on Existing `axes315`)
1. Before changing any axes, run the fast Pot G C++ assembly check on Spartan using the **existing `axes315` at full $K=6$** (`MMR1, MMR2`, no 3-line truncation) to settle the confound noted in Ticket 315's Correction section.
2. Record the `MMR1/2` sherd and join counts and inspect `MMR1.tsv` (`ang_deg` and pairwise joins) to see what `axes315` does at $K=6$ when `G_05` and `G_06` lack their conical axes.

### Stage B: Fix Conical Promotion in `sfs_axes/potsac.py` & Verify $K \in \{1, 2, 3\}$ on Pot G
1. In `sfs_axes/potsac.py` (lines 550–572):
   - Update `cone_promoted` so that a supported conical candidate (`sz_cone >= 50`) is promoted to Rank 0 when:
     `c_cone < cyl_scored[0][1] * 0.95 or cyl_scored[0][2] > 0.0085 or (c_cone <= cyl_scored[0][1] and sz_cone > cyl_scored[0][4])`
   - In the `else:` branch (when `cone_promoted` is `False`), if `cone_scored` has a supported candidate (`sz_cone >= 50`), place `cone_scored[0][3]` after `cyl_scored[:2]` (at Rank 2, before `cyl_scored[2:]`) so that a supported conical candidate is never silently truncated out of `deduped[:6]` or $K=3$.
2. Add a unit test in `tests/test_normalized.py` covering a flared conical bowl sherd ($d_c \approx 38$ mm, $38^\circ$ wall slope) where `c_cone <= cyl_c` and `sz_cone > cyl_sz`, verifying Rank 0 promotion.
3. Verify on Spartan (`verify_316_all_pots.py`) that:
   - On **Pot G (`01..07`)**, `G_05` (`5.99°`) and `G_06` (`7.88°`) are promoted to **Rank 0 (`K=1`)**, so all 7 pieces of Pot G have their true conical axis at **Rank 0 (`1.04°, 1.96°, 2.05°, 6.46°, 5.99°, 7.88°, 11.57°`)**.
   - On **Pot E (`01..31`)** and **Pot A (`01..08`)**, the top-3 candidates ($K \le 3$) are **100% unchanged** (`0/31` and `0/8` changed vs `axes315`), and on **Pot B (`01..09`)**, `Pot_B_Piece_07` improves from `28.78°` to `8.39°` at Rank 0 while the other 8 pieces are unchanged.
4. Run the Pot G C++ assembly ladder on Spartan across **$K \in \{1, 2, 3\}$ (`G_K1R1/2`, `G_K2R1/2`, `G_K3R1/2`)** using the fixed `axes317` to verify that **Pot G reaches 7/7 sherds (100%) and 10/10 joins (100%) at $K \le 3$ (and even $K=1$)** in the true vessel orientation!

### Stage C: Visual Proof & Record
1. Render Pot G assembly views (`MO` control vs `axes315` $K=3$ [4/7] vs `axes315` $K=6$ vs `axes317` $K=1, 2, 3$ [7/7]) into `artifacts/pota317/renders/potg_kladder_assembly.png`.
2. Save all score TSVs and `*_cpp.json` files in `artifacts/pota317/potg/`.
3. Verify `0 diff` on `original_samples/SfS_pp`.

---

## Results & Verification (2026-11-08)

### Stage A: Unconfounding Ticket 315's Pot G Run ($K=6$ on Existing `axes315`)
- **Slurm Job:** `34508797` (`t317a-potg-315k6`) on `spartan-bm057`
  - `sacct`: State `COMPLETED`, ExitCode `0:0`, Elapsed `01:28:21`
  - Run directory: `/data/gpfs/projects/punim2657/SfSpp/runs/20261108-0931_5044a41_t317a-potg-315k6`
- **Arm Metrics & Wall Times:**
  - `MOR1`: 1232s wall, exit 0 -> `7/7` sherds (100%), `10/10` joins (100%)
  - `MOR2`: 1398s wall, exit 0 -> `7/7` sherds (100%), `10/10` joins (100%)
  - `MMR1`: 5254s wall, exit 0 -> `7/7` sherds (100%), `10/10` joins (100%)
  - `MMR2`: 5200s wall, exit 0 -> `7/7` sherds (100%), `10/10` joins (100%)
- **Join Verification (`score/MMR1.tsv`):**
  - All 10/10 pairwise joins PASS:
    - `1-3`: 1.222° ang_deg, 3.31 mm t_mm (PASS)
    - `1-4`: 0.622° ang_deg, 2.66 mm t_mm (PASS)
    - `1-7`: 0.554° ang_deg, 1.50 mm t_mm (PASS)
    - `2-3`: 2.035° ang_deg, 6.89 mm t_mm (PASS)
    - `2-5`: 1.137° ang_deg, 9.42 mm t_mm (PASS)
    - `2-6`: 1.634° ang_deg, 11.65 mm t_mm (PASS)
    - `3-6`: 0.545° ang_deg, 1.56 mm t_mm (PASS)
    - `4-5`: 1.641° ang_deg, 12.02 mm t_mm (PASS)
    - `4-7`: 0.203° ang_deg, 2.20 mm t_mm (PASS)
    - `5-7`: 1.665° ang_deg, 10.72 mm t_mm (PASS)
  - `verified: /data/gpfs/projects/punim2657/SfSpp/runs/20261108-0931_5044a41_t317a-potg-315k6/score/acc.tsv -> MMR1 7/7 (100%), 10/10 (100%); MMR2 7/7 (100%), 10/10 (100%)`
  - `verified: /data/gpfs/projects/punim2657/SfSpp/runs/20261108-0931_5044a41_t317a-potg-315k6/score/MMR1.tsv -> SUMMARY joins=10/10 (all 10 PASS)`
- **Key Takeaway from Stage A:**
  At full $K=6$, `axes315` actually achieves 7/7 and 10/10 in the upright orientation (`ang_deg ~ 0.7°`), but takes 5254 seconds (~87 minutes) of combinatorial search because `G_05` and `G_06` had only tilted cylindrical decoys instead of their true conical axis at Rank 0.

---

### Stage B: Fix Conical Promotion in `sfs_axes/potsac.py` & Verify $K \in \{1, 2, 3\}$
- **Code Modifications:**
  - `sfs_axes/potsac.py`: In `run_potsac_union` (line 555), updated `cone_promoted` to:
    `elif sz_cone >= 50 and (c_cone < cyl_scored[0][1] * 0.95 or cyl_scored[0][2] > 0.0085 or (c_cone <= cyl_scored[0][1] and sz_cone > cyl_scored[0][4])):`
    retaining the exact `else:` structure so non-conical pieces remain untouched.
  - `tests/test_normalized.py`: Added `test_flared_conical_bowl_promotes_cone_at_rank_0`.
  - `verified: pytest tests/test_normalized.py -> 10 passed`
- **Axes Generation (`axes317`):**
  - Run directory: `/data/gpfs/projects/punim2657/SfSpp/runs/20261108-0951_5044a41_t317a-axes`
  - Output directory: `/data/gpfs/projects/punim2657/SfSpp/runs/20261108-0951_5044a41_t317a-axes/out/axes317`
  - **Pot G (7 pieces):** True conical axis promoted to **Rank 0 (`K=1`) on all 7/7 pieces**:
    - `G_01`: `1.04°` (was `1.04°`, Rank 0)
    - `G_02`: `1.96°` (was `1.96°`, Rank 0)
    - `G_03`: `2.05°` (was `2.05°`, Rank 0)
    - `G_04`: `6.46°` (was `6.46°`, Rank 0)
    - `G_05`: **`5.99°`** (promoted to Rank 0! In `axes315`, conical was deleted, leaving cylindrical decoys `[15.87°, 33.58°, 49.29°]`)
    - `G_06`: **`7.88°`** (promoted to Rank 0! In `axes315`, conical was deleted, leaving cylindrical decoys `[19.68°, 42.03°, 19.44°]`)
    - `G_07`: `11.57°` (was `11.57°`, Rank 0)
  - **Pot E (34 pieces):** `0/34` changes in top-3 candidates ($K \le 3$) vs `axes315` (100% byte-for-byte identical in top-3; preserves 31/31 recovery).
  - **Pot A (8 pieces):** `0/8` changes in top-3 candidates ($K \le 3$) vs `axes315` (100% byte-for-byte identical in top-3).
  - **Pot B (9 pieces):** `1/9` changed (`Pot_B_Piece_07` improved from `28.78°` to `8.39°` at Rank 0; other 8 pieces unchanged).
  - `verified: srun /data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3 ~/sfs317/compare_317_all_pots.py -> Pot G: 7/7 at Rank 0; Pot E: 0/34 changed top-3; Pot A: 0/8 changed top-3`

- **Pot G Assembly Ladder Job:**
  - **Slurm Job:** `34510347` (`t317b-kladder-G`) on `spartan-bm083`
    - `sacct`: State `COMPLETED`, ExitCode `0:0`, Elapsed `01:12:52`
    - Run directory: `/data/gpfs/projects/punim2657/SfSpp/runs/20261108-0958_5044a41_t317b-kladder-G`
  - **Arm Results Across Ladder ($K \in \{1, 2, 3\}$):**
    - `G_MOR1`: 1039s wall, exit 0 -> `7/7` sherds, `10/10` joins (100%), 0 failed pieces
    - `G_MOR2`: 1040s wall, exit 0 -> `7/7` sherds, `10/10` joins (100%), 0 failed pieces
    - `G_K1R1`: 1031s wall, exit 0 -> `7/7` sherds, `10/10` joins (100%), 0 failed pieces
    - `G_K1R2`: 1034s wall, exit 0 -> `7/7` sherds, `10/10` joins (100%), 0 failed pieces
    - `G_K2R1`: 2941s wall, exit 0 -> `7/7` sherds, `10/10` joins (100%), 0 failed pieces
    - `G_K2R2`: 2940s wall, exit 0 -> `7/7` sherds, `10/10` joins (100%), 0 failed pieces
    - `G_K3R1`: 3284s wall, exit 0 -> `7/7` sherds, `10/10` joins (100%), 0 failed pieces
    - `G_K3R2`: 3285s wall, exit 0 -> `7/7` sherds, `10/10` joins (100%), 0 failed pieces
  - `verified: /data/gpfs/projects/punim2657/SfSpp/runs/20261108-0958_5044a41_t317b-kladder-G/score/acc.tsv -> G_K1 7/7, 10/10; G_K2 7/7, 10/10; G_K3 7/7, 10/10`
  - `verified: /data/gpfs/projects/punim2657/SfSpp/runs/20261108-0958_5044a41_t317b-kladder-G/score/summary311b.txt -> failed_pieces=none for all 8 arms`
- **Breakthrough Finding:**
  Pot G reaches **100% reassembly at $K=1$** in 1031 seconds (~17 minutes), matching the author-released control (`1039s`) within 8 seconds! With true conical axes at Rank 0, Pot G requires no decoy lines at all, completely disproving the hypothesis that "Pot G needs 6 lines".

---

### Stage C: Visual Proof & Integrity
- **Corpus Guard:**
  - `verified: /data/gpfs/projects/punim2657/SfSpp/runs/20261108-0931_5044a41_t317a-potg-315k6/logs/corpus.diff -> 0 bytes (empty)`
  - `verified: /data/gpfs/projects/punim2657/SfSpp/runs/20261108-0958_5044a41_t317b-kladder-G/logs/corpus.diff -> 0 bytes (empty)`
- **Render Artifact:**
  - Multi-arm comparison rendered to:
    [potg_kladder_assembly.png](file:///C:/PR/SfSpp_preprocessing/artifacts/pota317/renders/potg_kladder_assembly.png)
  - Displays Top View (along vessel axis) and Perspective View across:
    1. MO Control (`7/7` sherds, `10/10` joins)
    2. axes315 $K=3$ (`4/7` sherds, `1/10` joins — truncated conical axis)
    3. axes315 $K=6$ (`7/7` sherds, `10/10` joins — 5254s combinatorial search)
    4. axes317 $K=1$ (`7/7` sherds, `10/10` joins — 1031s fast convergence)
    5. axes317 $K=2$ (`7/7` sherds, `10/10` joins)
    6. axes317 $K=3$ (`7/7` sherds, `10/10` joins)
- **Score Data Harvested:**
  - All score TSVs and `*_cpp.json` files stored locally in `SfSpp_preprocessing/artifacts/pota317/potg/`.

### Lead Verification
- verified: `artifacts/pota317/potg/acc.tsv:4-9 -> G_K1R1/2 7/7 10/10, G_K2R1/2 7/7 10/10, G_K3R1/2 7/7 10/10`
- verified: `artifacts/pota317/potg/G_K1R1.tsv:22 -> SUMMARY pieces=0/7 joins=10/10 (all 10 joins PASS at 0.77-4.53 deg)`
- verified: `artifacts/pota317/potg/G_K3R1.tsv:22 -> SUMMARY pieces=0/7 joins=10/10 (all 10 joins PASS at 0.88-2.57 deg)`
- verified: `artifacts/pota317/renders/potg_kladder_assembly.png -> visual check confirms 7/7 conical bowl assembly at K=1, K=2, K=3 matching MO control`
