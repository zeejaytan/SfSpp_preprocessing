#!/usr/bin/env bash
# run ON Spartan.  usage: prepE32.sh <rundir> <runid> <sha> <tag>
# Writes run.json for ticket 32 PART E before anything is submitted, so the parameters the job
# was given exist as a record even if the job never starts.
set -uo pipefail
RUN=${1:?rundir}
RUNID=${2:?runid}
SHA=${3:?sha}
TAG=${4:?tag}
[ -d "$RUN" ] || { echo "[PREP] FATAL no run dir $RUN"; exit 1; }
echo "$SHA" | grep -Eq '^[0-9a-f]{40}$' || { echo "[PREP] FATAL sha is not 40 lowercase hex: $SHA"; exit 1; }
PYBIN=$(command -v python3 || command -v python || true)
[ -n "$PYBIN" ] || { echo "[PREP] FATAL no python on PATH"; exit 1; }
"$PYBIN" - "$RUN/run.json" "$RUN" "$RUNID" "$SHA" "$TAG" <<'PYEOF'
import json, os, sys
dst, rundir, runid, sha, tag = sys.argv[1:6]
runs_root = os.path.dirname(os.path.abspath(rundir))
doc = {
    "ticket": "32-how-big-is-a-sherd-next-to-its-pot",
    "question": "U19",
    "part": "E",
    "runid": runid,
    "runs_root": runs_root,
    "commit": sha,
    "index_tag": tag,
    "job": "submit.sbatch",
    "jobid": "pending",
    "instrument": ("the pipeline itself, built from this commit inside the project's own "
                   "apptainer image, run with ticket 23's spacing/count/floor switches; "
                   "plus stage23's run_cell23.sh, measure_arm23.py, coverage23.py (copied "
                   "verbatim) and stage32's partE32.py (the table)"),
    "parameters": {
        "pieces": ["Juglet_Piece_2", "Juglet_Piece_3", "Juglet_Piece_9"],
        "arms": {
            "plain": "SFS_SPACING_POLICY=piece SFS_SPACING_SAMPLES=200 SFS_COUNT_SCALE=auto SFS_FLOOR_CEILING=<fraction>",
            "single": "the same plus SFS_SINGLE_CLUSTER=write"
        },
        "floors_requested": [0.03, 0.02, 0.01],
        "pot": "Juglet",
        "coverage_radius_mm": 2.0,
        "cells": 18,
        "build": "cmake -DCMAKE_BUILD_TYPE=Release + make -j8 MeshPreprocessingHeadless inside pcl_191_nurbs.sif",
        "why_two_arms": ("ticket 23 measured that a surface is written from a lone cluster only "
                         "with SFS_SINGLE_CLUSTER=write; the lead's switch set omits it, so the "
                         "plain arm is reported as it stands and the single arm supplies the "
                         "coverage and extent measurements, labelled separately")
    },
    "inputs": {
        "canonical_checkout": "/data/gpfs/projects/punim2657/sfs_preprocessing",
        "sif": "/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif",
        "clouds": "Dataset/Point/Juglet/Juglet_Piece_<N>_Point.pcd (mm, pipeline density)",
        "meshes": "Dataset/Mesh/Juglet/Juglet_Piece_<N>_Mesh.obj",
        "axes": "/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0055_d8af9d2_p07-juglet-stage1/out/boot/Juglet_Piece_<N>_boot_Axis.xyz",
        "note": "staged by symlink into each cell's stage dir; inputs.md5 before/after recorded by the job"
    },
    "writes": ["<rundir>/out/partE32.tsv", "<rundir>/out/cells/<tag>/Juglet/<piece>/ (cell.tsv, logs, surfaces)",
               "<rundir>/logs/", "one row appended to the shared index.tsv with empty verdict and human_note"],
    "geometry_deleted": "out/GEOMETRY_DELETED.txt, written before the delete; the build tree and every stage dir go, the surfaces and logs stay",
    "read_only": ["/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp",
                  "/data/gpfs/projects/punim2657/sfs_preprocessing",
                  "/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset"]
}
open(dst, "w").write(json.dumps(doc, indent=2) + "\n")
print("[PREP] wrote %s %d bytes" % (dst, os.path.getsize(dst)))
PYEOF
