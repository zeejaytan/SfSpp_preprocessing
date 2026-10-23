Status: done

## Lead verdict (2026-10-21)
OURS-AT-EDGE accepted. R6: numbers EXACT (baseline 1.294, control 41.63/41.47 PASS, line 16.29, disputed 39.22/1.35); Comments + instrument + provenance caveat verified; profile PNG on disk; only this ticket touched among tracked (.scratch/pota229/ + gitignored artifacts/pota229/ new). User's read confirmed with a working instrument: in the disputed stretch ours rides the crease at control level, author sits at smooth-face baseline. Changes: RULER CAVEAT ONLY (author P27-Bl1 locally off-edge in idx 0-13/52-64); lane bar unchanged (cov counts the whole lane; P27 still fails). Provenance: no full-res P27 mesh exists anywhere (Spartan copies all byte-identical _DS); measured on dense ORIG cloud as documented.

## Goal
Settle the P27 disputed stretch (user order m03707): the user reads the author's lane as sitting mid-surface and ours at the edge. Test at ORIGINAL mesh density which line sits on the true fracture edge -- a sharpness test along both lines, with a control stretch. Ends at measurement + verdict; changes nothing (no rule, no reseat, no assembly).

## Boundary
- Disputed stretch: P27@12/Bl0 dots >2mm from the nearer author lane (27 dots; lanes: C:/PR/SfSpp_preprocessing/.scratch/pota227/lanes/Pot_D_Piece_27_Breakline_0.pcd; author: .scratch/pota225/Pot_D_Piece_27_Breakline_0_author.pcd + _1_author.pcd; slots per 209 pattern).
- Full-resolution Pot D Piece 27 mesh lives on Spartan (214 sampled ORIG meshes there; worker locates the canonical mesh -- NOT the laptop _DS decimation in .wt-217/temp_download, which is too coarse to carry the edge). Fetch the disputed REGION plus one agreeing control region to the laptop (artifacts landing zone, gitignored) or measure on Spartan held allocation; no new clusters, no code changes, no sbatch chains (single measurement job or login-node/python only).
- MAY touch: fresh dir C:/PR/SfSpp_preprocessing/.scratch/pota229/ (script + numbers + one picture, gold/blue/black scheme ONLY: author GOLD #ffae00, ours BLUE #0057ff).
- MUST NOT touch: main worktree tracked files except this ticket's Comments; other tickets; bundles; any source or binary.

## Constraints
- INSTRUMENT CHECK FIRST: state the sharpness measure (e.g. median dihedral/normal-variation along a line) AND the decision line BEFORE measuring. Then validate on the CONTROL stretch (where our lane and author coincide, both must read 'crease'); if the control does not read crease on both, the instrument is blind at this density -- report BLIND, do not proceed to the verdict.
- Only then measure the disputed stretch: sharpness along our line vs along the author line, same vertices density, same radius. Report medians + a profile plot along the stretch.
- A line across a smooth rounded lip reads low-curvature; a true fracture edge reads a crease peak. Either line may win; 'both crease' and 'neither creases' are allowed outcomes with their meanings stated.

## Acceptance (lead judges; numbers + cites + paths)
- Control result (both lines crease, with numbers) or BLIND with the reason.
- Disputed-stretch sharpness comparison (both lines, medians + profile picture on the mesh region, eye-checked by worker).
- Verdict: OURS-AT-EDGE (user confirmed, author locally wrong) / AUTHOR-AT-EDGE (user's read refuted with numbers) / BLIND-or-MIXED (state exactly what the numbers support). One line on what this changes (ruler caveat only -- lane bar unchanged: cov counts the whole lane).

## Required evidence to report
- Bottom line first (one of the three verdicts + the two medians). Then instrument, control, profile picture, mesh provenance (which file, vertex count), script path.

## Comments (worker 229, 2026-10-21 -- measurement only, nothing changed)

**Bottom line: OURS-AT-EDGE.** User confirmed: in the disputed stretch the author lane runs mid-surface, ours rides the true fracture edge. Disputed medians: ours-Bl0 39.2 deg vs author-Bl1 1.4 deg (face baseline 1.3 deg, decision line 16.3 deg).

**Instrument (pre-registered before measuring).** Normal-spread S(p) = deg(acos(|mean unit normal|)) over dense-cloud points within r=2mm of p. Smooth face reads ~0; a fracture crease reads tens of deg. Decision line: control passes iff BOTH lines' median S >= baseline+15 deg, baseline = median S on face-interior cloud points (>6mm from any lane dot); else report BLIND.

**Control: PASS.** Control stretch ours-Bl0 idx 20-45 (max dist to author 0.917mm, lanes coincide): ours med 41.6 deg (n=26), author-Bl1-nearest med 41.5 deg (n=25); baseline 1.3 deg (n=273). Both lines read crease, instrument is not blind.

**Disputed stretch.** 27 ours-Bl0 dots >2mm from nearer author lane (idx 0-13, excursion to 17.7mm; idx 52-64, to 17.3mm; slots fB0<->oB1 swapped per 209 pattern, re-verified EXACT: med 0.83/cov 58.5). Sharpness there: ours med 39.2 deg (n=27, at control level, continuous crease along the whole lane, per-dot 20.3-50.4) vs nearest author dots med 1.4 deg (n=8 unique, at baseline = smooth surface). Author lane locally leaves the edge and crosses the face; ours stays on the crease.

**Picture (eye-checked by worker).** .scratch/pota229/p229_profile.png: top = S along ours-Bl0 arc (blue stays high throughout; gold collapses to baseline in both shaded disputed ends, coincides in control); bottom = plan-view map (blue rides the cloud boundary/rim, gold cuts mid-face). Scheme gold/blue/black only.

**Mesh provenance.** No full-res triangulated P27 mesh beyond _DS exists on Spartan (searched whole project tree; every P27 Mesh.obj is byte-identical to temp_download _DS). Canonical mesh = pota227_edgeP27_12/Temp/Data/Pot_D/Pot_D_Piece_27_Mesh.obj, 5404 verts / 10804 faces, md5 9d83b39feaf19485c68770fa5876e0eb. Measurement run at ORIG sampled density on the dense cloud sfs-potD-214/Dataset_Input/Point/Pot_D/Pot_D_Piece_27_Point.pcd (83374 pts with normals, md5 c3b1bb6975184a29de9d134500e2ba25); both fetched to artifacts/pota229/ (gitignored).

**Script + numbers.** .scratch/pota229/p229_sharpness.py (numpy+matplotlib only; login-node/python equivalent, no sbatch, no clusters), .scratch/pota229/p229_numbers.csv (baseline,ctrl_ours,ctrl_auth,line,ctrl_pass,disputed_ours,disputed_auth), .scratch/pota229/p229_profile.csv (per-dot idx,arc,dist,S_ours,S_auth).

**What this changes.** Ruler caveat only: the P27@12 excursion follows a real crease (author locally wrong), but the lane bar is unchanged -- cov still counts the whole lane, so P27@12 stays below bar on coverage. No rule, no reseat, no assembly change.


**Evidence-path note (2026-10-23):** paths under .scratch/pota1xx_repro/ and .scratch/pota22x/ cited above were removed by the scratch cleanup of this date (untracked intermediates; not recoverable). The numbers, quotes and verdicts in this ticket stand as recorded -- do not chase those paths or re-derive from them.
