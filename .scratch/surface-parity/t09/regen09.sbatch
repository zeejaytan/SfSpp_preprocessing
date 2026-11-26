#!/bin/bash
#SBATCH --job-name=t09-regen
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --array=0-10
#SBATCH --output=logs/slurm-regen-%A_%a.out
#SBATCH --error=logs/slurm-regen-%A_%a.err
#
# Surface Parity Ticket 09, Stage 2 -- regenerate the canonical own surfaces, one Slurm array
# task per vessel: tasks 0..9 are Pot_A..Pot_J into <RUN>/out/Pot_<P>/geom, task 10 is the
# def_3x Juglet into <RUN>/out/Juglet_def3x/geom.  Both recipes are transcribed from the runs
# of record (pots: 20261105-0445_9c5eec2_t305-lane-e2; juglet: 20261117-0430_d272313_t80-default-on
# cell def_3x).  SFS_DEDUPE stays unset (the dedupe is the build's, not a switch) and
# SFS_WALL_PAIR_FILTER stays unset, i.e. the Ticket 80 default ON.
# Submit from the run directory:  cd <RUN> && sbatch work/t09/regen09.sbatch
set -uo pipefail

RUN=${SLURM_SUBMIT_DIR:?submit from the run directory}
TASK=${SLURM_ARRAY_TASK_ID:?run as an array}
JOBID=${SLURM_JOB_ID:-na}
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
DS=$CANON/Dataset
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SHIP=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship
T331=/data/gpfs/projects/punim2657/SfSpp/runs/20261112-0218_b1e1580_t331-large
LG=/data/gpfs/projects/punim2657/Dataset/Juglet_large
SHIPPED="SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0"
ENV3="SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0 SFS_MERGE_CLUSTER_DOT=0.887 SFS_GROW_BASE_MM=1.5 SFS_GROW_BASE_THETA_DEG=25 SFS_TREE_UNITS_PER_MM=3.0"
JUG="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"
LOGS=$RUN/logs
CELLDRV=$RUN/build/src/.scratch/juglet-breaklines/stage66/run_cell66.sh
INSTR=$RUN/build/src/.scratch/juglet-breaklines/stage55/instruments
MESH_BIN=$RUN/bin-MeshPreprocessingHeadless
EDGE_BIN=$RUN/bin-EdgeLineExtractionHeadless

for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
export OMP_NUM_THREADS=1
cd "$RUN"
mkdir -p "$LOGS" "$RUN/out"

fail() { local rc=$1; shift
  echo "[REGEN] FATAL task=$TASK rc=$rc $*"
  echo "FAIL $*" >> "$LOGS/regen_failures.txt"
  echo "run-failed" > "$RUN/RUN-FAILED-regen-$TASK.txt"
  exit "$rc"; }

[ -x "$MESH_BIN" ] || fail 3 "binaries missing (run build09.sbatch first)"
[ -x "$EDGE_BIN" ] || fail 3 "binaries missing (run build09.sbatch first)"
[ -f "$CELLDRV" ] || fail 3 "run_cell66.sh missing from build/src"
[ -d "$INSTR" ] || fail 3 "stage55 instruments missing from build/src"

mesh_of() { local stem=$1
  if [ -f "$CORP/Mesh/${stem}_Mesh_DS.obj" ]; then echo "$CORP/Mesh/${stem}_Mesh_DS.obj"
  else echo "$CORP/Mesh/${stem}_Mesh.obj"; fi }

case "$TASK" in
  0|1|2|3|4|5|6|7|8|9)
    P=$(echo "ABCDEFGHIJ" | cut -c$((TASK + 1)))
    VESSEL=Pot_$P
    OUTDIR=$RUN/out/$VESSEL
    PIECES=$(for f in "$SHIP/out/axes03_own"/Pot_${P}_Piece_*_Axis.xyz; do b=$(basename "$f"); echo "${b%_Axis.xyz}"; done | sort -u | tr '\n' ' ')
    [ -n "$PIECES" ] || fail 4 "no own-surface stems for Pot_$P in the frozen SHIP axes"
    MAN=$RUN/pins/MANIFEST_$P.tsv
    { printf "piece\tpcd_md5\tkept_points\n"
      awk -F'\t' -v pot="Pot_$P" 'NR>1 && $1==pot {printf "%s\t%s\t%s\n",$2,$5,$3}' "$CORP/Point/MANIFEST_released.tsv"
      awk -F'\t' -v pot="Pot_$P" 'NR>1 && index($1,pot "_")==1 {printf "%s\t%s\t%s\n",$1,$5,$4}' "$CORP/Point/MANIFEST_derived.tsv"
    } > "$MAN"
    FARM=$RUN/work/mesh_$P
    rm -rf "$FARM"; mkdir -p "$FARM"
    for s in $PIECES; do ln -sf "$(mesh_of "$s")" "$FARM/${s}_Mesh.obj"; done
    STAGER=$RUN/work/stage305.sh
    [ -f "$STAGER" ] || fail 3 "work/stage305.sh missing (build09 copies it)"
    CELLENV_KIND=pot
    ;;
  10)
    VESSEL=Juglet_def3x
    OUTDIR=$RUN/out/$VESSEL
    PIECES=$JUG
    MAN=$T331/pins/MANIFEST_JUGLET_LARGE.tsv
    STAGER=$RUN/work/stage_synth_t73.sh
    [ -f "$STAGER" ] || fail 3 "work/stage_synth_t73.sh missing (build09 copies it)"
    CELLENV_KIND=juglet
    ;;
  *) fail 3 "unknown array task $TASK" ;;
esac

echo "[REGEN] runid=$(basename "$RUN") job=$JOBID task=$TASK vessel=$VESSEL host=$(hostname) at $(date -u +%FT%TZ)"
echo "[REGEN] pieces: $(echo $PIECES | wc -w) | $(echo $PIECES)"
echo "[REGEN] cell branch: $CELLENV_KIND (variables exported per branch, not word-split)"
echo "[REGEN] binaries: $(sha256sum "$MESH_BIN" "$EDGE_BIN")"

# Cell invocation, one branch per recipe, every value quoted: a bare "$CELLENV" string
# word-splits PIECES and env then tries to exec the second piece name (exit 127).
if [ "$CELLENV_KIND" = pot ]; then
  env POT_NAME="Pot_$P" PIECES="$PIECES" WORNESS= MESH_ENV="$SHIPPED" OUT="$OUTDIR" \
      CLOUD_DIR="$CORP/Point/Pot_$P" MESH_DIR="$FARM" AXIS_DIR="$CORP/Axes" MANIFEST="$MAN" \
      MAN_MD5_COL=pcd_md5 MAN_PTS_COL=kept_points INSTR="$INSTR" PY="$PY" DS="$DS" CORP="$CORP" \
      MESH_BIN="$MESH_BIN" EDGE_BIN="$EDGE_BIN" APT="$APT" SIF="$SIF" STAGER="$STAGER" \
      RUN="$RUN" JOBID="$JOBID" bash "$CELLDRV" > "$LOGS/cell_$VESSEL.log" 2>&1
else
  env MESH_ROOT="$T331/mesh_large" POT_NAME=Juglet_large PIECES="$PIECES" WORNESS=0.7 MESH_ENV="$ENV3" \
      OUT="$OUTDIR" CLOUD_DIR="$T331/cloud_mesh" MESH_DIR="$T331/mesh_large" AXIS_DIR="$LG" \
      MANIFEST="$MAN" MAN_MD5_COL=pcd_md5 MAN_PTS_COL=kept_points MAN_SPACING_COL=spacing_mm \
      INSTR="$INSTR" PY="$PY" DS="$DS" CORP="$CORP" MESH_BIN="$MESH_BIN" EDGE_BIN="$EDGE_BIN" \
      APT="$APT" SIF="$SIF" STAGER="$STAGER" RUN="$RUN" JOBID="$JOBID" bash "$CELLDRV" >> "$LOGS/cell_$VESSEL.log" 2>&1
fi
RC=$?
echo "[REGEN] cell rc=$RC"
tail -20 "$LOGS/cell_$VESSEL.log" || true

NGEOM=$(ls "$OUTDIR/geom" 2>/dev/null | wc -l)
NMISS=0
for s in $PIECES; do
  for k in S0 S1 Bl0 Bl1; do
    f=$OUTDIR/geom/$s.$k
    if [ ! -s "$f" ]; then echo "[REGEN] MISSING/EMPTY $f" >> "$LOGS/regen_missing.txt"; NMISS=$((NMISS + 1)); fi
  done
done
NDED=$(grep -ah "DEDUPE-27" "$OUTDIR"/pieces/*/mesh.log 2>/dev/null | wc -l)
{ echo "vessel=$VESSEL"; echo "task=$TASK"; echo "jobid=$JOBID"
  echo "pieces=$(echo $PIECES | wc -w)"; echo "cell_rc=$RC"
  echo "geom_files=$NGEOM"; echo "geom_missing_or_empty=$NMISS"; echo "dedupe27_lines=$NDED"
  echo "utc=$(date -u +%FT%TZ)"; } > "$LOGS/regen_$VESSEL.txt"
cat "$LOGS/regen_$VESSEL.txt"

[ "$RC" -eq 0 ] || fail 8 "cell rc=$RC (see logs/cell_$VESSEL.log)"
[ "$NMISS" -eq 0 ] || fail 9 "$NMISS missing or empty geom files"
echo "T09-REGEN-OK $VESSEL"
exit 0
