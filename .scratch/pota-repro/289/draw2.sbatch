#!/bin/bash
#SBATCH --job-name=p289d2
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=01:00:00
#SBATCH --output=logs/p289d2_%j.out

# Ticket 289, second half. Job 1 (33747056) already made draw 1 and the edge exports, but the
# analysis died on a missing matplotlib in the job PATH; the pipeline itself was clean.
# This job: (a) run the analysis on draw 1 with the conda interpreter that has numpy+matplotlib,
# (b) take a SECOND independent draw of the same mesh through the same binaries and flags,
# (c) print the two draws side by side with the distance between the exported lines.
# No code change, no default, no threshold, no SFS_* retune, nothing outside $RUN touched.
set -u
: "$RUN_DIR"; : "$CANONICAL"
RUN=$RUN_DIR
CANON=$CANONICAL
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/.conda/envs/graphify/bin/python3
SHIP=/data/gpfs/projects/punim2657/sfs-vote-248/p288-build-33746506/src/build/edge-release/EdgeLineExtractionHeadless
MESH=$RUN/bin/MeshPreprocessingHeadless
ST1=$RUN/stage/P09
ST2=$RUN/stage/P09d2
AUTHB=/data/gpfs/projects/punim2657/sfs_main/original_samples_backup/SfS_pp
say() { echo "[$(date -u +%H:%M:%S)] $*"; }
cd "$RUN" || exit 9
mkdir -p out/d1 out/d2

say "job $SLURM_JOB_ID on $(hostname)"
$PY -c "import numpy, matplotlib; print('numpy', numpy.__version__, 'mpl', matplotlib.__version__)" || exit 10
md5sum "$MESH" "$SHIP" | tee out/binaries_reused.md5
echo "SHIP_EXPECTED=a28d10afab2b50bbe750d599ee2b7214"
grep -m1 "^POINTS" "$ST1/Dataset/Point/Pot_J/Pot_J_Piece_09_Point.pcd"
md5sum "$ST1/Dataset/Point/Pot_J/Pot_J_Piece_09_Point.pcd" | tee out/draws.md5

# ---------- A. draw 1: score, decompose, draw the pictures (matplotlib now present) ----------
say "analysis on draw 1"
$PY a289.py "$RUN" 2>&1 | tee logs/a289_d1.log
echo "A289_D1_EXIT=${PIPESTATUS[0]}"

# ---------- B. keep draw 1 as a draw ----------
cp out/Pot_J_Piece_09_Breakline_0.pcd out/d1/lane0.pcd
cp out/Pot_J_Piece_09_Breakline_1.pcd out/d1/lane1.pcd
cp out/cloud.pcd out/d1/cloud.pcd
md5sum out/d1/*.pcd | tee -a out/draws.md5

# ---------- C. draw 2: same mesh, same flags, new sample ----------
say "draw 2: derive the cloud again"
mkdir -p "$ST2/Dataset/Point/Pot_J" "$ST2/Dataset/Mesh/Pot_J" "$ST2/Dataset/Axes"
mkdir -p "$ST2/Dataset/Breaklines/Pot_J" "$ST2/Temp/Data/Pot_J" "$ST2/Temp/Temp_edge/Pot_J"
cp "$AUTHB/Mesh/Pot_J_Piece_09_Mesh_DS.obj" "$ST2/Dataset/Mesh/Pot_J/Pot_J_Piece_09_Mesh.obj"
cp "$AUTHB/Axes/Pot_J_Piece_09_Axis.xyz" "$ST2/Dataset/Axes/"
md5sum "$ST2/Dataset/Mesh/Pot_J/Pot_J_Piece_09_Mesh.obj" "$ST2/Dataset/Axes/Pot_J_Piece_09_Axis.xyz" | tee -a out/draws.md5
cd "$ST2" || exit 9
bash "$CANON/cc_mesh_to_pcd.sh" -i "$ST2/Dataset/Mesh/Pot_J/Pot_J_Piece_09_Mesh.obj" -o "$ST2/Dataset/Point/Pot_J" -m 1000000 -n medium -f > "$RUN/logs/cc2.log" 2>&1
echo "CC2_EXIT=$?"
grep -E "BBOX_|POINTS=" "$RUN/logs/cc2.log" | tail -5
if [ ! -f "$ST2/Dataset/Point/Pot_J/Pot_J_Piece_09_Point.pcd" ]; then echo "NO CLOUD 2"; tail -20 "$RUN/logs/cc2.log"; exit 12; fi
cp "$ST2/Dataset/Point/Pot_J/Pot_J_Piece_09_Point.pcd" "$RUN/out/d2/cloud.pcd"
grep -m1 "^POINTS" "$RUN/out/d2/cloud.pcd"
md5sum "$RUN/out/d2/cloud.pcd" | tee -a "$RUN/out/draws.md5"

say "draw 2: mesh stage"
"$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_J SFS_AXIS_FILE="$ST2/Dataset/Axes/Pot_J_Piece_09_Axis.xyz" "$MESH" > "$RUN/logs/mesh2.log" 2>&1
echo "MESH2_EXIT=$?"
grep "PAPER-234\] classify" "$RUN/logs/mesh2.log" | head -3 | tee "$RUN/out/key_lines_d2.txt"
for f in Temp/Data/Pot_J/Pot_J_Piece_09_Surface_0.xyz Temp/Data/Pot_J/Pot_J_Piece_09_Surface_1.xyz; do if [ ! -f "$f" ]; then echo "NO SHEET2 $f"; exit 13; fi; done
md5sum Temp/Data/Pot_J/Pot_J_Piece_09_Surface_0.xyz Temp/Data/Pot_J/Pot_J_Piece_09_Surface_1.xyz | tee "$RUN/out/sheets_d2.md5"

say "draw 2: edge stage"
rm -f Dataset/Breaklines/Pot_J/*.pcd Dataset/Breaklines/Pot_J/*.xyz
"$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_J "$SHIP" > "$RUN/logs/edge2.log" 2>&1
echo "EDGE2_EXIT=$?"
grep -E "SEED-287|FULL-263|STOP-267 BEGIN" "$RUN/logs/edge2.log" | head -20 | tee -a "$RUN/out/key_lines_d2.txt"
cp Dataset/Breaklines/Pot_J/Pot_J_Piece_09_Breakline_0.pcd "$RUN/out/d2/lane0.pcd"
cp Dataset/Breaklines/Pot_J/Pot_J_Piece_09_Breakline_1.pcd "$RUN/out/d2/lane1.pcd"
cp Temp/Data/Pot_J/Pot_J_Piece_09_Surface_0.xyz "$RUN/out/d2/Surface_0.xyz"
cp Temp/Data/Pot_J/Pot_J_Piece_09_Surface_1.xyz "$RUN/out/d2/Surface_1.xyz"
for f in boundary.pcd boundaryImproved.pcd cloud_Filtered.pcd cloudBreaklinePointsOnBSplineSurface.pcd CompleteBreakline.pcd; do
  if [ -f "Temp/Temp_edge/Pot_J/$f" ]; then cp "Temp/Temp_edge/Pot_J/$f" "$RUN/out/d2/"; fi
done
md5sum "$RUN"/out/d2/*.pcd | tee -a "$RUN/out/draws.md5"

# ---------- D. the two draws side by side ----------
say "two-draw comparison"
cd "$RUN" || exit 9
$PY a289d.py "$RUN" 2>&1 | tee logs/a289d.log
echo "A289D_EXIT=${PIPESTATUS[0]}"

$PY - "$RUN" <<'PY'
import struct, glob, os, sys
for p in sorted(glob.glob(os.path.join(sys.argv[1], "out/png/*.png"))):
    d = open(p, "rb").read(33)
    w, h = struct.unpack(">II", d[16:24])
    print("[PX] %s %dx%d %d bytes" % (os.path.basename(p), w, h, os.path.getsize(p)))
PY
echo DONE
