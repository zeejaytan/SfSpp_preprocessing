# 276 — Does the cluster merge do the job Appendix A gives it?

Answers: E1
Status: ready-for-agent (dispatch HELD behind 275 — user: test this only if the walker work does not settle it)
Working in: C:/PR/worktrees/sfs/276 + Spartan runs/ directory; main source read-only
Needs-eye: no

## Why

The paper gives cluster merging one job: repair over-segmentation. Appendix A
(C:/PR/papers/text/sfspp-2502.13986v1.md:462-479, TABLE I at :464-473) opens with
"a single continuous surface may become over-segmented into multiple clusters".

Our port is faithful in structure — mergePaper234 (mesh_processing_headless.cpp:1929-1984)
with tryMergePair234 (:1864-1927) implements Alg. 1 Step 1 (boundary pairs within rhoD,
at least 3), Step 2 (k2-average normals + curvature, rhoN/rhoC), Step 3 (internal median
point, rhoInN/rhoInC) and loops to a fixpoint (:1942-1983). It prints the paper's own
parameters, so the settings are the paper's.

What it has almost never done on our data is merge:

| piece | clusters before | after | merges fired | source |
|---|---|---|---|---|
| Pot C 01 | 9 | 9 | 0 (one pass) | mesh_Pot_C_01.log |
| Pot J 01 | 7 | 6 | 1 (162 into 332) | mesh_Pot_J_01.log |
| Pot D P03 | 9 | 9 | 0 | ticket 270 |

And the top two clusters saturate at 77.5% on Pot C 01 (face0 56833 + face1 49245 of
~136880 points), so the remaining seven clusters are never joined to anything at all.

Two readings are possible and nobody has tested which is true:

1. The remainder are genuinely separate material — detached lumps, a base fragment,
   the break face — which the merge is right to leave alone, and the merge is healthy.
2. The remainder are pieces of one continuous surface — exactly the case Appendix A
   exists for — and the merge is failing to do its paper job on them.

This is a different question from the one behind tickets 273 and 275. There, the merge
could not help: it joins mesh clusters, while the walk eats boundary-dot lumps. Here we
ask whether the mesh stage is repairing its own segmentation at all.

## The question

Does mergePaper234 join the clusters Appendix A says belong to the same continuous
surface, and keep apart the ones it says do not?

## Phase 0b (added by the lead, 2026-10-24) — where does the missing 22.5% go?

Read-only, needs no build, and it should run before the phases below.

The mesh logs record that the two classified surfaces hold only 77.49% of the cloud on
Pot C 01 ("Points in two clusters / Total Points in pointcloud: 77.4892%", face0 56833 +
face1 49245 of ~136880). The other 22.5% never enters a surface, and the edge stage only
ever sees the surfaces. Nothing downstream can see what was dropped.

Hypothesis, to verify: part of every "real unreached arc" the edge stage shows is not
missing because of the walk but because it never became surface. Candidates, all
single-lump bags with no debris to blame: Pot H 02 Bl1 (73.2% ours / 74.5% author-side),
Pot H 10 Bl1 (68.8 / 76.1), Pot C C03 Bl1 (47.6 / 47.5).

Test, on those three pieces:
1. From the mesh run's own cloud, label every point by post-merge cluster and by final
   surface (Surface_0 / Surface_1 / neither).
2. Map every dot of the author's Breakline_*.pcd for that piece to its nearest mesh point
   and record that point's label.
3. Report, per piece and per lane, the share of author dots landing on a dropped cluster,
   and whether that share matches the uncovered stretch. Report every dropped cluster's
   size and its author-dot count.

Verdict rule: if the uncovered stretch is dominated by author dots whose nearest mesh
point is in a dropped cluster, the missing arc is a mesh-stage loss and the merge is the
suspect. If those dots land on Surface_0/1 points the walk never reached, the loss is at
the edge stage after all and this ticket's answer is "merge innocent, extent family".

## Phase 1 — positive control by deliberate over-segmentation

Nobody has ever handed this code a case where merging is the right answer.

Take one piece whose top-two classification is stable (Pot C 01; Pot D P03 at
theta = 3.4 as the control). Split its single largest cluster in two by position (a plane
through that cluster's centroid), keep every other cluster unchanged, and hand the
result to mergePaper234.

- PASS: the two halves are merged back, the cluster count returns to the unsplit value,
  and the small clusters keep the decisions they had in the unsplit run.
- FAIL: the halves are not rejoined, or a pair rejected before is now accepted.

The cut is through a connected cloud, so the halves are guaranteed to have boundary
points within 1 mm of each other and the "at least 3 pairs" test is satisfiable by
construction. A FAIL therefore isolates the normal/curvature tests as the blocker.

## Phase 2 — which criterion rejects, per real pair

Instrument tryMergePair234 to print, for every cluster pair, one of
`pairs<3 | rhoN | rhoC | rhoInN | rhoInC | accepted` with the measured value and the
threshold, in Appendix A's own vocabulary.

Pieces: Pot C 01, Pot J 01, Pot D P03 (theta = 3.4 sheets), plus Pot H P01 and P02 from
the rollout misses.

Deliver the rejected-pair table and, for each piece, how many clusters are larger than
say 5% of the largest. State plainly whether the dominant rejection is "fewer than 3
boundary pairs" (clusters genuinely far apart, merge innocent), a normal test, or a
curvature test.

## Phase 3 — audit our reading of Appendix A (read, do not tune)

Three places the code goes beyond what the paper spells out. For each, say defensible or
divergence, with line numbers:

1. **Aggregate vs per-pair normals.** tryMergePair234 averages the k2-neighbour normal
   over ALL boundary pairs first, then compares the two cluster-level means
   (mesh_processing_headless.cpp:1903-1914). The paper says "for each boundary point, an
   average normal is computed using k2 neighbors"
   (C:/PR/papers/text/sfspp-2502.13986v1.md:477) — per-pair is the natural reading.
   Aggregation hides per-pair mismatches, so our version merges MORE readily, not less.
2. **Units.** rhoD = 1.0 is compared against a squared point distance in cloud units
   (:1888). State the cloud's units and what 1.0 means physically here (mm).
3. **Pair enumeration.** The 200-pair cap (:1884) and taking only the single nearest
   partner per point of the smaller boundary set (:1887).

## Acceptance

1. Phase 1 is a PASS/FAIL with the cluster counts and the exact log lines.
2. The Phase 2 table covers 5 pieces and attributes every rejected pair to one
   Appendix A criterion.
3. Phase 3 answers the three readings with the paper's line numbers.
4. A one-paragraph verdict: is the merge doing its paper job on this data — yes / no /
   cannot tell — and which single measurement decides it.
5. If it is broken, propose the smallest change and its expected effect. Do NOT
   implement the change in this ticket.

## Boundaries

- Mesh stage only: mesh_processing_headless.cpp and the mesh logs. Do not touch
  edgeline_extraction_headless.cpp — ticket 275 owns that file.
- New instrumentation sits behind one env switch (e.g. SFS_MERGE_DIAG=1) and must be
  inert when unset: the six guard lanes of ticket 271 must reproduce bit-identically.
- Do not change rhoD / rhoN / rhoC / rhoInN / rhoInC defaults in this ticket.
- Run directory under /data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/
  with one index row; verdict and human_note left empty.
- One writer inside .scratch/ at a time: dispatch only once 275's worker has finished.

## Required evidence to report

- cluster counts before and after per piece, quoted from the logs
- the rejected-pair table
- the Phase 1 log excerpt showing the split halves merged or not
- binary md5, cloud md5, and the thetaDeg value printed by each run
