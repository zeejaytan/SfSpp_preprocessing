# 47 — rebuild the nine Juglet input clouds with the corpus converter

## What to build

The Juglet stops being the exception. Its nine input clouds become **corpus-conforming samples**,
produced by the same converter, the same switches and the same freeze discipline as the 143 released
pieces: `cc_mesh_to_pcd.sh` (README step 1 — CloudCompare samples up to 1 000 000 points on the mesh
faces, octree normals at 0.5, MST orientation, SOR noise filter; ASCII PCD with normals). The new clouds
are installed at the canonical `Dataset/Point/Juglet/` on Spartan — where every ticket branch and every
run stages its inputs from — so the whole workspace uses the same files, not a copy inside a run
directory. The 2026-09-25 vertex dumps they replace are **archived with a manifest, not deleted
silently**.

Why: `docs/notes/2026-10-31-juglet-cloud-provenance.md` — those dumps carry 2 094-24 294 points where
the corpus carries ~840 000-1 000 000, and the first measurement that read the input's own layout
(ticket 45's fold radius) was wrong by exactly that factor. This ticket touches **no pipeline source**.

**Answers:** U19

**Blocked by:** None (can start immediately).

**Status:** done
**Working in:** chat on Thinkbook16 (2026-10-31)
**Branch:** 47-rebuild-the-juglet-input-clouds-with-the-corpus-converter, in /c/PR/worktrees/sfs/47

**Worker:** lead - worker died mid-patch; lead finished the gate fix, rerun, verification and write-back (2026-10-31)

## The method, exactly

- Input meshes: `$CANON/Dataset/Mesh/Juglet/Juglet_Piece_N_Mesh.obj` — the **mm** meshes. The raw
  `Dataset/Juglet/PieceNN.obj` scans are inches (x50.8); never feed those.
- Command per piece, on a compute node via `sbatch` (the script loads GCC/11.3.0 OpenMPI/4.1.4
  CloudCompare/2.12.4 itself, offscreen Qt):
  `bash cc_mesh_to_pcd.sh -i <mesh> -o <staging dir>` — defaults only (1 000 000 points, medium SOR).
- Output naming must land exactly `Juglet_Piece_N_Point.pcd` — the name every stager and gate greps for.
- **Frame gate before install:** `-GLOBAL_SHIFT AUTO` must have shifted nothing (Juglet coordinates
  ~700 mm; Pot A at ~1e4 was left unshifted). Verify the first rows of each cloud against the mesh's
  own vertices and against the `Dataset/Juglet_GT` frame. A shifted cloud seats nothing downstream.
- Density gate: point count in the corpus range (the script itself refuses < 10 000; expect
  ~1 000 000 sampled, SOR keeping roughly 84 % as on Pot A 01: 1 000 088 -> 843 433); normals present
  in the header.
- **Freeze the draw:** the sampler is unseeded — one draw per piece, md5 + point count + `_cc.log`
  recorded in a `MANIFEST_JUGLET_CC.tsv` beside the clouds (the `MANIFEST_released.tsv` style). A
  rebuild is a different cloud and a corpus change, never a silent refresh.
- Install at `$CANON/Dataset/Point/Juglet/`; archive the nine vertex dumps to
  `/data/gpfs/projects/punim2657/SfSpp/attic/<dated dir>/` with a manifest-path-size list (rule 13:
  nothing is deleted without a record — moved with one, proved by reading it back).

## Known gaps in the converter — recorded here, NOT fixed in this ticket

`MAX_REMOVAL_PERCENT` is declared but never enforced, and the draw is unseeded (three Pot A 01 draws
spread 843 433 / 843 282 / 843 252, ticket 289). The corpus converter stays byte-frozen; changing it
is a separate decision with its own ticket.

## Acceptance

- [x] 9 of 9 clouds produced by `cc_mesh_to_pcd.sh` unmodified, defaults only; `_cc.log` beside each. install_verify 9/9 install-ok; converter byte-frozen from the pushed commit; run 20261031-1303_147b121_t47-jugletcc2.
- [x] Frame gate recorded per piece: first rows vs mesh vertices vs GT frame; no global shift applied. Gates 9/9: extent_delta 0.002-0.025 mm, first3 0.074-0.337 mm, center vs AREA-weighted centroid 0.007-0.021 mm, maxabs 512-552 mm both sides (GT frame, no shift).
- [x] `MANIFEST_JUGLET_CC.tsv` committed beside the record note (docs/notes/MANIFEST_JUGLET_CC.tsv); the draw is frozen. Lead re-checked: md5 col 6 matches installed bytes 9/9.
- [x] Vertex dumps archived: attic/20261031-juglet-vertex-dumps (9 pcd + manifest.tsv), readback-ok 9/9. Nothing else under `Dataset/` changed: corpus_confined clean, find -newermt 2026-10-31 12:00 over Mesh/Juglet, Axes/Juglet, Juglet_GT returns nothing.
- [x] Before/after figure for J2 staged: SfSpp_preprocessing/artifacts/t47-jugletcc2/j2_before_after.png (2,565 pts -> 841,310 pts; 5.22 -> ~12.35 pts/mm^2). Lead's machine eye was down (no image input on this model; vision bridge 503) — the conservator's eye on this figure is the instrument of record.
- [x] Run dir 20261031-1303_147b121_t47-jugletcc2 (run.json, submit.sbatch, logs, out); index row appended by the job with empty verdict, lead wrote PASS with note (backup .bak-t47pass). sacct COMPLETED 0:0, 00:05:42, job 34095579 (poll recorded below).
- [x] Lead re-verified frame gate (gates47.tsv + independent md5sum over installed bytes) and the manifest; AGENTS.md caveat and provenance note updated with the regeneration date in this commit.

**Needs-eye:** the before/after cloud figure (J2 minimum) — staged at SfSpp_preprocessing/artifacts/t47-jugletcc2/j2_before_after.png.

## Comments

### Results — run of record 20261031-1303_147b121_t47-jugletcc2 (lead, 2026-10-31)

- **Job 34095579**, sapphire, sacct **COMPLETED 0:0**, 00:05:42; polled via slurm_poll.sh; run built from pushed commit 147b121 (git archive of origin/branch-47).
- **Gates 9/9**: frame gate vs area-weighted mesh centroid 0.007-0.021 mm; extent (bbox-vs-bbox) 0.002-0.025 mm; first-3 rows on mesh vertices 0.074-0.337 mm; maxabs 512-552 mm both sides = GT frame, no global shift; density 9/9 (~1.0 M sampled, kept 840 666-841 413, ratio 0.8405-0.8417 vs Pot A 0.843); normals present all 9.
- **Install 9/9 install-ok; attic readback 9/9 readback-ok.** Nine new clouds at Dataset/Point/Juglet (49.8-50.5 MB, ASCII PCD, 6 fields incl normals) + 9 _cc.log + MANIFEST_JUGLET_CC.tsv. Old Sep-25 vertex dumps (2 094-24 294 pts) archived at SfSpp/attic/20261031-juglet-vertex-dumps with manifest.
- **Lead re-verification (independent of the job's own gates):** manifest col-6 md5 vs md5sum of installed bytes 9/9 OK; POINTS headers 840 666-841 413; Mesh/Axes/Juglet_GT untouched (find -newermt empty); index row verdict pass written with full note.
- **verified: ssh_exec md5sum loop over MANIFEST_JUGLET_CC.tsv -> 9/9 OK, md5-gate-fail=0; gates47.tsv cols 12-14/17-18 -> all pass; sacct -j 34095579 -> COMPLETED 0:0 00:05:42.**

### History of this ticket's three attempts

1. 20261031-0346_a51819f: pre-submit submit-gates killed it (no run dir) — the hardening was the point.
2. 20261031-0352_4a4b39b, job 34080350: sacct FAILED 8:0. Gates 6/9 — frame gate failed J1/J3/J5 on center_delta alone (2.4-3.8 mm vs 2.0 bar) while every other frame metric agreed to <=0.36 mm. **Defect: gate compared cloud point-mean centroid vs mesh BBOX centre — different kinds of centres.** Lead probe (/tmp/areaprobe.py, run-2 staging clouds): point-mean vs area-weighted centroid 0.003-0.025 mm on all nine — the clouds were right, the gate's reference was wrong. Index verdict void; corpus untouched by design (fail-before-install).
3. Fix 147b121: gates47.py reference -> mesh_area_centroid (mesh_area-weighted), provenance probe files kept in stage47/. Resubmitted as the run of record above.

Worker died mid-patch; lead completed the patch, resubmission, verification and this write-back (2026-10-31).
