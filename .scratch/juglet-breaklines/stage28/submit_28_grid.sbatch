#!/bin/bash
#SBATCH --job-name=__JOBNAME__
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=__TIME__
#SBATCH --output=__RUNDIR__/logs/slurm-%j.out
#SBATCH --error=__RUNDIR__/logs/slurm-%j.err
# ticket 28, job 2 of 2 -- the replica grid.
#
# Nothing here is a pipeline run: the replica reads rung-2 dumps that already
# exist (ticket 25 arms B and E for the four Juglet pieces, and job 1's Pot A 07
# dumps). The calibration gate runs first and the grid does not run at all if it
# fails: theta 3.4, nb 10, kappa 1, floor 50 on arm B must return
# piece 3 [169, 99], piece 5 [679], piece 7 [326, 263, 77, 68, 65].
set -uo pipefail

RUN=__RUNDIR__
RUNID=__RUNID__
NEW=__NEWCOMMIT__
IXTAG=__IXTAG__
POTADUMP=__POTADUMP__
T25=__T25DUMP__
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
CELLS=${RUN}/out/cells
export RUN RUNID NEW IXTAG POTADUMP T25 PY CELLS

cd "${RUN}" || exit 1
mkdir -p out cells logs out/calib
echo "[JOB] ticket 28 job2 runid=${RUNID} job=${SLURM_JOB_ID} commit=${NEW}"
date -u +"start %Y-%m-%dT%H:%M:%SZ"

git -C "${CANON}" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> logs/fetch.log 2>&1
git -C "${CANON}" cat-file -e "${NEW}^{commit}" 2>>logs/fetch.log || { echo "[JOB] FATAL commit ${NEW} missing"; exit 2; }
mkdir -p src
git -C "${CANON}" archive "${NEW}" | tar -x -C src || { echo "[JOB] FATAL archive"; exit 2; }
REPL=${RUN}/src/.scratch/juglet-breaklines/stage28/replica234.py
[ -f "$REPL" ] || { echo "[JOB] FATAL no replica at $REPL"; exit 2; }
cp "$REPL" out/replica234.py
if grep -lU $'\r' "$REPL" > out/crlf_check.txt 2>/dev/null; then
  echo "[JOB] FATAL CRLF in replica:"; cat out/crlf_check.txt; exit 2
fi
echo "[JOB] replica source ok md5=$(md5sum "$REPL" | cut -d" " -f1)"
echo "[JOB] python=$("$PY" -c 'import sys,numpy,scipy;print(sys.version.split()[0], "numpy", numpy.__version__, "scipy", scipy.__version__)')"

corpus_tree() {
  local out=$1
  { find "${CORP}" -type f -printf "%p\t%s\t%T@\n" | sort
    if [ -d /opt/sfs-pristine ]; then ls -R /opt/sfs-pristine | md5sum
    else echo "opt-sfs-pristine ABSENT"; fi
  } > "$out"
}
corpus_tree out/corpus_before.txt
grep -m1 "opt-sfs-pristine" out/corpus_before.txt

echo "[JOB] rung-2 dump inventory (the replica's inputs)"
: > out/inputs28.tsv
for tag in B E; do
  for p in 2 3 5 7; do
    f=$T25/$tag/Juglet_Piece_$p/r2_clusters_premerge.ply
    j=$T25/$tag/Juglet_Piece_$p/r2_clusters_premerge.json
    if [ -f "$f" ]; then
      printf "%s\t%s\t%s\t%s\t%s\n" "$tag" "Juglet_Piece_$p" "$(md5sum "$f" | cut -d" " -f1)" "$(awk '/^element vertex/{print $3; exit}' "$f")" "$f" >> out/inputs28.tsv
    else
      printf "MISSING\t%s\t-\t-\t%s\n" "Juglet_Piece_$p" "$f" >> out/inputs28.tsv
    fi
    [ -f "$j" ] && printf "SIDECAR\t%s\t%s\t-\t%s\n" "$tag" "$(tr -d '\n' < "$j")" "$j" >> out/inputs28.tsv
  done
done
PA=${POTADUMP}/Pot_A_Piece_07
if [ -f "$PA/r2_clusters_premerge.ply" ]; then
  printf "PA\tPot_A_Piece_07\t%s\t%s\t%s\n" "$(md5sum "$PA/r2_clusters_premerge.ply" | cut -d" " -f1)" "$(awk '/^element vertex/{print $3; exit}' "$PA/r2_clusters_premerge.ply")" "$PA/r2_clusters_premerge.ply" >> out/inputs28.tsv
  printf "SIDECAR\tPA\t%s\t-\t%s\n" "$(tr -d '\n' < "$PA/r2_clusters_premerge.json")" "$PA/r2_clusters_premerge.json" >> out/inputs28.tsv
else
  printf "MISSING\tPot_A_Piece_07\t-\t-\t%s\n" "$PA/r2_clusters_premerge.ply" >> out/inputs28.tsv
fi
grep -v "^SIDECAR" out/inputs28.tsv

echo "[JOB] CALIBRATION GATE"
"$PY" "$REPL" calibrate --dump-root "$T25" --tag B --outdir "${RUN}/out/calib" 2>&1 | tee logs/calibration.log
CALRC=${PIPESTATUS[0]}
echo "[JOB] calibration rc=$CALRC"
if [ "$CALRC" -ne 0 ]; then
  { echo "CALIBRATION GATE FAILED (rc=$CALRC) -- the grid was not run."
    echo "Expected: piece3 [169, 99] piece5 [679] piece7 [326, 263, 77, 68, 65] at theta 3.4 nb 10 kappa 1 floor 50 on arm B."
    grep "^\[CAL\]" logs/calibration.log
  } > out/GATE_FAILED.txt
  cat out/GATE_FAILED.txt
else
  echo "[JOB] grid: Juglet pieces 2 3 5 7 x cloud {B,E} x theta {3.4,4.0} x floor {50,none}"
  for tag in B E; do
    for p in 2 3 5 7; do
      f=$T25/$tag/Juglet_Piece_$p/r2_clusters_premerge.ply
      "$PY" "$REPL" sweep --ply "$f" --piece "Juglet_Piece_$p" --tag "$tag" --label "$tag" \
        --thetas 3.4 4.0 --kappa 1.0 --nb 10 --floors 50 none --outdir "$CELLS" 2>&1 | tee "logs/sweep_${tag}_p$p.log"
    done
  done
  PAFLOOR=$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["floor_applied"])' "$PA/r2_clusters_premerge.json")
  echo "[JOB] Pot A 07 recorded floor_applied=$PAFLOOR"
  "$PY" "$REPL" sweep --ply "$PA/r2_clusters_premerge.ply" --piece Pot_A_Piece_07 --tag PA --label PA \
    --thetas 3.4 4.0 --kappa 1.0 --nb 10 --floors 50 none "$PAFLOOR" --outdir "$CELLS" 2>&1 | tee logs/sweep_PA_p07.log
fi

echo "[JOB] cell table"
if [ -f "$CELLS/cells28.tsv" ]; then
  awk -F"\t" 'NR==1{print; next} {print}' "$CELLS/cells28.tsv" | cut -c1-220
  echo "[JOB] cells: $(($(wc -l < "$CELLS/cells28.tsv") - 1)) rows, json files: $(ls "$CELLS"/*.json 2>/dev/null | wc -l)"
fi

corpus_tree out/corpus_after.txt
if diff -q out/corpus_before.txt out/corpus_after.txt > out/corpus.diff 2>&1; then
  echo "[CORPUS] identical before and after: $(wc -l < out/corpus_before.txt) rows (incl /opt/sfs-pristine line)"
else
  echo "[CORPUS] DIFFERS"; cat out/corpus.diff
fi

"$PY" - "$RUN" "$SLURM_JOB_ID" "$NEW" "$RUNID" "$IXTAG" "$CALRC" <<'PYEOF'
import json, os, sys
run, job, commit, runid, ixtag, calrc = sys.argv[1:7]
d = {"runid": runid, "jobid": job, "commit": commit, "index_tag": ixtag,
     "ticket": "28-step-one-in-python", "job": "replica-grid",
     "instrument": ".scratch/juglet-breaklines/stage28/replica234.py",
     "inputs": "ticket-25 rung-2 dumps (arms B and E) + job-1 Pot A 07 rung-2 dump",
     "grid": "theta {3.4,4.0} x cloud {B,E} x floor {50,none}; Pot A 07: theta {3.4,4.0} x floor {recorded,50,none}",
     "calibration_exit": int(calrc),
     "cells": "out/cells/cells28.tsv and one json per cell"}
json.dump(d, open(os.path.join(run, "run.json"), "w"), indent=1, sort_keys=True)
print("[JOB] run.json written")
PYEOF

printf "%s\t%s\t%s\t%s\t\t\n" "$RUNID" "$SLURM_JOB_ID" "$NEW" "$IXTAG" >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
echo "[INDEX] appended one row:"
tail -2 /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv | awk -F"\t" '{print NF" fields: "$0}'

date -u +"end %Y-%m-%dT%H:%M:%SZ"
echo "[JOB] done runid=${RUNID} calibration_exit=$CALRC"
if [ "$CALRC" -ne 0 ]; then exit 4; fi
exit 0
