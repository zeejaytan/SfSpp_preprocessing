#!/bin/bash
#SBATCH --job-name=p290rep
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=00:40:00
#SBATCH --output=logs/p290rep_%j.out

# Ticket 290 follow-up: does a run from the frozen cloud reproduce? Two independent mesh-stage
# runs (each from the released cloud and the same DS mesh) and two independent edge-stage runs
# from identical Temp/Data inputs; exports compared byte for byte. No build, no code change, no
# default change. Uses the binaries kept in $RUN/bin from job 33748526.
set -u
: "$RUN_DIR"; : "$CANONICAL"
RUN=$RUN_DIR
CANON=$CANONICAL
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PYC=/data/gpfs/projects/punim2657/.conda/envs/graphify/bin/python3
CORPUS=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
POINT=$CORPUS/Point
PIECE=Pot_J_Piece_09
MESH=$RUN/bin/MeshPreprocessingHeadless
EDGE=$RUN/bin/EdgeLineExtractionHeadless
S3=$RUN/repeat/st3
S4=$RUN/repeat/st4
EA=$RUN/repeat/edgeA
EB=$RUN/repeat/edgeB
mkdir -p "$RUN/logs" "$RUN/repeat"
say() { echo "[$(date -u +%H:%M:%S)] $*"; }
say "job $SLURM_JOB_ID on $(hostname)"
md5sum "$MESH" "$EDGE" | tee "$RUN/out/repeat_binaries.md5"

# ---------- two independent mesh-stage runs, same inputs ----------
for d in "$S3" "$S4"; do
  mkdir -p "$d/Dataset/Point/Pot_J" "$d/Dataset/Mesh/Pot_J" "$d/Dataset/Axes" "$d/Dataset/Breaklines/Pot_J" "$d/Temp/Data/Pot_J" "$d/Temp/Temp_edge/Pot_J"
  ln -sfn "$POINT/Pot_J/"$PIECE"_Point.pcd" "$d/Dataset/Point/Pot_J/"$PIECE"_Point.pcd"
  cp "$CORPUS/Mesh/"$PIECE"_Mesh_DS.obj" "$d/Dataset/Mesh/Pot_J/"$PIECE"_Mesh.obj"
  cp "$CORPUS/Axes/"$PIECE"_Axis.xyz" "$d/Dataset/Axes/"
done
for d in "$S3" "$S4"; do
  say "mesh stage in $d"
  ( cd "$d" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_J SFS_AXIS_FILE="$d/Dataset/Axes/"$PIECE"_Axis.xyz" "$MESH" > "$RUN/logs/mesh_$(basename $d).log" 2>&1 ; echo "MESH_EXIT=$?" )
done
grep -h -E "PAPER-234\] classify" "$RUN/logs/mesh_st3.log" "$RUN/logs/mesh_st4.log" | tee "$RUN/out/repeat_classify.txt"
md5sum "$S3/Temp/Data/Pot_J/"$PIECE"_Surface_0.xyz" "$S4/Temp/Data/Pot_J/"$PIECE"_Surface_0.xyz" "$S3/Temp/Data/Pot_J/"$PIECE"_Surface_1.xyz" "$S4/Temp/Data/Pot_J/"$PIECE"_Surface_1.xyz" | tee "$RUN/out/repeat_sheets.md5"

# ---------- two independent edge runs from identical Temp/Data ----------
cp -a "$S3" "$EA"; cp -a "$S3" "$EB"
for d in "$EA" "$EB"; do
  say "edge stage in $d"
  ( cd "$d" && rm -f Dataset/Breaklines/Pot_J/*.pcd && "$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_J "$EDGE" > "$RUN/logs/edge_$(basename $d).log" 2>&1 ; echo "EDGE_EXIT=$?" )
done
grep -h -E "SEED-287|FULL-263 kept|chain=" "$RUN/logs/edge_edgeA.log" "$RUN/logs/edge_edgeB.log" | head -12 | tee "$RUN/out/repeat_edge_lines.txt"
"$PYC" "$RUN/repeat290.py" "$RUN" "$EA/Dataset/Breaklines/Pot_J" "$EB/Dataset/Breaklines/Pot_J" > "$RUN/logs/repeat290.log" 2>&1
echo "REPEAT290_EXIT=$?"
cat "$RUN/logs/repeat290.log"

# ---------- geometry dies with the ticket ----------
{
  for f in "$EA/Dataset/Breaklines/Pot_J/"$PIECE"_Breakline_0.pcd" "$EA/Dataset/Breaklines/Pot_J/"$PIECE"_Breakline_1.pcd"; do
    [ -f "$f" ] && md5sum "$f"
  done
  echo "repeat_stage_files=$(find "$RUN/repeat" -type f | wc -l)"
} | tee -a "$RUN/out/geometry.md5"
{
  echo "Ticket 290 follow-up geometry deletion - $(date -u +%Y-%m-%dT%H:%M:%SZ) on $(hostname)"
  echo "DELETED: repeat/ (two mesh-stage trees, two edge-stage trees, their sheets, PLYs and exports)."
  echo "KEPT: logs/mesh_st3.log logs/mesh_st4.log logs/edge_edgeA.log logs/edge_edgeB.log, out/repeat_*.{md5,txt}, logs/repeat290.log"
} >> "$RUN/out/GEOMETRY_DELETED.txt"
rm -rf "$RUN/repeat"
ls -l "$RUN/out" | head -40
say "DONE"
