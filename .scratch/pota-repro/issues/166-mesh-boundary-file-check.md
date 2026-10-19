# Mesh-boundary file check: do FAR dots sit on real mesh boundary edges?

GOAL: SETTLE ON THE FILE WHAT THE RENDER LIED ABOUT.

**Answers:** E1

**Blocked by:** 165 CORRECTION (translucent render faked a hole; mesh solid+whole; blue-loop identity open) + 163 (substrate) + 155 (code sites).

**Status:** results-in

**What to deliver:** (a) On the actual C01 mesh FILE (not a render): is it watertight? Enumerate real boundary-edge loops (open edges) with counts; do the 4 blue loops from 165 exist on the file, and where are they (fracture rims? interior?). (b) Distance from each of the 91 FAR + 86 NEAR veto dots to the nearest real mesh boundary edge -- do FAR dots coincide with mesh boundaries (data-gap rims) or sit mid-surface? (c) Re-render the false-loop region OPAQUE (no translucency) with dots + ORIG + real boundary loops, eye-checked.

**Starting position:** 165 Comments (blue-loop tracing method, dot sets, mesh path); 162/164 Comments (labels). New scratch pota166_repro/; renders artifacts/pota166/.

**Rules:** read-only over tickets 39-165; render-only + file inspection (login-node/mesh tools; laptop-side if fetchable); COMMIT NOTHING; Comments-only ticket edits; OPAQUE renders only; sacct if Slurm used; eye-check renders.

- [ ] watertight verdict + real boundary loops enumerated on the file
- [ ] FAR/NEAR distance-to-mesh-boundary numbers
- [ ] opaque re-render, eye-checked
## Comments

### Lead follow-up 2026-10-20 (Spartan reachable via Windows ssh agent)
Full-res check closed as un-runnable: no full-resolution Pot C mesh exists anywhere on the cluster -- only the same `_DS` files under `temp_download/Mesh/Pot_C/` (Nov 2025). Laptop and cluster `Pot_C_Piece_01_Mesh_DS.obj` are byte-identical (md5 a0a34170). So the hole + flake + crumb are in the source data as received, not a decimation artifact of ours. SSH route for this session: `C:\Windows\System32\OpenSSH\ssh.exe` (Windows agent holds `spartan-laptop-key`); MSYS2 ssh cannot sign (passphrase-locked key, no agent). (worker, 2026-10-20 -- file verdict + opaque renders)

VERDICT on "do FAR dots sit on real mesh boundary edges": NO as a class, PARTLY as a ring subset -- and none of the 4 loops is the fracture rim. Numbers are point-to-SEGMENT distances on the FILE (gate frame), not render estimates.

### (a) Watertight verdict + boundary loops on the file

Mesh temp_download/Mesh/Pot_C/Pot_C_Piece_01_Mesh_DS.obj (11875 verts/23114 faces, asserted): NOT watertight. Edge-use census over 34989 edges: 636 used once (boundary), 34353 twice, ZERO non-manifold (3+). All 636 boundary verts degree 2; traced into 4 CLOSED loops, sizes 274/247/97/18 -- reproduces 165 exactly.

Component analysis (face connectivity): 3 components, so the 4 loops are NOT 4 holes in one sheet:
- MAIN sheet 11263v/22186f carries loop1 (247e, perim 102mm, centroid [23.0,54.5,36.4]) + loop2 (97e, perim 44.6mm, centroid [36.9,87.3,82.2]).
- FLAKE 592v/908f (disk, ~25mm patch, gate bbox x[15.3,39.5] y[58.1,69.7] z[19.9,55.1]) carries loop0 (274e, perim 117.7mm) as its OWN outer rim; it hovers 3.65mm (min) / 4.17mm (med) off the main sheet beside the hole.
- CRUMB 20v/20f (2mm sliver near [13.2,56.7,25.0]) carries loop3 (18e, perim 5.4mm); floats 1.1mm off sheet.

Loop identities (centroid-to-sheet + min/median distance to ORIG G=Bl_0+Bl_1):
- loop1 = HOLE in main sheet at the false-loop site (centroid 10.8mm off-sheet = air, mean radius 12.8mm; minORIG 36.2). Interior scan hole, NOT fracture rim.
- loop2 = second hole/slot in main sheet at far corner (centroid 2.9mm off-sheet; minORIG 70.8). Zero veto dots near it (nearest-loop count 0 in all groups).
- loop0 = flake rim (NOT a hole -- 165's "two big loops sit at the ring" misread it; the flake covers the hole from the scan side, which is why translucency showed two concentric blue rings).
- loop3 = crumb rim (centroid on-sheet 0.16mm; pinhole-scale).
- NONE of the 4 loops is the piece's fracture rim: ORIG rides the mesh surface (ORIG-to-vertex med 0.51mm) but every loop is >=36mm from ORIG at its closest vertex. The DS mesh extends well beyond the fracture rim; 165's "air beyond the edge" at the rim site was sheet curving edge-on (fold), not mesh end. Rim panels confirm: ORIG + NEAR dots run along a fold in continuous sheet with mesh on both sides and no blue loop within 35mm.

### (b) FAR/NEAR distance to nearest real mesh boundary edge (point-to-segment, gate frame)

- FAR n=91: min 0.04 / p10 0.28 / p25 0.87 / MED 7.42 / p75 14.61 / p90 16.82 / max 69.39; frac <1mm 0.286, <2mm 0.374, <5mm 0.495. Nearest-loop: 73 loop1-hole (med 3.21), 14 loop3-crumb (med 12.90), 4 loop0-flake (med 14.65), 0 loop2. So ~1/3 of FAR dots hug the hole rim (<1-2mm), half sit in the hole neighbourhood (<5mm), the rest are interior dots up to 69mm from any boundary. The veto FAR loop parallels/rings the hole; it does NOT coincide with mesh boundary edges as a class.
- NEAR n=86: min 34.55 / p10 39.49 / MED 54.38 / max 82.17; ZERO below 5mm. Decisively NOT on any mesh boundary -- on-ORIG rim dots sit mid-sheet, tens of mm from every loop.
- MID n=187 for context: MED 49.78, same picture as NEAR.
- FAR dots are NOT on the flake either (FAR-to-flake min 7.40 / med 12.78); they ride the main sheet around the hole.

### (c) Opaque re-renders (artifacts/pota166/, eye-checked)

- artifacts/pota166/p166_overview.png -- full mesh opaque, all 364 dots + ORIG + 4 blue loops + site boxes (no cull)
- artifacts/pota166/p166_falseloop_1_e5_a-120.png -- hole-centred, red ring + blue rim bits + ORIG wall arcs (kept MID 0 / NEAR 2 / FAR 43)
- artifacts/pota166/p166_falseloop_2_e10_a-105.png -- second angle (2/8/39)
- artifacts/pota166/p166_falseloop_3_e30_a-120.png -- from above (15/8/19)
- artifacts/pota166/p166_rim_1_e10_a180.png -- ORIG pair + green NEAR on the fold, 0 FAR (38/14/0)
- artifacts/pota166/p166_rim_2_e10_a150.png -- (32/13/0)
- artifacts/pota166/p166_rim_3_e35_a165.png -- from above (23/4/0)
- artifacts/pota166/p166_frame.txt -- frame/provenance note
- diag_hole_all.png / diag_hole_mainonly.png -- method diagnostics (mplot3d buries 3D scatter under opaque mesh regardless of zorder; main-only view proves the hole is open in the main sheet with far-wall interior visible through it)
- Method: mesh alpha=1.0 everywhere (zero translucency); overlays are exact 2D pins (proj_transform + ax.transData chain, pixel-exact by construction) with per-camera opaque-visibility cull (tol 1.5mm behind front surface, pixel disc 2.5mm; through-hole/past-edge kept); cameras sweep-maximised for loop visibility; light identical all panels. Scripts: .scratch/pota166_repro/p166_filecheck.py (census+loops+distances), p166_locate.py, p166_comp.py, p166_flake.py, p166_camsweep.py, p166_diag.py, p166_render.py (final PIL-composited) + p166_numbers.npz.

Worker's read (eye + file agree): on OPAQUE mesh the red ring still circles a real opening -- dark bowl interior with lit far wall, no white-through-hole fakery; the surround sheet is smooth with no crease under the ring; the flake overlapping the hole explains the double blue ring. At the rim, ORIG + green dots ride a rounded fold in continuous sheet -- sharper-looking than the hole site yet itself crease-free, and boundary-free for >=35mm around.

Heads-up for the lead: (1) 165's Comments stay valid except two corrections: loop0 is a flake rim, not a second hole rim; the rim-site "air beyond the edge" is fold, not mesh end. (2) Hole-vs-decimation still open -- only DS meshes exist laptop-side (temp_download/Mesh/Pot_C/*_DS.obj); confirming the hole pre-dates decimation needs the full-res mesh (Spartan-side). (3) No Slurm used -- nothing for sacct (all laptop-side, system python numpy+matplotlib+scipy+PIL, no env change). COMMITTED NOTHING; tickets 39-165 untouched (read-only).

- [x] watertight verdict + real boundary loops enumerated on the file
- [x] FAR/NEAR distance-to-mesh-boundary numbers
- [x] opaque re-render, eye-checked

