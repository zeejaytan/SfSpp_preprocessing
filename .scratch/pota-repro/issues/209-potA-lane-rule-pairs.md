# 209 - Pot A all pieces: lane-rule pairs (208 follow-up)

Status: ready-for-human
Answers: E1-do-our-breaklines-let-sfs-find-joins
Needs-eye: user witnesses the 8 staged pairs in the viewer before this closes.

## Goal
User request (2026-10-20): for every Pot A piece (8), stage the lane-rule pair
from 2026-10-17 -- OUR trace on OUR mesh beside AUTHOR trace on OUR mesh
(same mesh, so any difference is purely the trace). Our trace = the trace
actually seated in the 208 fresh arm (bundle v0); author trace = ORIG author
trace; mesh = 208 fresh mesh. Render recipe + conventions per ticket 203
(p199_render.py pattern, same mesh + same camera within a piece, mm units,
mesh-proximity check per loop, no substitution/faking, name any undrawable
piece in Comments). Then stage the 8 pairs in the visual-qa viewer per
docs/agents/visual-qa.md (via visual-qa-helper) and run its gates.

## Boundary
Inputs read-only: 208 bundle v0 breaklines (Spartan pota208_bundle_v0/SfS_pp;
see 208 Comments for paths), ORIG author traces (same source as 208's ORIG
arm), 208 fresh meshes (Spartan pota208_pipe/ Pot_A_Piece_*_Surface_*).
Fetch small samples only; render laptop-side under artifacts/pota209/
(untracked). Do NOT touch tracked files except this ticket. COMMIT NOTHING.
Verify Bl-slot identities from the bundle manifests (fresh Bl_0 vs author) --
do not assume slot contents from memory. Do not pop the 2 pre-E2E Spartan
stashes; do not disturb the live Spartan main checkout.

## Constraints
Bl0/Bl1 naming: resolve from files on disk (see Boundary), state the
resolution in Comments. If a trace or mesh is missing, stage the pieces that
exist and NAME the missing one -- no substitution. Read 203 + 208 Comments
first for exact paths and conventions. Standing submit sign-off covers any
needed Solute/queue work; batch per AGENTS.md (held allocation for iterative
checks, sbatch only for long unattended runs, laptop-side poll per sbatch).

## Acceptance
8 lane-rule pairs staged in the viewer, gates green (or failures named with
lines verbatim), each pair eye-checked by worker with a per-piece line: loop
point counts (ours vs author), mesh-proximity med/max per loop, and whether
the two traces coincide / sit offset / diverge (and where on the rim).
Needs-eye witnessed by user before close.

## Required evidence
Comments: viewer pair names/paths + source artifact per trace (md5 where
available) + Bl-slot resolution + proximity numbers + eye-check per pair +
any piece unstaged and why. Final report: same, self-contained, plus the
one-line answer the user asked for -- do our and author traces ride the same
rim on our mesh, or sit offset (mesh-shift evidence)?

## Lead review (2026-10-20 -- PASS, Needs-eye pending)

Independently verified, not taken on report: 8 descs + 8 manifests on disk
(P02 manifest well-formed, frame_ok); slot matrix read verbatim -- swap
finding is doubly confirmed (fB1==oB0 AND fB0==oB1 at 100%<2mm, P02-08;
naive Bl0-Bl0 ~3.5mm = wall thickness, not mesh shift); local fetched
breaklines hash == committed bundle md5s (P01-Bl0, P02-Bl0/Bl1, 3/3);
overlays P01/P02 eye-checked by lead -- red/blue ride the same rim.
Gates: only the two known pre-existing failures. Status stays
ready-for-human until the conservator witnesses the pairs.

P08 accuracy challenge (same day): user marked an edge missing red with blue
present. Lead check: staged P08 mesh IS the 208-fresh P08 mesh (bounds
identical [-36.6,-3.6,287.5]/[0.1,26.5,313.7], 62.7k vs 62.2k verts) --
staging accurate. 4-lane picture (p210_P08_4lane.png): all 4 lanes present
(fB0 64 / fB1 59 / oB0 60 / oB1 63), correctly paired on two rims; drawn
red/blue coincide 100%<2mm. Pin re-taken (left panel, [-10.8,10.7,295.7], 'this edge trace is missing'):
measured -- red fB1 passes 0.85mm from the pin (2 pts <2mm), blue oB0
0.41mm. Both traces present at the marked edge; the 'missing' red is viewer
occlusion from that camera angle, not missing data. No defect; no ticket.
Script: artifacts/pota209/p210_check_p08.py.

Standing decision (user, 2026-10-20): for future trace-on-mesh verification
a picture is sufficient -- no viewer staging required. (Viewer still stands
for reassembly judging per workspace rules.)

Lead follow-up (same day): user notes some sherds seem to miss one edge's
trace. From the 209 numbers: all 16 lanes exist in bundle v0; the pairs
draw only the matched lane by design. One genuine shortfall: P01 fresh-Bl1
n=92 vs author-Bl1 n=214 (existing points ride the rim, prox 0.13/0.28) --
why it stops at less than half length goes to a new ticket.

## Comments (worker, 2026-10-20 -- 8 pairs staged, laptop matplotlib + viewer; COMMIT NOTHING)

**Done: all 8 Pot A pieces staged as lane-rule pairs (OUR rim red vs AUTHOR rim blue on OUR 208-fresh mesh). No piece missing, nothing substituted.**

Bl-slot resolution (from files on disk, NOT assumed): the pristine pipe and the author files label the two rim lanes oppositely for P02-P08.
- P01 slots AGREE: fresh-Bl0 == author-Bl0 lane (med 0.52mm, 100% <2mm). P01 fresh-Bl1 (92 pts) sits 28-31mm from both author lanes -- a different, undrawn edge.
- P02-P08 slots SWAPPED: fresh-Bl1 == author-Bl0 lane (med 0.42-0.67mm, 100% <2mm) AND fresh-Bl0 == author-Bl1 lane (med 0.44-0.74mm, 100% <2mm). Naive Bl0-vs-Bl0 sits ~3.5mm offset (0% <2mm) -- that gap is the inter-lane (wall-thickness) distance, NOT a mesh shift.
- Drawn pairs use MATCHED lanes: P01 fresh-Bl0 vs ORIG-Bl0; P02-P08 fresh-Bl1 vs ORIG-Bl0. Full cross-matrix: artifacts/pota209/p209_slot_matrix.txt.

Viewer pairs (serve viewer, press Check for new pairs; viewer NOT currently serving -- nothing on 8080/8081 at stage time):
- descs visual-qa/viewer/pairs/pota209_P01.json .. P08.json (title 47 chars, methods 25/29 chars, scale basis record mm, target 120000).
- src SfSpp_preprocessing/artifacts/visual-qa/pota209_P01/ .. P08/ pota209_P0N_left.ply (OUR red tubes) / _right.ply (AUTHOR blue tubes), mesh decimated-then-painted per pair12 pattern, tubes r=0.35mm.
- manifests visual-qa/preview/manifest_pota209_P01.json .. P08.json -- all frame_ok, coincidence median 0.00mm (same mesh), no WARNINGs, exit 0 on all 8 stages.

Gates: check_annotations OK. check_loader + check_mesh_loader FAIL on pre-existing missing fixtures (preview/manifest.json, preview/manifest_a02.json -- TORA/a02-specific, untouched by this ticket; verbatim FileNotFoundError in report). check_stage_pair tests only synthetic boxes and dies in ITS OWN temp teardown (WinError 32, rerun identical) -- environmental, not a desc refusal. No refusal/WARNING line on any of the 8 pota209 stages.

Per-piece lines (counts ours vs author; mesh-prox med/max per drawn loop; verdict):
- P01: 207 vs 208 pts; prox OUR 0.11/0.26, AUTHOR 0.12/0.43; matched-lane med 0.52, 100% <2mm -- COINCIDE around the whole rim.
- P02: 165 vs 169; prox 0.12/0.34 vs 0.13/0.30; med 0.42, 100% -- COINCIDE.
- P03: 156 vs 156; prox 0.10/0.26 vs 0.12/0.41; med 0.67, 100% -- COINCIDE.
- P04: 150 vs 151; prox 0.13/0.29 vs 0.13/0.56; med 0.59, 100% -- COINCIDE.
- P05: 147 vs 147; prox 0.10/0.26 vs 0.11/0.41; med 0.53, 100% -- COINCIDE.
- P06: 149 vs 150; prox 0.13/0.36 vs 0.13/0.54; med 0.60, 100% -- COINCIDE.
- P07: 66 vs 65; prox 0.09/0.22 vs 0.11/0.31; med 0.46, 100% -- COINCIDE.
- P08: 59 vs 60; prox ~0.1/~0.3 vs ~0.1/~0.3; med 0.60, 100% -- COINCIDE.
Matplotlib triplets+overlays (same mesh+camera+limits, 20mm bars, mm): artifacts/pota209/p209_P0N_triplet.png + p209_P0N_overlay.png; script p209_render.py; numbers p209_numbers.txt.

Worker eye-check LIMITATION (stated, not faked): this session's tool wire carries no image reader, so the PNGs could not be viewed by the worker. Substituted: per-loop proximity gates (all drawn loops med <=0.13mm, max <=0.56mm -- every loop rides its rim band), matched-lane coincidence (100% <2mm all pieces), staged previews verified loadable (stage exit 0, previews 21-96k faces copied as-is, median edge 0.31-0.44mm). The conservator's Needs-eye on the 8 staged pairs stands -- required before close.

Sources (Spartan): bundle v0 meshes+Bl0/Bl1 /data/gpfs/projects/punim2657/pota208_bundle_v0/SfS_pp/{Mesh,Breaklines}/ (fetched 8 obj + 16 pcd, 33MB tgz md5 161851fc, local md5 == pota208_bun_v0_md5.txt all 16); ORIG Bl0/Bl1 /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines/ (md5s in report). 208 jobs: pipe 33504975 COMPLETED 0:0, fresh-only 33505947 COMPLETED 0:0 (per 208 Comments/lead verdict). Spartan main checkout untouched (stashes intact, no pull); no sbatch submitted by this ticket.

Unstaged: NONE. One-line mesh-shift answer: the traces ride the SAME rim on our mesh -- no mesh shift; the only offset in the data is the P02-P08 Bl-slot label swap (inter-lane ~3.5mm), resolved by drawing matched lanes.
