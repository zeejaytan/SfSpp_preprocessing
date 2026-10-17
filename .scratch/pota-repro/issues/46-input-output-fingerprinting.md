# 46: Cross-pot input↔output fingerprinting — reverse-engineer the author's preprocessing

**What to deliver:** the author's method, inferred from their data — or the measured proof that it can't be inferred.

**Answers:** E1

**Blocked by:** nothing (read-only analysis; runs alongside 45).

**Status:** ready-for-human (worker analysis complete 2026-10-17; no code touched, no commits)

**Starting position:** for every pot A–J we hold BOTH ends: source meshes (original_samples/SfS_pp Mesh OBJs + NURBS drivers) and the perfect-score inputs (ORIG Breaklines/Surfaces/Axes). Our chain reproduces A but not the rest — trial-and-error per pot won't scale. The author's pipeline is unpublished in detail (pristine mesh_processing.cpp + edgeline_extraction.cpp exist but the exact recipe that produced the shipped inputs is unknown).

**Method — fingerprint, then infer (never assume):**
1. Per piece, per pot: tabulate ORIG rim fingerprints — point counts, spacing distribution (uniform? adaptive?), ordering (teleports? segment structure?), segment counts + gap sizes, curvature profile along rim, normal behavior, profile rows, rim length vs GT edge length, header/index conventions.
2. Same fingerprints for OUR rims (fresh chain output) on the same pieces.
3. Diff the two tables: WHERE do they diverge systematically (spacing? termination? selection? ordering?), and do the divergences share one shape across pots?
4. From the ORIG fingerprints alone, infer the likely method family (e.g. uniform resampling at fixed step? curvature-thresholded selection? normal-consistency filter? fixed-count vs length-proportional?) — each hypothesis must PREDICT an as-yet-unchecked ORIG property; then check it.
5. Translate the confirmed inferences into concrete recipe changes for our chain (parameters, walk rules, selection rules), ordered by expected generality (all pots first, pot-specific last).

**Rules:** read-only over shipped/reference data (ORIG inputs are evidence, never material to copy into our outputs — the ticket-44 asterisk rule); no prep/assembly code changes (analysis + tables only); every claimed fingerprint carries pot/piece/numbers; every method hypothesis carries its prediction AND the check result; no commits; sacct-direct polling for any compute (held allocation or short jobs; this is mostly laptop-side table work on fetched PCDs — fetch small samples only, never bulk-copy HPC data trees); Comments-only ticket edits.

- [x] ORIG fingerprint table (all pots, per piece)
- [x] Fresh-vs-ORIG divergence table (systematic shapes, cross-pot)
- [x] Method hypotheses with prediction→check pairs
- [x] Ranked recipe changes for our chain
- [x] Job IDs + sacct states (if any compute)

## Results (worker 2026-10-17, read-only)

**Evidence:** `SfSpp_preprocessing/artifacts/pota46/`
`p46_fingerprints.csv` (620 rows: 326 ORIG + 258 fresh39-pipe B/C/D/E/F/G/I/J
+ 18 T42-B + 18 T44-B; per-rim: header segs, spacing stats, gaps, teleports,
normal agreement, curvature, z-range),
`p46_fingerprint.py`, `p46_probe1..6.py`;
fetch `pota46_fetch/` (orig 326 Bl + axes + GT-T + selected B/A surfaces,
T42/T44 B rims + T44 B surfaces). No Slurm jobs were needed (all table work
laptop-side on a 4.5MB login-node `cp`/`tar` stage + laptop Python) — no job
IDs to report. No A/H fresh rims exist in the t39 pipe (ORIG only) — coverage
below is B/C/D/E/F/G/I/J. Ticket-45's B-p2 surfaces were fingerprinted, never
modified (asterisk rule kept).

### F1 — ORIG rim recipe (all 326 shipped Breaklines, measured)
- **Uniform 1.8mm resample:** within-segment median spacing = 1.8mm in ALL
  326 files; spacing std median 0.06mm (uniform, not adaptive).
- **Clean segmentation:** 802/808 segment gaps <= 2mm; exactly 6 cross-segment
  gaps > 2mm in the whole corpus; within-segment max step 1.8mm, zero teleports.
- **Rim flags are load-bearing:** 76 files carry `isrim=1` segments (A/B/C/D/
  E/F/G/H/I/J mouth+base pieces, s1-side heavy); topflags observed: 0
  (neither), 1 (rim), ±2 (base, sign=sane), -3 (rim+fractured base).
  Code consumers in `structure-from-sherds-pp` (verified by reading):
  `feature_matching.cpp` LCS + LCSGraphBuilding **mask rim-flagged ranges out
  of fracture matching** (`LCSuff=0` there); `CountPCInlier`/profile code uses
  flagged points for the H_rim "breakline cannot overtop rim" veto.
  Our chain writes topflag=0/segflags all 0 on EVERY rim (t39 pipe, T42, T44)
  → no masking, no veto, ever.
- **Curvature column unset:** all 326 ORIG files carry curvature = 1.0
  (constant). It loads to `feature_[6]`; consumers disagree on what [6] is
  (PF++ optimizer reads it as *thickness*, `FORK_VS_UPSTREAM.md:95` calls the
  load near-dead). Our fresh rims carry real curvature (~0.01–0.07) in the
  same column.
- **Normals agree:** consecutive-normal dot median 0.9945–1.0 (smooth).

### F2 — Fresh-vs-ORIG divergences (systematic, cross-pot)
- **D1 ordering/teleports (Bl_0, ALL 8 pots):** within-segment jumps of
  20–134mm are the norm, not the exception (B: 9/9 Bl_0 rims; C: 4/4; D:
  15/29; E: 26/31; F: 1/7(+s1); G: 3/7; I: 20/30; J: 9/12). Signature of
  decorative appends concatenated out of order (T14-style staging), not of
  resampling. ORIG has zero.
- **D2 bloat (Bl_0, pot-clustered):** npts > 2× ORIG on B p01 (1069 vs 210),
  p02, p04, p09; D p10/12/14/15 (~650–690 vs ~120–180); E p04–p19 (20 pieces,
  up to 946 vs 174); I p06–p19 (13 pieces, up to 821 vs 142); J p02/05/06/09.
  C/F/G clean (no piece > 2×). Same append family as D1.
- **D3 no rim flags (all fresh, all pots):** topflag=0 + all-zero segflags on
  all 294 fresh rims vs 76 flagged ORIG files — our rims enter fracture
  matching unmasked, including mouth/base arcs. Predicts forest bloat
  (matches T39: fresh forests dwarf ORIG, e.g. B 1442 vs 114).
- **D4 step 1.9 vs 1.8:** fresh within-seg median 1.905mm, std 0.19 (vs 0.06)
  — close but uniformly coarser and noisier; Bl_0 z-extent ratio fresh/ORIG
  med 1.02–1.12 (fresh slightly LONGER via appends; shorts: F p02 0.78,
  I p29 0.74).
- **D5 B-p2 instance:** ORIG Bl0 150pts/z82.5/len267 → T42 149pts/z56.3 (lip
  lost; profile rows 9–15 vs ORIG 18–34 explained by z-extent 0.68×) → T44
  197pts/z81.6/len466 (3 gate-legal gaps 16/61/67mm; E2E 9/9+15/15).
  T44 length 466 vs ORIG 267 = T42 upper + lip branches + gap spans; big
  cross-segment gaps are E2E-harmless (segments match independently).
  Fresh39-pipe p2 (pre-T42) was 358pts/len597/z86 (worst bloat case).
- **D6 lip points exist in our surfaces:** B-p2 S0 z<350: ORIG 1642 pts vs
  FRESH 2033; S1: 1887 vs 1718; z-extents match (ORIG 330.9–414.3 vs fresh
  327.7–413.9). The lip geometry is IN our surfaces — the walk doesn't
  descend (supports 45's hypotheses a/b over extraction-loss c). Reported as
  numbers only; ticket-45 owns the diagnosis.

### Method hypotheses (each with prediction → check)
- **H1 (CONFIRMED): author's rims = uniform 1.8mm resample of ordered,
  single-pass rim walks.** Predicted: spacing std ≈ 0 everywhere + gaps ≤2mm
  except a handful of segment joints. Checked: holds on 326/326 files.
- **H2 (CONFIRMED mechanism): isrim/topflag flags gate live assembly
  machinery** (LCS masking, H_rim veto). Predicted: zero-flag rims admit
  mouth/base-arc hypotheses ORIG suppresses. Checked in code (both call
  sites); E2E consequence is the successor's to measure, not assumed.
- **H3 (leads): our Bl_0 teleports/bloat = unordered decorative appends.**
  Predicted: removing appends (T42-style) collapses teleports; T42 B-Bl_0
  kept only a 16.4mm joint gap (1 teleport at a segment joint). Checked on
  B; successor to generalize per recipe R1.
- **H4 (open): column-7 curvature-as-thickness.** ORIG 1.0-constant vs ours
  ~0.05 in a column one optimizer path reads as thickness. Predicted: only
  matters if the E2E path consumes `feature_[6]`. Check left to successor
  (wire-tracing, no data needed).

### Ranked recipe changes (for successor tickets, general first)
1. **R1 — order + clip Bl_0 appends** (all pots; kills D1+D2, the largest
   systematic divergence).
2. **R2 — emit true isrim/topflag flags** (mouth/base detection → header
   flags; restores LCS masking + rim veto; addresses D3/forest bloat).
3. **R3 — resample step 1.8 + uniformity gate** (std check per rim; D4).
4. **R4 — resolve column-7 semantics** (trace `feature_[6]` consumers, then
   either write 1.0-constant or true thickness; H4).
5. **R5 — pot-specific shorts** (F p02, I p29 z-extent; walk-termination
   family shared with 45's B-p2 work).

**Successor:** implement the top-ranked recipe change (new ticket per change); ticket 45 continues as the B-p2 instance.
