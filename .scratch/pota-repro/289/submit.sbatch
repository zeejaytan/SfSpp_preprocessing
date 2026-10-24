#!/bin/bash
#SBATCH --job-name=p289p09
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --output=logs/p289_%j.out

# Ticket 289 - Pot J 09, picture first. One piece, no code change, no default, no threshold,
# no sweep. Steps: build the mesh-stage binary from git archive of the shipped commit (the
# shipped EDGE binary already exists and is reused as-is), derive the input cloud from the only
# surviving (DS) mesh with cc_mesh_to_pcd.sh, run the mesh stage with SFS_AXIS_FILE set, run both
# lanes at shipped defaults, score with the project scorer, decompose the length excess along the
# pipeline stages, and draw the picture set. Everything written lives inside $RUN.
set -u
: "$RUN_DIR"; : "$CANONICAL"; : "$SOURCE_COMMIT"
RUN=$RUN_DIR
CANON=$CANONICAL
COMMIT=$SOURCE_COMMIT
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SCR=/data/gpfs/projects/punim2657/sfs-vote-248/p289-build-$SLURM_JOB_ID
SHIP=/data/gpfs/projects/punim2657/sfs-vote-248/p288-build-33746506/src/build/edge-release/EdgeLineExtractionHeadless
AUTHB=/data/gpfs/projects/punim2657/sfs_main/original_samples_backup/SfS_pp
AUTHO=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
STAGE=$RUN/stage/P09
mkdir -p "$RUN/logs" "$RUN/out" "$RUN/bin" "$SCR/src"
say() { echo "[$(date -u +%H:%M:%S)] $*"; }

say "job $SLURM_JOB_ID on $(hostname) RUN=$RUN"
echo "commit_resolved=$(git -C "$CANON" rev-parse "$COMMIT")"
ls -l "$SIF" "$SHIP"

# ---------- 1. build the mesh stage from the shipped commit (node-local scratch) ----------
git -C "$CANON" archive "$COMMIT" | tar -x -C "$SCR/src"
cp -a "$CANON/alglib" "$SCR/src/"
F=$SCR/src/edgeline_extraction_headless.cpp
say "source md5_lf=$(tr -d "\r" < $F | md5sum | cut -d" " -f1) lines=$(wc -l < $F) SEED287_count=$(grep -c "SEED-287" $F)"
"$APT" exec --bind /data:/data "$SIF" /bin/bash -c "cmake -S "$SCR/src" -B "$SCR/src/build/edge-release" -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON && make -C "$SCR/src/build/edge-release" -j8 EdgeLineExtractionHeadless MeshPreprocessingHeadless" > "$RUN/logs/build.log" 2>&1
echo "BUILD_EXIT=$?"
tail -3 "$RUN/logs/build.log"
MESH=$SCR/src/build/edge-release/MeshPreprocessingHeadless
EDGEB=$SCR/src/build/edge-release/EdgeLineExtractionHeadless
if [ ! -f "$MESH" ]; then echo "NO MESH BINARY"; exit 11; fi
md5sum "$MESH" "$EDGEB" "$SHIP" | tee "$RUN/out/binaries.md5"
cp "$MESH" "$RUN/bin/MeshPreprocessingHeadless"
SHIPMD5=$(md5sum "$SHIP" | cut -d" " -f1)
echo "SHIPPED_EDGE_MD5=$SHIPMD5 EXPECTED=a28d10afab2b50bbe750d599ee2b7214"

# ---------- 2. stage: only the DS mesh survives for this piece ----------
mkdir -p "$STAGE/Dataset/Point/Pot_J" "$STAGE/Dataset/Mesh/Pot_J" "$STAGE/Dataset/Axes"
mkdir -p "$STAGE/Dataset/Breaklines/Pot_J" "$STAGE/Temp/Data/Pot_J" "$STAGE/Temp/Temp_edge/Pot_J"
cp "$AUTHB/Mesh/Pot_J_Piece_09_Mesh_DS.obj" "$STAGE/Dataset/Mesh/Pot_J/Pot_J_Piece_09_Mesh.obj"
cp "$AUTHB/Axes/Pot_J_Piece_09_Axis.xyz" "$STAGE/Dataset/Axes/"
md5sum "$STAGE/Dataset/Mesh/Pot_J/Pot_J_Piece_09_Mesh.obj" "$STAGE/Dataset/Axes/Pot_J_Piece_09_Axis.xyz" | tee -a "$RUN/out/inputs.md5"

say "derive the cloud (CloudCompare sampler; unseeded, so this cloud is a new draw)"
set +u
source /usr/share/modules/init/bash
module load GCC/11.3.0 OpenMPI/4.1.4 CloudCompare/2.12.4
set -u
export QT_QPA_PLATFORM=offscreen
bash "$CANON/cc_mesh_to_pcd.sh" -i "$STAGE/Dataset/Mesh/Pot_J/Pot_J_Piece_09_Mesh.obj" -o "$STAGE/Dataset/Point/Pot_J" -m 1000000 -n medium -f > "$RUN/logs/cc.log" 2>&1
CC_EXIT=$?
echo "CC_EXIT=$CC_EXIT"
grep -E "BBOX_|POINTS=|Status:" "$RUN/logs/cc.log" | tail -8
if [ ! -f "$STAGE/Dataset/Point/Pot_J/Pot_J_Piece_09_Point.pcd" ]; then echo "NO CLOUD - cc failed"; tail -20 "$RUN/logs/cc.log"; exit 12; fi
cp "$STAGE/Dataset/Point/Pot_J/Pot_J_Piece_09_Point.pcd" "$RUN/out/cloud.pcd"
md5sum "$RUN/out/cloud.pcd" | tee -a "$RUN/out/inputs.md5"
grep -m1 "^POINTS" "$RUN/out/cloud.pcd"

# ---------- 3. mesh stage at shipped defaults, axis file set ----------
say "mesh stage"
cd "$STAGE" || exit 9
"$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_J SFS_AXIS_FILE="$STAGE/Dataset/Axes/Pot_J_Piece_09_Axis.xyz" "$MESH" > "$RUN/logs/mesh.log" 2>&1
echo "MESH_EXIT=$?"
grep "PAPER-234\] classify" "$RUN/logs/mesh.log" | head -3 | tee "$RUN/out/key_lines.txt"
grep -m1 "SPLITTER-234" "$RUN/logs/mesh.log" | tee -a "$RUN/out/key_lines.txt"
for f in Temp/Data/Pot_J/Pot_J_Piece_09_Surface_0.xyz Temp/Data/Pot_J/Pot_J_Piece_09_Surface_1.xyz; do if [ ! -f "$f" ]; then echo "NO SHEET $f"; exit 13; fi; done
grep -m1 "PAPER-234\] paper grow" "$RUN/logs/mesh.log" | tee -a "$RUN/out/key_lines.txt"
md5sum Temp/Data/Pot_J/Pot_J_Piece_09_Surface_0.xyz Temp/Data/Pot_J/Pot_J_Piece_09_Surface_1.xyz | tee "$RUN/out/sheets.md5"
wc -l Temp/Data/Pot_J/Pot_J_Piece_09_Surface_0.xyz Temp/Data/Pot_J/Pot_J_Piece_09_Surface_1.xyz

# ---------- 4. both lanes on the shipped edge binary ----------
say "edge stage, shipped binary"
rm -f Dataset/Breaklines/Pot_J/*.pcd Dataset/Breaklines/Pot_J/*.xyz
"$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_J "$SHIP" > "$RUN/logs/edge.log" 2>&1
echo "EDGE_EXIT=$?"
grep -E "SEED-287|FULL-263|STOP-267 BEGIN" "$RUN/logs/edge.log" | head -20 | tee -a "$RUN/out/key_lines.txt"
cp Dataset/Breaklines/Pot_J/Pot_J_Piece_09_Breakline_0.pcd "$RUN/out/"
cp Dataset/Breaklines/Pot_J/Pot_J_Piece_09_Breakline_1.pcd "$RUN/out/"
cp Temp/Data/Pot_J/Pot_J_Piece_09_Surface_0.xyz Temp/Data/Pot_J/Pot_J_Piece_09_Surface_1.xyz "$RUN/out/"
for f in boundary.pcd boundaryImproved.pcd boundary_S0.pcd boundary_S1.pcd cloudBreaklinePointsOnBSplineSurface.pcd cloud_Filtered.pcd CompleteBreakline.pcd; do
  if [ -f "Temp/Temp_edge/Pot_J/$f" ]; then cp "Temp/Temp_edge/Pot_J/$f" "$RUN/out/"; fi
done
ls -l "$RUN/out" | head -20

# ---------- 5. the authors lanes: the backup and the original tree, md5-checked ----------
cp "$AUTHB/Breaklines/Pot_J_Piece_09_Breakline_0.pcd" "$RUN/out/authB_0.pcd"
cp "$AUTHB/Breaklines/Pot_J_Piece_09_Breakline_1.pcd" "$RUN/out/authB_1.pcd"
cp "$AUTHO/Breaklines/Pot_J_Piece_09_Breakline_0.pcd" "$RUN/out/authO_0.pcd"
cp "$AUTHO/Breaklines/Pot_J_Piece_09_Breakline_1.pcd" "$RUN/out/authO_1.pcd"
md5sum "$RUN/out/auth"*.pcd | tee "$RUN/out/auth.md5"

# ---------- 6. score, decompose, draw ----------
say "score + pictures"
python3 "$RUN/a289.py" "$RUN" 2>&1 | tee "$RUN/logs/a289.log"
echo "A289_EXIT=$?"
python3 - "$RUN" <<'PY'
import struct, glob, os, sys
for p in sorted(glob.glob(os.path.join(sys.argv[1], "out/png/*.png"))):
    d = open(p, "rb").read(33)
    w, h = struct.unpack(">II", d[16:24])
    print("[PX] %s %dx%d %d bytes" % (os.path.basename(p), w, h, os.path.getsize(p)))
PY
echo DONE
