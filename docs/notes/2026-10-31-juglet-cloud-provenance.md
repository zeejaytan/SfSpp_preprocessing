# 2026-10-31 — The Juglet input clouds: the corpus step was skipped, a vertex copier ran instead

Recorded the day the cause was found. The conservator asked why the Juglet clouds had not been
built the README way; the answer is that the README's step 1 was never run on the Juglet at all.
This note is the evidence, so the failure is not remembered as "the sampler was unlucky".

## What the step is supposed to be

README.md step 1 (upstream authors' text): sample the .obj with CloudCompare, up to 1,000,000
points, apply initial noise filtering, output a PCD cloud. The workspace implementation is
cc_mesh_to_pcd.sh (repo root; committed 2026-07-19 b5404fe from untracked scripts that predate
the commit). One run:

- module load GCC/11.3.0 OpenMPI/4.1.4 CloudCompare/2.12.4, offscreen Qt
- -SAMPLE_MESH POINTS 1000000 — points spread over the mesh FACES
- -OCTREE_NORMALS 0.5 then -ORIENT_NORMS_MST 6 — PCA normals, MST orientation
- -SOR 6 1.0 — noise filter
- ASCII PCD x y z normal_x normal_y normal_z; refuses under 10,000 points

This is not a reconstruction of the method from the README — it is the tool that built the
corpus. Dataset/Point/Pot_A/Pot_A_Piece_01_cc.log (2025-11-22 04:15:49) is this script's own
log and shows the chain live: mesh loaded with 100,064 vertices / 200,124 faces, cloud sampled
at 1,000,088 points, SOR leaves 843,433. Every released pot cloud has its _cc.log beside it.
The corpus-freeze tickets (276, 284, 289, 290, 292, 298) pinned this as the corpus standard:
each of the 143 released pieces carries one unseeded CloudCompare draw.

## What actually ran on the Juglet

All nine Dataset/Point/Juglet/*_Point.pcd were written 2026-09-25 14:35-14:40 in one batch by
original_nurbs_preprocessing/tools/obj_to_pcd.cpp (152 lines, committed 2026-09-26 3095064).
That tool loads the OBJ and writes EVERY mesh vertex as one point (POINTS = numVerts),
computing each normal by averaging the faces around the vertex (the Juglet OBJs carry no vn).
No sampling, no noise filter, no CloudCompare.

## Proof, three independent fingerprints

1. Counts. Cloud points equal mesh vertices exactly: J1 24,294 = 24,294; J2 2,565 = 2,565;
   J9 2,094 = 2,094. A sampled cloud would not land on the vertex count nine times.
2. Order. The first three rows of Juglet_Piece_2_Point.pcd are the OBJ's first three vertices,
   same order, with normals appended.
3. Format. "49.7903 -10.4979 -529.641" is float-cast output at 6 significant digits —
   obj_to_pcd.cpp's static_cast<float> with default ostream precision. The corpus writer
   (python float repr) preserves -529.6408.

No _cc.log exists beside any Juglet cloud; no note or ticket from 2026-09-25 records the
choice; cc_mesh_to_pcd.sh was present in the repo the whole time.

## Why it stayed hidden for a month

Every stage the pipeline runs downsamples its input first, so a sparse cloud and a dense cloud
converge by the first stage: through ticket 42 no measurement could see the difference. The
first reader of input layout was ticket 43's fold radius (30-neighbour patches). On the vertex
dump those patches span the sparse vertex layout — J2 carries 5.22 pts/mm2 against 12.35 for
an even covering — so folds read 2-4x too tight and theta came out 4x too steep (J2 48.56 deg
against 12.40 true; run 20261030-2128_f4a3559_t45-default). Ticket 46
(20261031-0123_a4d72f6_t46-covering4) is the counterproof: same binary, same commit, even
covering in, formula lands within 2 % on 8 of 9 (mean 0.79 %). The method was never wrong; the
input was never the corpus's kind of cloud.

## What is and is not affected

- Affected: any measurement that reads the input cloud's layout (fold radius / R, spacing
  statistics, anything k-NN over raw points) on the Juglet.
- Not affected by itself: downstream stages after the pipeline's own downsampling; the pot
  corpus (built by the right tool); ticket 44's thetas (measured on the mesh, calibrated on
  Pot A).
- The Sep-25 clouds must not be replaced silently: a regeneration is a corpus change (record,
  index row, freeze the unseeded draw per ticket 289's precedent, and check that
  -GLOBAL_SHIFT AUTO leaves the coordinates in the GT frame — Pot A at ~1e4 was left
  unshifted; the Juglet at ~700 mm should be too, but verify against the first rows).

## Failure, named

The step was documented, implemented, and already on Spartan; the staging session wrote a
substitute tool instead and used it, without a ticket, a note, or a comparison against the
README. That is a process failure by us, not a defect in the method or the data. The remedy
ticket (regenerate the nine clouds with cc_mesh_to_pcd.sh) awaits the conservator's go.
