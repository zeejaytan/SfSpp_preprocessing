#!/usr/bin/env bash
# ticket 32 fixup: write the run directory's run.json.  Runs ON Spartan, before submitFIX32.sh.
# usage: prepFIX32.sh <rundir> <runid> <sha> <tag> <srcrunid>
set -uo pipefail
RUN=$1
RUNID=$2
SHA=$3
TAG=$4
SRCRUNID=$5
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DS=$CANON/Dataset
if [ -e "$RUN/run.json" ]; then echo "[PREP] FATAL $RUN/run.json already exists"; exit 3; fi
"$PY" - "$RUN" "$RUNID" "$SHA" "$TAG" "$DS" "$CORP" "$SRCRUNID" <<'PYEOF'
import json, os, sys
run, runid, sha, tag, ds, corp, srcrunid = sys.argv[1:8]
rec = {
    "ticket": "32-how-big-is-a-sherd-next-to-its-pot",
    "question": "U19",
    "runid": runid,
    "runs_root": "/data/gpfs/projects/punim2657/SfSpp/runs",
    "commit": sha,
    "index_tag": tag,
    "job": "submit.sbatch",
    "jobid": "pending",
    "fixup_of": {
        "source_runid": srcrunid,
        "source_dir": "/data/gpfs/projects/punim2657/SfSpp/runs/" + srcrunid,
        "why": "the grid run left one phase-A cell unwritten, A|VESSEL|PotA: its recorded "
               "graph md5 built 'PotA_simple_graph.txt' while the corpus file is "
               "'Pot_A_simple_graph.txt' (the placement itself read the right name at "
               "partA32.py:199). One string in the record, changed to 'Pot_A' for PotA.",
        "what_is_recomputed": ["A|VESSEL|PotA (the whole cell, from the corpus)"],
        "what_is_copied": "the grid's 70 out/cells/*.json, byte for byte, md5 lists compared "
                          "in out/CELLS-COPIED.txt",
        "what_is_regenerated": ["out/sizes32.tsv", "out/windows32.tsv", "out/vessel32.tsv",
                                "out/figure32.png"],
        "superseded": "the source run's sizes32.tsv, windows32.tsv, vessel32.tsv and "
                      "figure32.png lack the Pot A vessel extent and therefore the Pot A "
                      "ratio; their md5s are in out/SUPERSEDED.md5",
    },
    "instrument": "stage32 partA32.py (vessel arm only), table32.py, figure32.py, io32.py",
    "instrument_commit": sha,
    "parameters": {
        "windows_mm": [1.0, 2.0, 3.0, 5.0],
        "arms": ["J", "PA_native", "PA_025"],
        "n_centres_max": 8000,
        "neighbour_cap": 40000,
        "angle_step_deg": 0.005,
        "rho_cap_mm": 10000.0,
        "min_fit_neighbours": 6,
        "voxel_cell_mm": 0.25,
        "seed": 32,
        "note": "the full parameter block is in the source run's run.json",
    },
    "inputs": {
        "dataset_root": ds,
        "corpus_root": corp,
        "note": "read-only; every file md5 is in out/inputs_before.md5 and out/corpus_before.txt",
    },
    "writes": ["out/", "logs/", "submit.sbatch"],
    "geometry_deleted": "nothing: this job writes no geometry and deletes none",
    "read_only": [ds, corp,
                  "/data/gpfs/projects/punim2657/sfs_preprocessing (fetch only)",
                  "/opt/sfs-pristine (recorded, not created)"],
}
p = os.path.join(run, "run.json")
with open(p, "w") as f:
    json.dump(rec, f, indent=2, sort_keys=False)
    f.write("\n")
print("[PREP] wrote", p, os.path.getsize(p), "bytes")
PYEOF
