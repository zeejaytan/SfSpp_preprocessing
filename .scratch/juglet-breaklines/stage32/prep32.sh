#!/usr/bin/env bash
# ticket 32: write the run directory's run.json.  Runs ON Spartan, before submit32.sh.
# usage: prep32.sh <rundir> <runid> <sha> <tag>
set -uo pipefail
RUN=$1
RUNID=$2
SHA=$3
TAG=$4
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DS=$CANON/Dataset
DUMP=/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0637_66c84dc_t30-clouds/out/dump
if [ -e "$RUN/run.json" ]; then echo "[PREP] FATAL $RUN/run.json already exists"; exit 3; fi
"$PY" - "$RUN" "$RUNID" "$SHA" "$TAG" "$DS" "$CORP" "$DUMP" <<'PYEOF'
import json, os, sys
run, runid, sha, tag, ds, corp, dump = sys.argv[1:8]
rec = {
    "ticket": "32-how-big-is-a-sherd-next-to-its-pot",
    "question": "U19",
    "runid": runid,
    "runs_root": "/data/gpfs/projects/punim2657/SfSpp/runs",
    "commit": sha,
    "index_tag": tag,
    "job": "submit.sbatch",
    "jobid": "pending",
    "instrument": "stage32 (partA32.py sizes/area/vessel, partB32.py fixed-window "
                   "curvature and neighbour-normal angle, partD32.py ticket-28 growth "
                   "replica with the floor sweep, table32.py, figure32.py, selftest32.py, "
                   "io32.py); reuses analyse30.quadric_radii arithmetic, "
                   "replica29.pair_angles, analyse30.mesh_floor, replica234.grow",
    "instrument_commit": sha,
    "parameters": {
        "windows_mm": [1.0, 2.0, 3.0, 5.0],
        "arms": ["J (nine Juglet clouds from Dataset/Point/Juglet, native)",
                 "PA_native (released Pot A clouds)", "PA_025 (same, 0.25 mm voxel subsample)"],
        "n_centres_max": 8000,
        "neighbour_cap": 40000,
        "angle_step_deg": 0.005,
        "rho_cap_mm": 10000.0,
        "min_fit_neighbours": 6,
        "voxel_cell_mm": 0.25,
        "growth_theta_deg": 3.4,
        "growth_kappa": 1.0,
        "growth_nb": 10,
        "floors_points": [50, 40, 30, 20, 10],
        "coverage_radius_mm": 2.0,
        "seed": 32,
    },
    "inputs": {
        "dataset_root": ds,
        "corpus_root": corp,
        "rung2_dump_root": dump,
        "note": "staged by reference, nothing copied; every file md5 is in "
                "out/inputs_before.md5 and out/corpus_before.txt",
    },
    "writes": ["out/", "logs/", "submit.sbatch"],
    "geometry_deleted": "out/geom (the eight 0.25 mm subsampled Pot A clouds), recorded in "
                        "out/GEOMETRY_DELETED.txt before the delete",
    "read_only": [ds, corp, dump,
                  "/data/gpfs/projects/punim2657/sfs_preprocessing (fetch only)",
                  "/opt/sfs-pristine (recorded, not created)"],
}
p = os.path.join(run, "run.json")
with open(p, "w") as f:
    json.dump(rec, f, indent=2, sort_keys=False)
    f.write("\n")
print("[PREP] wrote", p, os.path.getsize(p), "bytes")
PYEOF
