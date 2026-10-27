#!/bin/bash
#SBATCH --job-name=__JOBNAME__
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=__TIME__
#SBATCH --output=__RUNDIR__/logs/slurm-%j.out
#SBATCH --error=__RUNDIR__/logs/slurm-%j.err
# ticket 28, job 1 of 2 -- the Pot A 07 control run, then a calibration smoke test.
#
# Part 1: ONE pipeline run of Pot_A_Piece_07 at today's defaults (no SFS_* parameter
# overrides beyond the dump switch) with SFS_DUMP_STAGE armed, so the rung-1 and
# rung-2 geometry of the piece the method is known to work on exists on disk.
# Part 2: the calibration gate of the Python replica on the ticket-25 arm-B dumps,
# run in this same job so a replica that does not reproduce the three expected
# region lists can be corrected without spending a third job.
set -uo pipefail

RUN=__RUNDIR__
RUNID=__RUNID__
NEW=__NEWCOMMIT__
IXTAG=__IXTAG__
PIECE=__PIECE__
POT=__POT__
T25=__T25DUMP__
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
SIF=${CANON}/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
INSTR=${RUN}/instruments
ST=${RUN}/out/stage
DUMPROOT=${RUN}/out/dump
STAGER=${INSTR}/stage_piece_p28.sh
BIND="--bind /data:/data"
export CANON CORP SIF APT PY INSTR ST DUMPROOT STAGER NEW RUN RUNID PIECE POT T25 SLURM_CPUS_PER_TASK

cd "${RUN}" || exit 1
mkdir -p out/bin out/logs logs out/calib
echo "[JOB] ticket 28 job1 runid=${RUNID} job=${SLURM_JOB_ID} commit=${NEW} piece=${PIECE} pot=${POT}"
date -u +"start %Y-%m-%dT%H:%M:%SZ"

git -C "${CANON}" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" >> logs/fetch.log 2>&1
if ! git -C "${CANON}" cat-file -e "${NEW}^{commit}" 2>>logs/fetch.log; then
  echo "[JOB] FATAL commit ${NEW} not in ${CANON}"; exit 2
fi
echo "[JOB] commit ok $(git -C "${CANON}" rev-parse --short "${NEW}")"
for f in "${STAGER}" "${INSTR}/replica234.py"; do
  [ -f "$f" ] || { echo "[JOB] FATAL missing instrument $f"; exit 2; }
done
if grep -lU $'\r' "${STAGER}" "${INSTR}/replica234.py" > out/crlf_check.txt 2>/dev/null; then
  echo "[JOB] FATAL CRLF in instruments:"; cat out/crlf_check.txt; exit 2
fi
echo "[JOB] instruments present, no CRLF"

hash_inputs() {
  local out=$1 f
  : > "$out"
  for f in "${CORP}/Point/Pot_A/${PIECE}_Point.pcd" "${CORP}/Mesh/${PIECE}_Mesh.obj" "${CANON}/Dataset/Axes/Pot_A/${PIECE}_Axis.xyz"; do
    if [ -f "$f" ]; then
      printf "%s\t%s\t%s\n" "$(md5sum "$f" | cut -d" " -f1)" "$f" "$(stat -c %s "$f")"
    else
      printf "MISSING\t%s\t-\n" "$f"
    fi
  done > "$out"
}
corpus_tree() {
  local out=$1
  { find "${CORP}" -type f -printf "%p\t%s\t%T@\n" | sort
    if [ -d /opt/sfs-pristine ]; then ls -R /opt/sfs-pristine | md5sum
    else echo "opt-sfs-pristine ABSENT"; fi
  } > "$out"
}

hash_inputs out/inputs_before.md5
corpus_tree out/corpus_before.txt
echo "[JOB] inputs before:"; cat out/inputs_before.md5
grep -m1 "opt-sfs-pristine" out/corpus_before.txt

echo "[JOB] build from ${NEW}"
mkdir -p build/src
if ! git -C "${CANON}" archive "${NEW}" | tar -x -C build/src; then
  echo "[JOB] FATAL git archive failed"; exit 3
fi
( cd build/src && mkdir -p build && cd build \
    && "$APT" exec $BIND "$SIF" cmake -DCMAKE_BUILD_TYPE=Release .. \
    && "$APT" exec $BIND "$SIF" make -j"${SLURM_CPUS_PER_TASK:-8}" MeshPreprocessingHeadless ) >> logs/build.log 2>&1
if [ ! -x build/src/build/MeshPreprocessingHeadless ]; then
  echo "[JOB] FATAL build failed"
  grep -E "error:|Error [0-9]" logs/build.log | head -40
  exit 3
fi
BIN=${RUN}/build/src/build/MeshPreprocessingHeadless
cp "$BIN" out/bin/MeshPreprocessingHeadless.NEW
echo "[JOB] build ok bytes=$(stat -c %s "$BIN") md5=$(md5sum "$BIN" | cut -d" " -f1)"

echo "[JOB] stage ${PIECE}"
bash "$STAGER" "$ST" "$POT" "$PIECE" "${CANON}/Dataset/Axes/Pot_A/${PIECE}_Axis.xyz" > logs/stage.log 2>&1
SS=$?
echo "[JOB] stage exit=$SS"; cat logs/stage.log
if [ "$SS" -ne 0 ]; then echo "[JOB] FATAL stage failed"; exit 4; fi

echo "[JOB] pipeline run, today's defaults + SFS_DUMP_STAGE"
T0=$(date +%s)
( cd "$ST" && "$APT" exec $BIND "$SIF" env POT_NAME="$POT" \
    SFS_AXIS_FILE="$ST/Dataset/Axes/${PIECE}_Axis.xyz" \
    SFS_STATUS_FILE="${RUN}/out/status_raw.tsv" \
    SFS_DUMP_STAGE="$DUMPROOT" SFS_DUMP_PIECES="$PIECE" "$BIN" ) > logs/mesh.log 2>&1
MS=$?
T1=$(date +%s)
echo "[JOB] pipeline exit=$MS elapsed=$((T1-T0))s"
grep -E "\[DUMP-25\]|\[STATUS-23\]|\[RETRY-23\]|\[PAPER-234\]|\[COUNT-22\]|\[FLOOR-23\]|\[SPACING-22\]" logs/mesh.log | head -40

echo "[JOB] dump inventory"
find "$DUMPROOT" -type f -printf "%p\t%s\n" 2>/dev/null | sort > out/dump_files.tsv
cat out/dump_files.tsv
find "$DUMPROOT" -name "*.ply" -exec md5sum {} + 2>/dev/null | sort -k2 > out/dump_md5.txt
cat out/dump_md5.txt
DP=$DUMPROOT/$PIECE
for r in r1_downsampled r2_clusters_premerge; do
  f=$DP/$r.ply
  if [ -f "$f" ]; then
    echo "[RUNG] $r vertices=$(awk '/^element vertex/{print $3; exit}' "$f")"
  else
    echo "[RUNG] $r MISSING"
  fi
done
cp -f "$DP"/r*.json out/ 2>/dev/null || true
ls -l out/*.json 2>/dev/null || true

echo "[JOB] geometry deleted with a counted record, stage tree removed"
if [ -d "$ST" ]; then
  find "$ST" -type f -printf "%f\t%s\n" 2>/dev/null | awk -F"\t" '{
      n = split($1, a, "."); e = (n > 1 ? a[n] : "none");
      if (e == "pcd" || e == "ply" || e == "xyz" || e == "obj") f = e; else f = "other";
      cnt[f]++; byt[f] += $2
    } END { for (k in cnt) printf "%s\t%d\t%d\n", k, cnt[k], byt[k] }' | sort > out/geometry_deleted.tsv
  rm -rf "$ST"
fi
{
  echo "# ticket 28 job 1 -- geometry deleted after the pipeline run, with counts and bytes."
  echo "# KEPT: out/dump/** (rung 1-5 of ${PIECE} -- the Pot A control cloud and normals), logs/, out/*.json sidecars."
  echo -e "ext\tfiles\tbytes"
  cat out/geometry_deleted.tsv
  echo "#"
  echo -e "total\t$(awk -F"\t" '{c+=$2; b+=$3} END {print c"\t"b}' out/geometry_deleted.tsv)"
  echo "# kept rung dumps: $(find "$DUMPROOT" -name "*.ply" | wc -l) ply, $(find "$DUMPROOT" -name "*.json" | wc -l) json, $(du -sb "$DUMPROOT" | cut -f1) bytes"
  echo "# stage trees left on disk (expect 0): $(find "${RUN}/out" -maxdepth 1 -type d -name stage | wc -l)"
} > out/GEOMETRY_DELETED.txt
cat out/GEOMETRY_DELETED.txt

echo "[JOB] CALIBRATION GATE: replica234.py on ticket-25 arm B, theta 3.4 nb 10 kappa 1 floor 50"
"$PY" "$INSTR/replica234.py" calibrate --dump-root "$T25" --tag B --outdir "${RUN}/out/calib" 2>&1 | tee logs/calibration.log
CALRC=${PIPESTATUS[0]}
echo "[JOB] calibration rc=$CALRC (0 = all three pieces match)"

hash_inputs out/inputs_after.md5
corpus_tree out/corpus_after.txt
if diff -q out/inputs_before.md5 out/inputs_after.md5 > out/inputs.diff 2>&1; then
  echo "[INPUTS] identical before and after: $(wc -l < out/inputs_before.md5) rows"
else
  echo "[INPUTS] DIFFERS"; cat out/inputs.diff
fi
if diff -q out/corpus_before.txt out/corpus_after.txt > out/corpus.diff 2>&1; then
  echo "[CORPUS] identical before and after: $(wc -l < out/corpus_before.txt) rows (incl /opt/sfs-pristine line)"
else
  echo "[CORPUS] DIFFERS"; cat out/corpus.diff
fi
grep -m1 "opt-sfs-pristine" out/corpus_before.txt || true

"$PY" - "$RUN" "$SLURM_JOB_ID" "$NEW" "$RUNID" "$IXTAG" "$PIECE" "$MS" "$CALRC" <<'PYEOF'
import json, os, sys
run, job, commit, runid, ixtag, piece, ms, calrc = sys.argv[1:9]
d = {"runid": runid, "jobid": job, "commit": commit, "index_tag": ixtag,
     "ticket": "28-step-one-in-python", "job": "pota07-dump+calibration",
     "piece": piece, "pot": "Pot_A",
     "parameters": "today's defaults; only SFS_DUMP_STAGE/SFS_DUMP_PIECES armed",
     "pipeline_exit": int(ms), "calibration_exit": int(calrc),
     "dump_kept": "out/dump/%s (r1..r5, the Pot A control cloud and normals)" % piece,
     "runs_root": os.path.dirname(run)}
json.dump(d, open(os.path.join(run, "run.json"), "w"), indent=1, sort_keys=True)
print("[JOB] run.json written")
PYEOF

printf "%s\t%s\t%s\t%s\t\t\n" "$RUNID" "$SLURM_JOB_ID" "$NEW" "$IXTAG" >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
echo "[INDEX] appended one row:"
tail -2 /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv | awk -F"\t" '{print NF" fields: "$0}'

rm -rf "${RUN}/build"
date -u +"end %Y-%m-%dT%H:%M:%SZ"
echo "[JOB] done runid=${RUNID} pipeline_exit=$MS calibration_exit=$CALRC"
exit 0
