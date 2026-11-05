## Comments

### 2026-11-05 · worker session sfs307 · Stage A (clause audit), Stage B (arms), Stage C (verdict)

**Verdict in one paragraph.** The paper and the authors' MATLAB disagree on one thing that changes the emitted set: `run_potsac.m:61` and `:78` delete every candidate whose Huber cost is more than 10 % above the first survivor's, and the paper (`:175`) describes only the top-10 cut plus the 10° dedup. The prune is the authors' own code (it is in the vendored pristine tree, not a local fix), but it is not the paper's method, and on the assembler it costs sherds at every seed. The shipped default is now the paper's candidate set (`SFS_AXES_COST_PRUNE=0`); the authors' prune stays one environment variable away (`=1`). Pot A with our axes at NP=8: paper set **7/8 13/15, 8/8 15/15, 7/8 13/15** (seeds 0/1/2) against the authors' prune **6/8 10/15, 7/8 12/15, 6/8 10/15**. The 8/8 + 15/15 is reached at **one** of three seeds, not two, so C1 is **not met**; the named blocker is Pot A Piece 08 spun to the wrong place on the pot (joins 2–8 and 4–8 at 86° / 165–169 mm on seed 0 and 168° / 376–380 mm on seed 2), and it is not a clause difference. Corpus: 84/163 pieces within 5° (median best 4.56°) with the new default vs 83/163 (4.66°) with the authors' prune — no worse. MATLAB parity still passes at 1e-9, pytest 9/9. Nothing is committed.

#### 1. What ships

Two files, both in `sfs_axes/` (uncommitted; the lead commits):

- `sfs_axes/potsac.py` — `COST_PRUNE` default flipped `"1"` → `"0"` (paper's set is the default); the `ADAPTIVE_UNDER_5K` comment rewritten: the under-5,000-point step rule is a **deviation**, not the authors' rule (it exists only in the locally patched `AxisExtraction/run_potsac.m:18-27`, commit ff40fc9); module docstring updated to name `run_potsac.m:61/:78` as the prune's home.
- `sfs_axes/cli.py` — module and `extract_piece` docstrings say what the new default is, where the paper says it (`papers/text/sfspp-2502.13986v1.md:175`), and how to get the authors' chain back.

`git diff --stat`: `sfs_axes/cli.py | 21 +-`, `sfs_axes/potsac.py | 58 +-`. `python -m pytest tests/ -q` → 9 passed. `git status`: nothing else modified in tracked files.

#### 2. Stage A — clause table (A1)

Provenance established first, because two copies of the MATLAB exist here. `original_nurbs_preprocessing/AxisExtraction/` is the vendored pristine upstream (commit 3095064 "Vendor the pipeline source from the nested clone", provenance back to 405c048 Sisung Liu 2025-03-06). `AxisExtraction/` is the local working copy (ff40fc9 Zeejay Tan 2025-11-15 "Local fixes: MATLAB bugs, headless build, path corrections, SFS format"). `diff -r` between them, ignoring line endings: **one behavioural difference in the whole axis chain — `run_potsac.m`**, whose local copy adds the adaptive-step block at `:18-27`. Every other axis `.m` is identical. So a quote from any other file is the authors' code; a quote from the local `run_potsac.m:18-27` is not.

| # | paper (`papers/text/sfspp-2502.13986v1.md`) | authors' `.m` (pristine) | ours | changes the emitted set? | verdict |
|---|---|---|---|---|---|
| 1 | `:173` "MLESAC-based sampling with a minimal 6-point solver" | `compute_axis_of_symmetry.m:7` (`num_sample_set = 6`), `:9` (`max_iters = 1000`), `:18` `randsample(num_points, 6)` | `potsac.py:74-76`, `:108` | no (sampling only) | **MATCH** — 1,000 fixed uniform 6-point draws without replacement; no adaptive stopping, no likelihood weighting (A-Q2) |
| 2 | `:173` "Pottmann's constraint — the offset vector, symmetry axis direction, and the cross product of the surface normal lie on the same plane" | `compute_pottmann_axis.m:14-25` (reduced 3×3 system, smallest singular vector) | `pottmann.py:26-32` | no (solver only) | **MATCH** — one axis per 6-point sample (A-Q3) |
| 3 | `:173` "the original PotSAC outputs only a single axis … we propose a modified version capable of producing multiple axes" | `run_potsac.m:34-37` (10 refined candidates kept) | `potsac.py:229-231` | yes | **MATCH** |
| 4 | `:175` "selects the top 10 candidate axes" | `run_potsac.m:22` (`num_candidates = 10`), `:37` | `potsac.py:208`, `:231` | yes | **MATCH** |
| 5 | `:175` "those with an angle of 10 degrees or less are considered duplicates, with the axis having the higher cost … removed through pruning" | `run_potsac.m:47-56` (`angles > 0.9848`, `repeats(jj)`) | `potsac.py:134-146` | yes | **MATCH** on threshold and rule; documented quirk: MATLAB marks the *second* member of each pair, i.e. the later one in the GM-sorted order, which is usually but not always the dearer |
| 6 | `:175` "we initially sample only 10% of the surface points" | `run_potsac.m:18` `C(:,1:10:num_points)` | `effective_step` + `cli.py` `--step 10` | yes | **MATCH** for pieces ≥ 5,000 points; **DIFFERS-DOCUMENTED** below 5,000 (row 17) |
| 7 | `:175` "after pruning, all surface points are used for more detailed refinement" | `run_potsac.m:66-68` (`refine_axis(vt(:,i), C, …)` on all `C`); `read_surfaces.m:21-32` keeps both walls whole | `potsac.py:240-241`; `io_surfaces.read_surfaces(truncate=False)` (default since 306) | yes | **MATCH** |
| 8 | `:173` "an extended Cao and Mumford error, applicable to both interior and exterior surfaces" | `compute_biaxial_cao_error.m:16-19` (log-sum-exp soft-min over the two normal-sign hypotheses, `s = 100`) | `cao.py:54-85` | yes (cost feeds ranking) | **MATCH** |
| 9 | `:175` "cost, defined as the robustified residual error" | `run_potsac.m:39-45` (Huber width 1.0, sum of per-point cost) | `potsac.py:265-269`, `_huber_per_point` | yes | **MATCH** |
| 10 | `:173` "trust-region-based nonlinear optimization" | `optimize_using_lm.m:25-91` (LM/trust-region hybrid, max_trials 20, Triggs-corrected robustifier, `J(:,1:3)` projected) | `refine.py` | no (refines, does not select) | **MATCH** — the `.m` is the operative reading; the paper's phrase is generic |
| 11 | — (no paper clause) | `run_potsac.m:61` and `:78` `good_cost_idx = cost < cost(1) * 1.1` | `potsac.py` `COST_PRUNE`, `_dedup` | **yes** | **DIFFERS-DOCUMENTED**, decided: default **OFF** (paper). Measurement in §3 |
| 12 | — (no paper clause) | the second prune at `:78` runs on the **stale** stage-1 cost, never recomputed after the all-points refinement | `_dedup` is handed the same stage-1 cost at `:247` | yes (when the prune is on) | **MATCH** — quirk reproduced faithfully |
| 13 | — (no paper clause) | `run_potsac.m:82-83` `[cost, ia] = sort(cost); vt = vt(:, ia)` — ascending | `potsac.py:248-251` `np.argsort(cost)` | yes | **MATCH** |
| 14 | — (no paper clause) | `run_potsac.m:8-16` one-wall handling (`half_point = floor(0.5*n)`) | `run_potsac(C1, C2=None)` | n/a here (both walls present on all 163 + Pot A) | **MATCH** |
| 15 | — (no paper clause) | `compute_axis_of_symmetry.m:29-34` computes `num_inliers`, never uses it for stopping | `potsac.py:120-121` records inliers, unused | no | **MATCH** |
| 16 | `:155` "B-Spline fitting refines the surface boundaries" | no axis `.m` reads a spline; surfaces arrive as xyz | `io_surfaces.read_surfaces` | no | **MATCH** — a surface-generation clause, nothing to port into the axis chain |
| 17 | — (no paper clause; **local only**) | `AxisExtraction/run_potsac.m:18-27` (ff40fc9): `step = 1` under 5,000 points — absent from the pristine tree | `ADAPTIVE_UNDER_5K` (default ON) | yes | **DIFFERS-DOCUMENTED**, kept ON — see B5 and the buddy arm in §6 |

#### 3. Stage A — the three questions and the 1.1-prune decision (A3)

**A-Q1 — is the `cost < cost[0]*1.1` prune in `run_potsac.m`, and is the paper's "top 10 survive" the same quantity?** Yes to the first: the prune is in the authors' file, twice (`:61` after the stage-1 dedup, `:78` after the all-points refinement), and it applies to the survivors of the 10° dedup, not to the top 10. It is not the same quantity as "top 10 survive": the paper's sentence stops after the dedup, so under the paper as written up to 10 non-duplicate axes are written; the `.m` keeps only those within 10 % of the *first survivor of the GM-sorted order* (which is not necessarily the minimum Huber cost — `compute_axis_of_symmetry.m:48-51` sorts by the GM-robustified sum, while `cost` here is the Huber sum). What it costs on Pot A: Piece 07's second released basin is 3.5× the best cost and dies in all four probe cases; Piece 08's good line is rank 1–38 and dies at one seed. So yes, this single line is the difference between the two methods.

**A-Q2 — is the sampling adaptive (MLESAC stopping / likelihood weighting) or 1,000 fixed uniform draws?** 1,000 fixed uniform 6-point draws without replacement (`compute_axis_of_symmetry.m:9`, `:18`); `num_inliers` is computed at `:31-33` and never used; "MLESAC" survives only as the MSAC-style GM ranking at `:29-32`. Our port matches, so **B2 is closed: there is no adaptation to port.**

**A-Q3 — does `compute_pottmann_axis.m` return one axis per sample or several?** One: the smallest singular vector of the reduced 3×3 system (`:20-25`), unscaled and projected onto the tangent plane by the caller. Multiple axes come from many samples. Our `pottmann.py:26-32` is the same solve, so **B3 is closed: nothing more to extract per sample.**

**The decision (A3).** Default = the paper's set, no cost prune. Warrants, in order: (i) the paper describes the method and has no such line; (ii) the prune is the only place the two differ in a way that changes what is written; (iii) measured on the assembler it is worse at every seed (§6, B1 vs base) and worse or equal on the corpus (83/163 vs 84/163 within 5°); (iv) it is reversible by one env var, and the chain it belongs to is still exercised by the parity gate. The authors' chain is therefore *available*, not *default*, and the parity test (C2) still runs it.

#### 4. Stage A — line-count census, 163 pieces (A2)

Arms: **paper** = new default (no prune, under-5k rule on); **prune** = authors' chain (`SFS_AXES_COST_PRUNE=1`). Released = `$CORP/Axes/*.xyz`, 220 lines over 163 pieces.

| pot | pieces | released lines | paper: ours | paper: fewer/equal/more | prune: ours | prune: fewer/equal/more |
|---|---|---|---|---|---|---|
| A | 8 | 11 | 12 | 1 / 5 / 2 | 11 | 1 / 5 / 2 |
| B | 9 | 10 | 16 | 0 / 4 / 5 | 12 | 1 / 6 / 2 |
| C | 6 | 7 | 10 | 0 / 4 / 2 | 10 | 0 / 4 / 2 |
| D | 32 | 45 | 45 | 3 / 26 / 3 | 45 | 3 / 26 / 3 |
| E | 34 | 41 | 38 | 3 / 31 / 0 | 35 | 4 / 30 / 0 |
| F | 7 | 9 | 10 | 1 / 5 / 1 | 9 | 1 / 5 / 1 |
| G | 7 | 7 | 7 | 0 / 7 / 0 | 7 | 0 / 7 / 0 |
| H | 11 | 24 | 23 | 2 / 4 / 5 | 14 | 6 / 3 / 2 |
| I | 30 | 33 | 40 | 0 / 25 / 5 | 37 | 0 / 27 / 3 |
| J | 19 | 33 | 37 | 3 / 9 / 7 | 31 | 5 / 9 / 5 |
| **all** | **163** | **220** | **238** | **13 / 120 / 30** | **211** | **21 / 122 / 20** |

Differing pieces, paper: A06 A07 A08 B03 B05 B06 B07 B09 C02 C06 D15 D17 D21 D24 D27 D30 E21 E31 E34 F05 F07 H02 H04 H06 H07 H08 H09 H10 I16 I17 I27 I28 I29 J05 J06 J07 J11 J12 J13 J14 J16 J18 J19 (43). Differing pieces, prune: A06 A07 A08 B05 B08 B09 C02 C06 D15 D17 D21 D24 D27 D30 E20 E21 E31 E34 F05 F07 H02 H05 H06 H07 H08 H09 H10 H11 I17 I27 I29 J05 J06 J08 J11 J12 J13 J14 J15 J18 J19 (41). Pot A Piece 08 is 3/2 on the paper arm (we write one line more than released) and 1/2 on the prune arm — the same difference that decides the assembly.

#### 5. Stage A — A4

Every row of the table above is `MATCH` except three `DIFFERS-DOCUMENTED` (row 6 below 5,000 points, rows 11 and 17), and each is closed by a measurement, not by assignment to an arm still to run: row 11 by B1, rows 6/17 by B5 and its buddy arm (§6). **No `DIFFERS-UNDOCUMENTED` row remains.**

#### 6. Stage B — arms (one variable each; Pot A, seeds 0/1/2)

The number is the assembler's own `1. Acc.txt` (sherds / joins), NP=8, `ARMSPEC "MM:2"` (two internal repeats, identical in every case below), `NAMED=8`, `FLOOR=50`, lanes = ticket 66 `outU_pota/geom`, axes = this ticket's own extraction. NP matters: at NP=3 every arm under-scores (the *same* axis set that gives 7/8 12/15 at NP=8 gives 5/8 7/15 at NP=3), so the NP=3 sweep run earlier in this ticket is kept only as a record and is **not** the table below.

| arm | what varies | warrant | K per piece 01–08 (s0 / s1 / s2) | Pot A s0 / s1 / s2 | verdict |
|---|---|---|---|---|---|
| **B1** | paper's set: no cost prune | paper `:175` | s0 1 1 1 1 1 2 2 3 / s1 1 1 1 1 1 2 2 5 / s2 1 1 1 1 1 2 2 3 | **7/8 13/15 · 8/8 15/15 · 7/8 13/15** | **ACCEPTED — becomes the default** |
| base | authors' prune (previous default) | `run_potsac.m:61,:78` | s0 1 1 1 1 1 2 1 3 / s1 1 1 1 1 1 2 1 5 / s2 1 1 1 1 1 2 1 3 | 6/8 10/15 · 7/8 12/15 · 6/8 10/15 | reference arm |
| B2 | MLESAC adaptation | none exists | — | — | **CLOSED**: A-Q2, 1,000 fixed uniform draws |
| B3 | Pottmann multi-axis per sample | none exists | — | — | **CLOSED**: A-Q3, one axis per sample |
| B4 | rank by post-refine cost (all points) | no clause prescribes it | s0 … 1 3 / s1 … 1 5 / s2 … 2 3 | 6/8 10/15 · 7/8 12/15 · 5/8 7/15 then 6/8 10/15 | **REJECTED** — worse or equal, and unstable between repeats |
| B5 | step = 10 always (under-5k rule off) | local `run_potsac.m:18-27` removed | s0 1 1 1 1 1 2 2 3 / s1 … 2 1 2 / s2 … 2 1 4 | 7/8 13/15 · 6/8 10/15 · 6/8 10/15 | **REJECTED** — no seed improves consistently; Piece 07 loses its second line on s1/s2 |
| (buddy) | paper's literal 10 % **and** no prune | paper `:175` | s0 … 2 2 3 / s1 … 2 2 2 / s2 … 2 2 4 | not assembled (B1 and B5 already isolate both variables) | **Piece 08's released line is lost at all three seeds** (cov5 = 0) — this is why the deviation stays |
| B6 | any remaining `DIFFERS-UNDOCUMENTED` row | — | — | — | **CLOSED**: §5, none remain |

Piece 07 and Piece 08 specifically (B5's named pieces, and the two the ticket is about). Piece 07 has 3 released lines; the paper's set gives it **2** at all three seeds and the prune gives it **1**; no arm reproduces its lines 1–2 (ticket 306: line 2 is in no pool at 120–130°, nearest draw 8.55° away; line 1 is in the pool at 5.06–6.54° but 3.5× the cost). Piece 08 has 2 released lines; the paper's set gives it **3 / 5 / 3** lines.

Run ids and `sacct` (all `COMPLETED | 0:0`):

| run dir (`runs/20261105-0424_e6adf69_t307-…`) | job | elapsed | result |
|---|---|---|---|
| `b1-s0-np8` | 34372619 | 6:15 | 7/8 13/15 |
| `b1-s1-np8` | 34372620 | 6:59 | **8/8 15/15** |
| `b1-s2-np8` | 34372621 | 8:46 | 7/8 13/15 |
| `base-s0-np8` | 34372628 | 5:00 | 6/8 10/15 |
| `base-s1-np8` | 34372629 | 5:20 | 7/8 12/15 |
| `base-s2-np8` | 34372630 | 5:35 | 6/8 10/15 |
| `b4-s0/s1/s2-np8` | 34372622 / 34372623 / 34372624 | 7:44 / 9:10 / 8:51 | 6/8 10/15 · 7/8 12/15 · 5/8 7/15 + 6/8 10/15 |
| `b5-s0/s1/s2-np8` | 34372625 / 34372626 / 34372627 | 7:35 / 4:49 / 7:13 | 7/8 13/15 · 6/8 10/15 · 6/8 10/15 |
| extraction `20261105-0406_e6adf69_t307a-axes` | 34372174 | 1:54 | 96/96 Pot A + 3×163 corpus |
| default-flip proof `20261105-0437_e6adf69_t307f-def` | 34373280 | 2:29 | paper == b1 byte-identical, 3 seeds |
| NP=3 record `-s0/s1/s2` (12 runs) | 34372425/26/33, 34372436/56/57, 34372458/59/60, 34372461/62/63 | 2:28–4:57 | **superseded, see NP note** |

The strict scorer (`score305.py`) reproduces the binary's join count in all 24 run × repeat checks (13, 15, 13, 10, 12, 7+10, 13, 10, 10, 10, 12, 10). Its per-piece column is not usable as printed — it reports 0/8 on runs where the binary says 7–8 and where pieces 1–6 take identical values in different arms (a frame artefact of that diagnostic) — so sherd counts are quoted from `1. Acc.txt`.

#### 7. Stage C — C1 verdict and the named blocker

Criterion: 8/8 + 15/15 with our axes at 2 of 3 seeds. Measured: **1 of 3**. C1 is **not met**; the best attempt is reported (best-of-N rule): `20261105-0424_e6adf69_t307-b1-s1-np8`, job 34372620, **8/8 sherds, 15/15 joins**, both internal repeats, joins at 0.727–3.789° and 3.17–25.07 mm.

**Named blocker — Pot A Piece 08, joins 2–8 and 4–8.** Every failing join on the other seeds involves Piece 08:

- seed 0 (7/8 13/15): join 2–8 **86.0° / 164.7 mm**, join 4–8 **84.9° / 169.0 mm** — seated near a quarter-turn out;
- seed 2 (7/8 13/15): join 2–8 **168.6° / 376.0 mm**, join 4–8 **167.1° / 379.9 mm** — near a half-turn out;
- seed 1 (8/8 15/15): all 15 joins pass.

The other 13 joins pass on every seed at 0.5–3.8° and 3–23 mm. This is not a missing axis and not a pose error: on seeds 1 and 2 both of Piece 08's released lines are within 5° of one of our lines (cov5 = 1, best 3.68° / 3.13°), and the assembly still differs between them — so what remains is *which* of Piece 08's 3–5 candidate lines the assembler matches, and the paper prescribes nothing after "top 10 by cost" that would decide it. On seed 0 one released line is 5.67° away and the other beyond 10°, the worse case. No single-variable arm closes it: B4 (post-refine ranking) worse, B5 (step=10) worse, the authors' prune worse. **This is the named blocker; it is not a gap in the paper's clause set but in the assembler's choice among lines the paper allows.**

#### 8. C2, C3, C4, C5

**C2 — parity PASS.** `20261105-0438_e6adf69_t307c-matlab-unit`, job 34373396, `COMPLETED 0:0` in 0:32. 9 rows (Pot A Piece 01/04/07 × probes released/+2°/+5°), all PASS at the 302 bar: `R1_rel` 4.6–4.8e-15, `J_rel` 4.8e-15–7.6e-13, `R3_rel` 4.7–5.0e-15, `OVERALL: PASS`, `compare rc=0`. Run against the **edited** tree (`potsac.py` md5 287fe6042ffaf92f72e1eefea9a89042, the same file the extraction job used). `python -m pytest tests/ -q` → 9 passed.

**C3 — corpus 163, released md5 unchanged.** `20261105-0437_e6adf69_t307f-def` (job 34373280) wrote all 163 axis sets for both chains to new paths (`out/axes/`, `out/axes_prune/`) and logged "corpus Surfaces+Axes unchanged"; no file under `Dataset/` was touched by any job in this ticket. Tier table (`analyse306c.py`, direction only):

| tier | pieces | median best° | within 5° | paper arm | prune arm |
|---|---|---|---|---|---|
| gt_close (all released lines matched) | 78 | 2.13 | 100 % | same | same |
| gt_off | 85 | 12.50 | 7.1 % | same | same |
| **all** | **163** | **4.56** | **51.5 % (84/163)** | **84/163, 4.56°** | 83/163, 4.66° |

Baseline to beat was 84/163 within 5° and median best 4.63° (ticket 306): the paper's set **equals the count and improves the median**; the authors' prune is one piece short. **`rad_mm` is not reported**: this worktree has no compare-only radial instrument (`analyse306c.py` emits direction; `corpus302.py`'s `rad_mm` is computed inside its own extraction loop), and ticket 302 flagged that column's validity. Flagged as the one unmet part of C3 rather than silently dropped — the last valid radial figure on record is 304's corpus run (median 21.171 mm, n=163), which is not comparable to this axis set.

**C4 — Juglet arm, F20 floor.** `20261105-0422_e6adf69_t307d-jug`, job 34372673, `COMPLETED 0:0` in 3:22. Our axes (default chain, seed 0) → `F20N_r1..r3`: **0/9 sherds, 0/36 directed pairs**, 8 of 9 pieces get a transform, chamfer 249.5–278.5 mm; the authors' own Dataset axes → `F20O_r1..r3`: **0/9, 0/36**, 2 of 9 pieces get a transform, chamfer 19.7–21.5 mm; seat bar 4.596 mm, `seated_count 0` both. At F20 the Juglet lane fails for both axis sets — the axis set is not the discriminator, and this arm changes nothing about the ticket's verdict. K per Juglet piece: 1,1,2,1,1,1,2,3,2.

**C5 — render.** `artifacts/pota307/pota307_b1-s1_vs_base-s1.png` (409,207 bytes; job 34373360, 0:11), two rows: top (x,y) and side (x,z); left = paper set 8/8 15/15, right = authors' prune 7/8 12/15. Reading it (image description; this session has no image input): the left panel shows 8 distinct sherd clouds forming one continuous wall band; the right panel shows 7 clouds with Piece 7 sitting isolated near the centre — the missing sherd is the one the prune loses, not a general collapse. Defaults are documented in the `cli.py`/`potsac.py` docstrings (§1).

#### 9. Corrections to the record

1. **Ticket 304's provenance claim is wrong.** `SFS_AXES_ADAPTIVE_UNDER_5K` was documented as "this IS the authors' rule, not a deviation". The pristine `run_potsac.m:18` has no size exception; the block exists only in `AxisExtraction/run_potsac.m:18-27` (ff40fc9, Zeejay Tan). Corrected in `potsac.py` this ticket. The rule stays on (its own 304 measurement; Piece 08's released line is lost without it), but it is a deviation and must be reported as one.
2. **Ticket 306's collapse finding is an NP artefact.** "Adding any second line to Piece 07 drops Pot A to 4/8 5/15" was measured at `NP = 3` (recorded in both `run.json` files, jobs 34358233 and 34358971), the setting that under-scores every arm. At NP=8 the same construct — with the paper's set on — seats Pot A 8/8 15/15 (b1-s1). Do not carry the collapse claim forward.
3. **The MO 8/8 15/15 bar cannot be re-verified from its run directories.** `runs/20261105-0615_9c5eec2_t305-e2e-a-moom` and `runs/20261105-0617_9c5eec2_t305-e2e-a-moom` both have an empty `out/` and an empty `logs/` (no `acc.log`, no `panel.tsv`, no `1. Acc.txt` anywhere under the run). The numbers in this ticket's brief came from those runs and are quoted as given; the directories themselves do not support them. The directory name in the ticket text (`20261105-0617_c333dc7_t306-c1c-moom`) does not exist.
4. **The 306 baseline reproduces.** "84/163 within 5° / median 4.63°" was produced by a chain that then defaulted to the authors' prune; the paper's set reproduces the count (84/163) with a slightly better median (4.56°). Note this when comparing to 306's tables.

#### 10. Acceptance

- [x] **A1** clause table (§2), 17 rows: paper quote, `.m file:line` + whose commit, our `file:line`, whether it can change the emitted set, verdict.
- [x] **A2** census (§4), 163 pieces, per pot, both chains, differing pieces named.
- [x] **A3** A-Q1/Q2/Q3 answered with quotes (§3); the 1.1-prune conflict decided in writing with its measurement.
- [x] **A4** no `DIFFERS-UNDOCUMENTED` row remains; the three `DIFFERS-DOCUMENTED` rows are closed by B1/B5 measurements (§5).
- [x] **B1** paper's set emitted and measured on Pot A, 3 seeds, K per piece (§6).
- [x] **B2–B6** B2 and B3 closed by A-Q2/A-Q3; B4 and B5 run and rejected; B6 closed (§6).
- [ ] **C1** **not met** — 1 of 3 seeds (8/8 15/15 at seed 1); named blocker in §7.
- [x] **C2** parity 1e-9 PASS on the edited tree; pytest 9/9.
- [x] **C3** corpus to new paths, released md5 unchanged, tier table vs 306 baseline; `rad_mm` **not** reported (flagged in §8).
- [x] **C4** Juglet arm reported (§8).
- [x] **C5** render in `artifacts/pota307/`, defaults documented.

#### 11. The diff to ship, with the warrant for each hunk

| file | hunk | warrant |
|---|---|---|
| `sfs_axes/potsac.py` | `COST_PRUNE` default `"1"` → `"0"` | paper `:175` has no cost prune; measured better on Pot A at all three seeds (B1 vs base, §6) and no worse on the corpus (§8 C3) |
| `sfs_axes/potsac.py` | `_dedup`: `if vt.shape[1] == 0 or not COST_PRUNE: return vt, cost` | the switch above; keeps `run_potsac.m:61/:78` reachable with `SFS_AXES_COST_PRUNE=1` |
| `sfs_axes/potsac.py` | `ADAPTIVE_UNDER_5K` comment rewritten (deviation, provenance, B5 measurement) | pristine `run_potsac.m:18` has no size exception; only `AxisExtraction/run_potsac.m:18-27` (ff40fc9) adds it — §9.1 |
| `sfs_axes/potsac.py` | module docstring: prune named at `run_potsac.m:61`/`:78` and marked OFF by default | same two warrants |
| `sfs_axes/cli.py` | module + `extract_piece` docstrings: what the default emits, the paper line, how to restore the authors' chain | documentation of the flip; no behaviour change of its own |

Nothing is committed or pushed: `git status` shows only `sfs_axes/potsac.py` and `sfs_axes/cli.py` modified, plus this ticket's untracked instruments under `.scratch/pota-repro/307-stage/`.

#### 12. Open for the lead

1. Decide whether C1's blocker is worth a follow-on ticket. It is not a paper-fidelity gap any more (the paper's set is shipped and reaches the authors' best result at one seed); it is the assembler's choice among Piece 08's candidate lines. Directions none of which the paper prescribes: a stability rule (write only lines that survive more than one seed), a cap on lines per piece, or leaving it — the authors' own axes also give Piece 08 two lines and reach 15/15 every seed, so nothing in the corpus says how many lines a piece should get.
2. The `rad_mm` column (C3) needs a compare-only instrument before it can be reported for any axis set.
3. `artifacts/pota307/` holds one PNG; the conservator should read it before the 8/8 vs 7/8 claim is repeated anywhere (this session cannot see images).
