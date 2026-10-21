Status: ready-for-agent

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
