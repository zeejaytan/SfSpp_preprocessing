#!/bin/bash
#SBATCH --job-name=t57-stageA
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=03:00:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0450_05be12c_t57-sweep/logs/sweep-%j.out
# ticket 57 Stage A sweep: N arms of SFS_WORNESS, one run directory per arm.
# The dial binary is COPIED from the t54/t55 build and md5-gated; this job NEVER rebuilds it.
set -uo pipefail

RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
PREFIX=20261102-0450_05be12c_t57
BINSRC=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0333_05be12c_t57-w050
INSTRSRC=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0333_05be12c_t57-w050/instruments
SELF=/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0450_05be12c_t57-sweep/submit.sbatch
SELF_DIR=$(cd "$(dirname "$SELF")" && pwd)
DS=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
ARMS="w030 w035 w040 w045 w055 w060 w065 w075 w080 w085 w090 default w070"
PAR=4
JOBID=${SLURM_JOB_ID:-manual}
export DS CORP APT SIF PY JOBID

echo "[SW57] job=$JOBID host=$(hostname) arms=[$ARMS] par=$PAR"
date -u +%H:%M:%S

EXPECT=736ff95c976486d17f7c00b3af402040
GOT=$(md5sum "$BINSRC/bin-MeshPreprocessingHeadless" | cut -d" " -f1)
[ "$GOT" = "$EXPECT" ] || { echo "[SW57] FATAL source mesh binary md5 $GOT != $EXPECT"; exit 9; }
echo "[SW57] source mesh binary md5 ok $GOT"

arm_dir() {
  if [ "$1" = default ]; then echo "$RUNS/${PREFIX}-default"; else echo "$RUNS/${PREFIX}-$1"; fi
}

arm_value() {
  case "$1" in
    default) echo "" ;;
    w*) local d="${1#w}"; echo "${d%??}.${d: -2}" ;;
    *) echo "?" ;;
  esac
}

setup_arm() {
  local A=$1 W AD
  AD=$(arm_dir "$A")
  W=$(arm_value "$A")
  [ "$W" = "?" ] && { echo "[SW57] FATAL bad arm $A"; return 9; }
  mkdir -p "$AD/logs" "$AD/instruments" "$AD/out"
  cp -f "$BINSRC/bin-MeshPreprocessingHeadless" "$BINSRC/bin-EdgeLineExtractionHeadless" "$AD"/ || return 9
  chmod +x "$AD"/bin-* || return 9
  cp -f "$INSTRSRC/run_cell57.sh" "$INSTRSRC/run_arm57.sh" "$INSTRSRC/stage_synth_p40.sh" \
        "$INSTRSRC/render55.py" "$INSTRSRC/check_separation.py" "$AD/instruments/" || return 9
  cp -f "$SELF" "$AD/submit.sbatch" || return 9
  local GOTE
  GOT=$(md5sum "$AD/bin-MeshPreprocessingHeadless" | cut -d" " -f1)
  GOTE=$(md5sum "$AD/bin-EdgeLineExtractionHeadless" | cut -d" " -f1)
  if [ "$GOT" != "$EXPECT" ]; then echo "[SW57] FATAL $A copied mesh md5 $GOT"; return 9; fi
  printf '{"runid": "%s", "jobid": "%s", "commit": "05be12c28e252a3b06410b2cf5126ef8afa19064", "tag": "t57-worness-fine-sweep", "branch": "57-worness-fine-sweep-surface-separation", "arm": "%s", "worness": "%s", "pieces": 9, "binary_md5": "%s", "edge_binary_md5": "%s", "harness": "run_cell57.sh (t55 run_cell55.sh, WORNESS default removed)", "note": "arm of the ticket 57 Stage A sweep; all arms share one code path"}\n' \
    "$(basename "$AD")" "$JOBID" "$A" "${W:-unset}" "$GOT" "$GOTE" > "$AD/run.json"
  echo "[SW57] arm $A -> worness=${W:-<unset>} $AD $(date -u +%H:%M:%S)"
}

run_one() {
  local A=$1 W AD RC
  AD=$(arm_dir "$A")
  W=$(arm_value "$A")
  ARM="$A" WORNESS="$W" OUT="$AD/out" \
    INSTR="$AD/instruments" PY="$PY" DS="$DS" CORP="$CORP" \
    MESH_BIN="$AD/bin-MeshPreprocessingHeadless" EDGE_BIN="$AD/bin-EdgeLineExtractionHeadless" \
    APT="$APT" SIF="$SIF" STAGER="$AD/instruments/stage_synth_p40.sh" RUN="$AD" JOBID="$JOBID" \
    bash "$AD/instruments/run_arm57.sh" > "$AD/logs/arm.log" 2>&1
  RC=$?
  cp -f "$AD/out/cells57.log" "$AD/logs/cells57.log" 2>/dev/null
  echo "[SW57] arm $A rc=$RC $(date -u +%H:%M:%S)"
  return $RC
}

for A in $ARMS; do setup_arm "$A" || { echo "[SW57] FATAL setup failed for $A"; exit 9; }; done

for A in $ARMS; do
  while [ "$(jobs -rp | wc -l)" -ge "$PAR" ]; do wait -n || true; done
  run_one "$A" &
done
wait
echo "[SW57] all arms done $(date -u +%H:%M:%S)"

FAILED=0
for A in $ARMS; do
  AD=$(arm_dir "$A")
  echo "[SW57] ===== $A ($AD) ====="
  if [ -f "$AD/out/pieces57.tsv" ]; then
    cat "$AD/out/pieces57.tsv"
    BAD=$(awk -F'\t' 'NR>1 && $11!="ok"' "$AD/out/pieces57.tsv" | wc -l)
    [ "$BAD" -gt 0 ] && { echo "[SW57] WARN $A has $BAD non-ok pieces"; FAILED=1; }
  else
    echo "[SW57] MISSING $AD/out/pieces57.tsv"; FAILED=1
  fi
  grep -a "STOP\|FATAL" "$AD/logs/cells57.log" 2>/dev/null | head -5
done
echo "[SW57] summary_failed=$FAILED"

# ---- phase 2: frozen-definition metrics for every arm, plus the baseline row, same code path
echo "[SW57] ===== metrics phase $(date -u +%H:%M:%S) ====="
T54=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-1613_83edd76_t54-worness-dial
T55=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-2004_05be12c_t55-worness07-breaklines
MET=$SELF_DIR/metrics
mkdir -p "$MET"
run_metrics() {
  local label=$1 geom=$2 tsv=$3 json=$4
  "$PY" "$SELF_DIR/check_separation.py" --geom "$geom" --mesh-dir "$DS/Mesh/Juglet" \
      --walls "$T54/out/wall40" --k 15 --out-tsv "$tsv" --out-json "$json" > "$MET/$label.log" 2>&1
  echo "[SW57] metrics $label rc=$? -> $tsv"
}
run_metrics baseline "$T55/out/geom" "$MET/baseline_t55.tsv" "$MET/baseline_t55.json"
for A in $ARMS; do
  AD=$(arm_dir "$A")
  [ -d "$AD/out/geom" ] || { echo "[SW57] metrics skip $A (no geom)"; continue; }
  run_metrics "$A" "$AD/out/geom" "$MET/$A.tsv" "$MET/$A.json"
done
echo "[SW57] metrics done $(date -u +%H:%M:%S)"
PLAY="$MET/play.tsv"
"$PY" "$SELF_DIR/table57.py" --metrics "$MET" --arms "$ARMS" --out "$PLAY" || echo "[SW57] table rc=$?"
cat "$PLAY" 2>/dev/null
exit 0
