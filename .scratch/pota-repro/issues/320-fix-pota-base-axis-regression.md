# Ticket 320 — Restore Pot A base sherd (`Pot_A_Piece_01`) axis extraction without regressing Pots B–J or Juglet

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-09)
**Branch:** 320-fix-pota-base-axis-regression, in /c/PR/worktrees/sfs/320
**Answers:** E1
**Depends on:** 319
**Blocks:** none
**Worker:** sfs320

## Context & Root-Cause Diagnosis (Lead Investigation)

In Ticket 319 (`20261109-1426_ecd5bb8_t319-potA`), **Pot A** collapsed from **8/8 sherds, 15/15 joins** (achieved in Ticket 315 `20261108-0608_c1fed82_t315c-pota-mm` and Ticket 310) down to **3/8 sherds, 3/15 joins** at $K=3$, while all other sample pots (`B, C, D, E, F, G, H, I, J`) and `Juglet` held or improved.

### Exact Root Cause of Pot A's Collapse

1. **7 of 8 pieces of Pot A (`Pot_A_Piece_02..08`) are 100% byte-for-byte identical** between `axes315`/`axes317` (`8/8` sherds, `15/15` joins) and `axes318` (`3/8` sherds, `3/15` joins).
2. **The entire collapse is caused by a single piece: `Pot_A_Piece_01` (the large flat base disk of Pot A, connected to 5 neighbours in the ground-truth graph and used as the gauge piece in the assembler):**
   - In `axes315` and `axes317`, `Pot_A_Piece_01`'s Rank-0 axis was:
     `-55.455363869919353 -133.7139020330311 62.247189744445812 0.22644329153861517 0.33231351857945707 0.91558241632662363`
     which is **$0.10^\circ$ from the authors' released axis** (`Axes/Pot_A_Piece_01_Axis.xyz`), supported by **8,204 of 10,000 MLESAC draws (82.0%)** across two converging basins (`j=2` with `sz=5076`, `dc=8.38` mm, `cw=0.00204` and `j=0` with `sz=3128`, `dc=8.38` mm, `cw=0.00204`).
   - In `axes318` (`ecd5bb8`), **all 6 emitted lines on `Pot_A_Piece_01` lost the true base axis completely** — Rank 0 became a **$65.2^\circ$ decoy** (`0.484347 -0.699554 0.525387`), and all 6 lines sit $64.9^\circ$–$88.5^\circ$ away from the true axis.
3. **Why `axes318` (`sfs_axes/potsac.py:524, 573, 585-586`) deleted `Pot_A_Piece_01`'s true base axis:**
   - In Ticket 318 (`ecd5bb8`), to prevent perpendicular wall-piercing decoys on vertical cylindrical wall sherds (`Pot_E_Piece_24, 26`, where a skewer piercing the wall at `d_c = 6..14` mm with `mean_ax = 0.95..0.97` and `cw = 0.0078..0.0096` falsely triggers `is_base_fragment`) from getting `r_prior` waived (`r_p = 0.0`), `sfs318` added an unspec'd veto at `sfs_axes/potsac.py:573, 585-586`:
     ```python
     not (diag > 65.0 and mean_ax > 0.925 and sz < 6000)
     ```
   - On `Pot_A_Piece_01` (a large flat base disk with `diag = 170.2 > 65.0` mm, `mean_ax = 0.957 > 0.925`, `dc = 8.38` mm, `cw = 0.00204`, and largest single pre-LM basin `sz = 5076 < 6000`), that veto evaluated to `False` and threw away `Pot_A_Piece_01`'s true base axis in both `cone_pre` and `cone_scored`!
   - Additionally, at `sfs_axes/potsac.py:524`, `max_drift = 25.0 if diag >= 140.0 else 8.0` fired on `Pot_A_Piece_01` (`diag = 170.2` mm, even though `Pot_A_Piece_01` is a flat base with support-weighted `w_ax = 0.937`, not a cylindrical wall sherd like `C_01`/`C_02` where `w_ax = 0.34..0.41`), altering Rank 1 (`cyl_scored`).
4. **Why the 172-piece benchmark in Ticket 318 did not flag `Pot_A_Piece_01`:**
   - `scripts/run_benchmark_172.py` scored each piece against `min(Axes/, Ground Truth Axes/)`. On Pot A, `Ground Truth Axes/` is in an unaligned coordinate frame ($68.9^\circ$ from `Axes/`), and `Pot_A_Piece_07` happened to sit within $8.27^\circ$ of `Ground Truth Axes/` ($23.1^\circ$ from `Axes/`), while `Pot_A_Piece_01`'s $65.2^\circ$ decoy happened to sit $10.09^\circ$ from `Ground Truth Axes/`, keeping the aggregate Pot A count at `6/8` when `Ground Truth Axes/` was included, even though against the assembly-frame `Axes/` Pot A dropped from `6/8` to `5/8` (`Pot_A_Piece_01` jumping from $0.10^\circ$ to $65.2^\circ$).

### Clean Physical Distinction Between True Base Disks and Wall-Piercing Skewers (Zero Regression Across All 171 Other Pieces)

- **True base disks (`Pot_A_Piece_01`, `Pot_B_Piece_01`, `Pot_C_Piece_03`, `Pot_F_Piece_01`):** Around the true symmetry axis of a vessel base, the upturned basal rim/foot-ring is axisymmetric, so its worst-wall normalized Huber cost is tiny (**`cw <= 0.0065`**, specifically `0.00204` after LM / `0.00300` before LM on `Pot_A_Piece_01`, `0.00298` on `B_01`, `0.0053` on `C_03` and `F_01`), and its MLESAC support is large (`sz >= 4000`).
- **Perpendicular wall-piercing skewers on vertical cylindrical walls (`Pot_E_Piece_23, 24, 26, 27, 28, 30`):** A line piercing perpendicularly through a curved vertical cylinder wall (`mean_ax > 0.925`) is *not* a rotational symmetry axis of the cylinder (the wall curves in only one direction, not radially around the skewer), so its worst-wall normalized Huber cost is high (**`cw >= 0.0078`** on all Pot E lower-wall pieces: `0.0149` on `E_23`, `0.0092` on `E_24`, `0.0078` on `E_26`, `0.0159` on `E_27`, `0.0125` on `E_28`, `0.0122` on `E_30`) and its support is small (`sz <= 1656 < 4000`).
- Therefore:
  1. In `sfs_axes/potsac.py` (lines 573 and 585–586), only veto a `base` candidate when `diag > 65.0 and mean_ax > 0.925 and sz < 4000 and cw > 0.0065`:
     - Pre-LM (`cone_pre`, line 573):
       ```python
       cw_raw = max(normalized_huber_cost(cand, C0), normalized_huber_cost(cand, S1))
       base = is_base_fragment(C, cand) and not (diag > 65.0 and mean_ax > 0.925 and sz < 4000 and cw_raw > 0.0065)
       ```
     - Post-LM (`cone_scored`, lines 585–589):
       ```python
       cw_orig_raw = max(normalized_huber_cost(orig_cand, C0), normalized_huber_cost(orig_cand, S1))
       orig_base = is_base_fragment(C, orig_cand) and not (diag > 65.0 and orig_mean_ax > 0.925 and sz < 4000 and cw_orig_raw > 0.0065)
       base = is_base_fragment(C, v_ref) and orig_base and not (diag > 65.0 and mean_ax_ref > 0.925 and sz < 4000 and cw_ref > 0.0065)
       ```
  2. In `sfs_axes/potsac.py` (line 524), gate the large-cylinder LM drift relaxation (`diag >= 140.0`) by `w_ax <= 0.90` (where `w_ax = float(np.sum(mean_axs * sizes) / max(np.sum(sizes), 1))`) so flat base disks (`w_ax = 0.937` on `Pot_A_Piece_01`) keep `max_drift = 8.0`:
     ```python
     w_ax = float(np.sum(mean_axs * sizes) / max(np.sum(sizes), 1))
     max_drift = 25.0 if (diag >= 140.0 and w_ax <= 0.90) else 8.0
     ```
- **Lead pre-verification on `/tmp/basins_172.pkl` (`spartan-bm024`, `task-2803`):**
  - Across all **172 pieces** (`Pots A–J + Juglet`), this exact change alters **only 1 piece out of 172**: **`Pot_A_Piece_01`**!
  - All **171 other pieces** (`Pot_A_Piece_02..08`, all of `Pots B, C, D, E, F, G, H, I, J`, and all of `Juglet`) are **100% byte-for-byte identical** to `axes318` (`ecd5bb8`).
  - And on **`Pot_A_Piece_01`**, all 6 lines are restored to **100% byte-for-byte identity with `axes315`/`axes317`** (`Rank 0 = 0.10°` from released `Axes/Pot_A_Piece_01_Axis.xyz`, making all 8 pieces of Pot A identical to `axes315`/`axes317` which scored **8/8 sherds, 15/15 joins**).

---

## Scope & Stages

> **Constraint:** Do **NOT** run a full 10-pot assembly sweep in this ticket (per user instruction: *"future don't do full sweep unless i told you to"*). Because the 171 pieces across `Pots B–J + Juglet` (and `Pot_A_Piece_02..08`) are provably byte-for-byte identical to `axes318`, only **Pot A** needs an end-to-end assembly run on Spartan.

### Stage A — Fix `sfs_axes/potsac.py`, Add Unit Test, and Verify 172-Piece Non-Regression

1. In `/c/PR/worktrees/sfs/320/sfs_axes/potsac.py`:
   - Compute `w_ax = float(np.sum(mean_axs * sizes) / max(np.sum(sizes), 1))` and set `max_drift = 25.0 if (diag >= 140.0 and w_ax <= 0.90) else 8.0`.
   - Replace the `not (diag > 65.0 and mean_ax > 0.925 and sz < 6000)` veto in `cone_pre` and `cone_scored` with `not (diag > 65.0 and mean_ax > 0.925 and sz < 4000 and cw > 0.0065)` (using `cw_raw` on `orig_cand` and `cw_ref` on `v_ref`).
2. In `/c/PR/worktrees/sfs/320/tests/test_normalized.py`:
   - Add a unit test `test_large_base_fragment_not_vetoed()` verifying that a synthetic large flat base disk with upturned rim (`diag > 140` mm, `mean_ax > 0.93`, `d_c < 15` mm, `cw <= 0.0065`) is admitted and ranked at Rank 0 (`< 2.0°` from the true axis).
   - Run `python -m pytest C:/PR/worktrees/sfs/320 -v` on the laptop and confirm all tests pass.
3. In `scripts/run_benchmark_172.py` (or a companion verification check on Spartan `spartan-bm024` via `srun --jobid=34462441 --overlap`):
   - Extract `axes320` across all 172 pieces (`Pots A–J + Juglet`).
   - Verify and record in the write-back:
     - `Pot_A_Piece_01` Rank-0 angular error vs `Axes/Pot_A_Piece_01_Axis.xyz` drops from **$65.20^\circ$ (`axes318`) to $0.10^\circ$ (`axes320`)**.
     - All 8 pieces of `Pot A` (`Pot_A_Piece_01..08`) in `axes320` match `axes317` (`np.allclose` $\le 10^{-6}$).
     - All 164 pieces of `Pots B–J + Juglet` in `axes320` match `axes318` (`np.allclose` $\le 10^{-6}$, **0/164 pieces changed**).
     - Record both benchmark columns for Pot A: vs `Axes/` alone (`6/8` within $\le 10^\circ$ at $K=1, K \le 3$, up from `5/8` in `axes318`) and vs `min(Axes/, Ground Truth Axes/)` (`6/8`).

### Stage B — End-to-End Pot A Assembly Verification & Visual QA Render on Spartan

1. Submit a targeted Pot A assembly job on Spartan (`runs/<YYYYMMDD-HHMM>_<git7>_t320-potA`) running `A_MO` (2 internal repeats `R1, R2`) and `A_K3` (`axes320` truncated to $K=3$, 2 internal repeats `R1, R2`).
2. Poll the job to completion with `scripts/slurm_poll.sh <JOBID>` and record its `sacct` `State/ExitCode` and `runs/index.tsv` row.
3. Verify that **Pot A** at $K=3$ (`axes320`) achieves **8/8 sherds (`100%`) and 15/15 joins (`100%`)** (`1. Acc.txt`).
4. Render a before/after visual comparison (`axes318` $3/8$ collapse vs `axes320` $8/8$ restored vs `MO` $8/8$) to `C:/PR/SfSpp_preprocessing/artifacts/pota320/renders/potA_assembly_comparison.png`.
5. Write all exact numbers, commands, job IDs, and verification lines into `## Write-back` below, commit on branch `320-fix-pota-base-axis-regression`, and report back without concluding.

## Acceptance Criteria

- [ ] `sfs_axes/potsac.py` updated so large axisymmetric base fragments (`cw <= 0.0065` or `sz >= 4000`) are not vetoed by the wall-skewer filter, and `max_drift = 25.0` is gated by `w_ax <= 0.90`.
- [ ] Unit test added in `tests/test_normalized.py` and `pytest` passes (`22 passed`).
- [ ] 172-piece verification on Spartan confirms `Pot_A_Piece_01` is restored to $0.10^\circ$ at Rank 0 (`Pot_A_Piece_01..08` identical to `axes317`) and **0/164 pieces** across `Pots B–J + Juglet` change relative to `axes318`.
- [ ] End-to-end Pot A assembly at $K=3$ (`axes320`) on Spartan achieves **8/8 sherds, 15/15 joins**, with before/after render saved to `artifacts/pota320/renders/potA_assembly_comparison.png`.

## Write-back

*(To be filled by worker `sfs320`)*
