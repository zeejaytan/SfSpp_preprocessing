#!/bin/bash
#SBATCH --job-name=__JOBNAME__
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=__TIME__
#SBATCH --output=__RUNDIR__/logs/slurm-%j.out
#SBATCH --error=__RUNDIR__/logs/slurm-%j.err
# ticket 29 -- one job, no build, no pipeline run: the whole measurement is numpy/scipy.
#
# Order is the ticket's: part C (the calibration gate) runs first and if any growPaper234
# cloud fails it, the instrument writes out/GATE_FAILED.txt and returns 5, so no angles, no
# ladder, no comparison and no figure are computed or written in this job.
#
# The borrowed rung dumps (ticket 25 and ticket 28) are read in place and never written:
# their inventory and md5s are taken before and after the instrument runs and diffed.
# This job writes no geometry of its own; it keeps tables, json cells, logs and one figure.
set -uo pipefail

RUN=__RUNDIR__
RUNID=__RUNID__
NEW=__NEWCOMMIT__
IXTAG=__IXTAG__
GRID=__GRIDROOT__
POTA=__POTAROOT__
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
RUNROOT=/data/gpfs/projects/punim2657/SfSpp/runs
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
INS=$RUN/instruments
OUT=$RUN/out
FIG=$OUT/ticket29_angles_vs_theta.png
export RUN RUNID NEW IXTAG GRID POTA PY RUNROOT CORP INS OUT FIG SLURM_JOB_ID

cd "$RUN" || exit 1
mkdir -p logs out out/cells
echo "[JOB] ticket29 survey runid=$RUNID job=$SLURM_JOB_ID commit=$NEW tag=$IXTAG"
echo "[JOB] node=$(hostname) date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[JOB] grid=$GRID"
echo "[JOB] pota=$POTA"
"$PY" -c "import numpy, scipy, matplotlib, PIL; print('[JOB] numpy', numpy.__version__, 'scipy', scipy.__version__, 'matplotlib', matplotlib.__version__)"

# CRLF guard: two earlier grids died with "set: pipefail: invalid option name" on CRLF scripts.
if grep -lU $'\r' "$INS"/*.py "$INS"/*.sh "$INS"/*.sbatch "$RUN/submit.sbatch" 2>/dev/null; then
  echo "[JOB] FATAL CRLF line endings in the files this job runs"
  exit 2
fi
echo "[JOB] no CRLF in instruments or submit.sbatch"
md5sum "$INS"/* > out/instruments.md5
cat out/instruments.md5

inv() {
  local out=$1 a p
  : > "$out"
  for a in B D E; do
    for p in 2 3 5 7; do
      find "$GRID/$a/Juglet_Piece_$p" -type f -printf "%p\t%s\n" 2>/dev/null
    done
  done >> "$out"
  find "$POTA/Pot_A_Piece_07" -type f -printf "%p\t%s\n" 2>/dev/null >> "$out"
  sort -o "$out" "$out"
}
md5s() {
  local out=$1 a p
  : > "$out"
  for a in B D E; do
    for p in 2 3 5 7; do
      find "$GRID/$a/Juglet_Piece_$p" -type f -name "*.ply" -exec md5sum {} + 2>/dev/null
    done
  done >> "$out"
  find "$POTA/Pot_A_Piece_07" -type f -name "*.ply" -exec md5sum {} + 2>/dev/null >> "$out"
  sort -k2 -o "$out" "$out"
}
sizes() {
  local out=$1 a p
  {
    echo -e "cloud\tfiles\tbytes\tpath"
    for a in B D E; do
      for p in 2 3 5 7; do
        printf "%s/%s\t%s\t%s\t%s\n" "$a" "Juglet_Piece_$p" \
          "$(find "$GRID/$a/Juglet_Piece_$p" -type f | wc -l)" \
          "$(du -sb "$GRID/$a/Juglet_Piece_$p" | cut -f1)" \
          "$GRID/$a/Juglet_Piece_$p"
      done
    done
    printf "PA/%s\t%s\t%s\t%s\n" "Pot_A_Piece_07" \
      "$(find "$POTA/Pot_A_Piece_07" -type f | wc -l)" \
      "$(du -sb "$POTA/Pot_A_Piece_07" | cut -f1)" \
      "$POTA/Pot_A_Piece_07"
  } > "$out"
}
corpus_tree() {
  local out=$1
  { find "$CORP" -type f -printf "%p\t%s\t%T@\n" | sort
    if [ -d /opt/sfs-pristine ]; then ls -R /opt/sfs-pristine | md5sum
    else echo "opt-sfs-pristine ABSENT"; fi
  } > "$out"
}

inv out/dump_inventory_before.tsv
md5s out/dump_md5_before.txt
sizes out/dump_sizes.tsv
corpus_tree out/corpus_before.txt
echo "[JOB] borrowed dumps before: $(wc -l < out/dump_inventory_before.tsv) files, $(awk -F'\t' '{s+=$2} END {print s}' out/dump_inventory_before.tsv) bytes"
cat out/dump_sizes.tsv
grep -m1 "opt-sfs-pristine" out/corpus_before.txt || true
echo "[JOB] corpus files listed before: $(wc -l < out/corpus_before.txt)"

echo "[JOB] PART C first, then A, B, D and the figure"
"$PY" "$INS/replica29.py" survey \
  --grid-root "$GRID" --pota-root "$POTA" --outdir "$OUT" --figure "$FIG" \
  --kappa 1.0 --nb 10 --floor 50 \
  --thetas 2.0 3.4 4.0 5.0 6.0 8.0 10.0 12.0 \
  --gate-tol 10 --commit "$NEW" --runid "$RUNID" --jobid "$SLURM_JOB_ID" \
  > logs/survey.log 2>&1
RC=$?
echo "[JOB] survey rc=$RC (0 ok, 5 = calibration gate failed, 1/other = error)"
tail -40 logs/survey.log
echo "[JOB] calibration lines:"
grep -h "^\[CAL\]" logs/survey.log || true

inv out/dump_inventory_after.tsv
md5s out/dump_md5_after.txt
corpus_tree out/corpus_after.txt
if diff -q out/dump_inventory_before.tsv out/dump_inventory_after.tsv > out/dump_inventory.diff 2>&1; then
  echo "[DUMPS] inventory identical before and after ($(wc -l < out/dump_inventory_before.tsv) files)"
else
  echo "[DUMPS] INVENTORY DIFFERS"; cat out/dump_inventory.diff
fi
if diff -q out/dump_md5_before.txt out/dump_md5_after.txt > out/dump_md5.diff 2>&1; then
  echo "[DUMPS] md5 identical before and after ($(wc -l < out/dump_md5_before.txt) ply files)"
else
  echo "[DUMPS] MD5 DIFFERS"; cat out/dump_md5.diff
fi
if diff -q out/corpus_before.txt out/corpus_after.txt > out/corpus.diff 2>&1; then
  echo "[CORPUS] identical before and after ($(wc -l < out/corpus_before.txt) rows incl the /opt/sfs-pristine line)"
else
  echo "[CORPUS] DIFFERS"; cat out/corpus.diff
fi
grep -m1 "opt-sfs-pristine" out/corpus_after.txt || true

{
  echo "# ticket 29 -- geometry written by this job and deleted by this job, with counts."
  echo "# This job ran no pipeline and produced no intermediate geometry: it read the borrowed"
  echo "# rung dumps in place and wrote tables, json cells, logs and one figure."
  echo -e "ext\tfiles\tbytes"
  echo "# geometry files written by this job: 0"
  echo "# geometry files deleted by this job: 0"
  echo "# stage trees left on disk (expect 0): $(find "$OUT" -maxdepth 1 -type d -name stage | wc -l)"
  echo "# borrowed geometry stays where it is; the lead deletes it at close:"
  echo -e "total\t$(awk -F'\t' 'NR>1 {c+=$2; b+=$3} END {print c"\t"b}' out/dump_sizes.tsv)"
  awk -F'\t' 'NR>1 {printf "# borrowed\t%s\t%s\t%s\n", $1, $2, $3}' out/dump_sizes.tsv
  echo "# kept by this run: $(find "$OUT" -type f -name '*.tsv' | wc -l) tsv, $(find "$OUT" -type f -name '*.json' | wc -l) json, $(find "$OUT" -type f -name '*.png' | wc -l) figure, $(find "$OUT" -type f -name '*.md' | wc -l) summary"
} > out/GEOMETRY_DELETED.txt
cat out/GEOMETRY_DELETED.txt

"$PY" - "$RUN" "$SLURM_JOB_ID" "$NEW" "$RUNID" "$IXTAG" "$RC" "$GRID" "$POTA" <<'PYEOF'
import json, os, sys
run, job, commit, runid, tag, rc, grid, pota = sys.argv[1:9]
d = {"runid": runid, "jobid": job, "commit": commit, "index_tag": tag,
     "ticket": "29-what-angle-does-the-wall-need",
     "job": "part C gate, then part A angles, part B theta ladder, part D comparison, figure",
     "instrument": "instruments/replica29.py (copy of stage28/replica234.py extended)",
     "instrument_commit": commit,
     "parameters": {"kappa": 1.0, "nb": 10, "floor": 50,
                    "thetas": [2.0, 3.4, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0],
                    "gate_tolerance_points": 10},
     "inputs": {"grid": grid, "pota": pota,
                "note": "read-only; inventory and md5 taken before and after",
                "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp list only",
                "opt_sfs_pristine": "ABSENT (recorded, not created)"},
     "geometry_written": 0, "geometry_deleted": 0,
     "survey_exit": int(rc),
     "survey_exit_meaning": "0 ok; 5 the calibration gate failed and nothing else ran",
     "writes": ["out/", "logs/", "index.tsv one row"],
     "runs_root": os.path.dirname(run)}
json.dump(d, open(os.path.join(run, "run.json"), "w"), indent=1, sort_keys=True)
print("[JOB] run.json written")
PYEOF

printf "%s\t%s\t%s\t%s\t\t\n" "$RUNID" "$SLURM_JOB_ID" "$NEW" "$IXTAG" >> "$RUNROOT/index.tsv"
echo "[INDEX] appended one row:"
tail -2 "$RUNROOT/index.tsv" | awk -F"\t" '{print NF" fields: "$0}'

echo "[JOB] files in out/"
find out -type f -printf "%p\t%s\n" | sort
date -u +"[JOB] end %Y-%m-%dT%H:%M:%SZ"
echo "[JOB] done runid=$RUNID survey_exit=$RC"
exit "$RC"
