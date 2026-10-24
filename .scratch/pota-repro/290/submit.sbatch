#!/bin/bash
#SBATCH --job-name=p290corp
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=02:00:00
#SBATCH --output=logs/p290_%j.out

# Ticket 290 - the frozen input corpus. Proves the corpus is complete and unchanged, then runs ONE
# piece (Pot J Piece 09) end to end from the released cloud it already holds: no mesh sampling, no
# code change, no default, no threshold. Then shows the lanes reproduce ticket 289 numbers, states
# whether a symlinked Dataset/Point is read, and deletes this run geometry at the end (the corpus
# itself is INPUT and is never touched).
set -u
: "$RUN_DIR"; : "$CANONICAL"; : "$SOURCE_COMMIT"
RUN=$RUN_DIR
CANON=$CANONICAL
COMMIT=$SOURCE_COMMIT
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PYC=/data/gpfs/projects/punim2657/.conda/envs/graphify/bin/python3
SCR=/data/gpfs/projects/punim2657/sfs-vote-248/p290-build-$SLURM_JOB_ID
CORPUS=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
POINT=$CORPUS/Point
PIECE=Pot_J_Piece_09
STAGE=$RUN/stage/P09
STAGE2=$RUN/stage/P09d2
PROBE=$RUN/probe
mkdir -p "$RUN/logs" "$RUN/out/png" "$RUN/bin" "$SCR/src"
say() { echo "[$(date -u +%H:%M:%S)] $*"; }
say "job $SLURM_JOB_ID on $(hostname) RUN=$RUN"
echo "commit_resolved=$(git -C "$CANON" rev-parse "$COMMIT")"
ls -l "$SIF"

# ---------- 1. inventory: is the corpus complete, unchanged, and readable? ----------
say "inventory of $POINT"
"$PYC" "$RUN/inv290.py" > "$RUN/logs/inv290.log" 2>&1
INV_EXIT=$?
echo "INV_EXIT=$INV_EXIT"
grep -E "^\[INV\]|\[FAIL\]" "$RUN/logs/inv290.log" | tee "$RUN/out/inventory.txt"
head -1 "$POINT/MANIFEST_released.tsv" > "$RUN/out/manifest_row_test_piece.txt"
grep -E "^$PIECE" "$POINT/MANIFEST_released.tsv" | head -2 >> "$RUN/out/manifest_row_test_piece.txt"
cat "$RUN/out/manifest_row_test_piece.txt"
md5sum "$POINT/Pot_J/"$PIECE"_Point.pcd" | tee "$RUN/out/inputs.md5"
sed -n "1,14p" "$POINT/Pot_J/"$PIECE"_Point.pcd" | cut -c1-160 | tee "$RUN/out/cloud_header.txt"

# ---------- 2. build both binaries from a pushed commit (node-local scratch) ----------
say "build from git archive $COMMIT"
git -C "$CANON" archive "$COMMIT" | tar -x -C "$SCR/src"
cp -a "$CANON/alglib" "$SCR/src/"
F=$SCR/src/edgeline_extraction_headless.cpp
M=$SCR/src/mesh_processing_headless.cpp
echo "edge_source_md5_lf=$(tr -d '\r' < $F | md5sum | cut -d' ' -f1) lines=$(wc -l < $F) SEED287=$(grep -c 'SEED-287' $F)" | tee "$RUN/out/source.md5"
echo "mesh_source_md5_lf=$(tr -d '\r' < $M | md5sum | cut -d' ' -f1) lines=$(wc -l < $M)" | tee -a "$RUN/out/source.md5"
"$APT" exec --bind /data:/data "$SIF" /bin/bash -c "cmake -S "$SCR/src" -B "$SCR/src/build/edge-release" -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON && make -C "$SCR/src/build/edge-release" -j8 EdgeLineExtractionHeadless MeshPreprocessingHeadless" > "$RUN/logs/build.log" 2>&1
echo "BUILD_EXIT=$?"
tail -3 "$RUN/logs/build.log"
MESH=$SCR/src/build/edge-release/MeshPreprocessingHeadless
EDGEB=$SCR/src/build/edge-release/EdgeLineExtractionHeadless
[ -f "$MESH" ] || { echo "NO MESH BINARY"; exit 11; }
[ -f "$EDGEB" ] || { echo "NO EDGE BINARY"; exit 11; }
md5sum "$EDGEB" "$MESH" | tee "$RUN/out/binaries.md5"
echo "expected_edge_from_8e1e514 a28d10afab2b50bbe750d599ee2b7214" | tee -a "$RUN/out/binaries.md5"
echo "edge_marker_strings=$(strings "$EDGEB" | grep -cE 'SEED-287|STOP-267|FULL-263|VOTE-247')" | tee -a "$RUN/out/binaries.md5"
grep -o '"CMAKE_CXX_COMPILER[^,]*' "$SCR/src/build/edge-release/compile_commands.json" | head -2
cp "$EDGEB" "$RUN/bin/EdgeLineExtractionHeadless"
cp "$MESH" "$RUN/bin/MeshPreprocessingHeadless"
python3 - "$SCR/src/build/edge-release/compile_commands.json" "$RUN/logs/compile_cmd.txt" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
for e in d:
    if e["file"].endswith("edgeline_extraction_headless.cpp"):
        open(sys.argv[2], "w").write(e["command"])
        print("compile_cmd_chars=%d" % len(e["command"]))
        break
PY

# ---------- 3. does the pipeline read a SYMLINKED Dataset/Point? ----------
# A directory symlink means the stage recursive scan sees all 148 pieces, which is what makes the
# answer visible: whatever lands in Temp/Data/Pot_A came from other pots as well.
say "symlink probe (25 s, bounded, inside $PROBE)"
mkdir -p "$PROBE/Dataset/Mesh/Pot_A" "$PROBE/Dataset/Axes" "$PROBE/Dataset/Breaklines/Pot_A" "$PROBE/Temp/Data/Pot_A" "$PROBE/Temp/Temp_edge/Pot_A"
ln -sfn "$POINT" "$PROBE/Dataset/Point"
ls -l "$PROBE/Dataset/Point"
cd "$PROBE" || exit 9
timeout 25 "$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_A "$MESH" > "$RUN/logs/probe.log" 2>&1
echo "PROBE_EXIT=$? (124 = stopped by the timeout, so it was still enumerating)"
ls -1 "$PROBE/Temp/Data/Pot_A" | head -20 > "$RUN/out/probe_copied.txt"
echo "probe_files_copied=$(ls -1 "$PROBE/Temp/Data/Pot_A" | wc -l)" >> "$RUN/out/probe_copied.txt"
echo "distinct_pots_seen=$(ls -1 "$PROBE/Temp/Data/Pot_A" | sed -E 's/_Piece_[0-9]+_Point\.pcd//' | sort -u | tr '\n' ' ')" >> "$RUN/out/probe_copied.txt"
sed -n "1,8p" "$RUN/logs/probe.log" >> "$RUN/out/probe_copied.txt"
cat "$RUN/out/probe_copied.txt"

# ---------- 4. the real run: the released cloud, through a file-level symlink ----------
say "stage the one piece (file-level symlink into the corpus)"
mkdir -p "$STAGE/Dataset/Point/Pot_J" "$STAGE/Dataset/Mesh/Pot_J" "$STAGE/Dataset/Axes"
mkdir -p "$STAGE/Dataset/Breaklines/Pot_J" "$STAGE/Temp/Data/Pot_J" "$STAGE/Temp/Temp_edge/Pot_J"
ln -sfn "$POINT/Pot_J/"$PIECE"_Point.pcd" "$STAGE/Dataset/Point/Pot_J/"$PIECE"_Point.pcd"
ls -l "$STAGE/Dataset/Point/Pot_J"
cp "$CORPUS/Mesh/"$PIECE"_Mesh_DS.obj" "$STAGE/Dataset/Mesh/Pot_J/"$PIECE"_Mesh.obj"
cp "$CORPUS/Axes/"$PIECE"_Axis.xyz" "$STAGE/Dataset/Axes/"
md5sum "$STAGE/Dataset/Mesh/Pot_J/"$PIECE"_Mesh.obj" "$STAGE/Dataset/Axes/"$PIECE"_Axis.xyz" | tee -a "$RUN/out/inputs.md5"

say "mesh stage (no CloudCompare, no sampling: the cloud is the frozen one)"
cd "$STAGE" || exit 9
"$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_J SFS_AXIS_FILE="$STAGE/Dataset/Axes/"$PIECE"_Axis.xyz" "$MESH" > "$RUN/logs/mesh.log" 2>&1
echo "MESH_EXIT=$?"
grep -E "PAPER-234\] classify" "$RUN/logs/mesh.log" | head -3 > "$RUN/out/key_lines.txt"
grep -m1 "SPLITTER-234" "$RUN/logs/mesh.log" >> "$RUN/out/key_lines.txt"
grep -m1 "PAPER-234\] paper grow" "$RUN/logs/mesh.log" >> "$RUN/out/key_lines.txt"
grep -E "Point.pcd|cleanSamples|pointCloudFromMesh" "$RUN/logs/mesh.log" | head -6 >> "$RUN/out/key_lines.txt"
cat "$RUN/out/key_lines.txt"
for st in 0 1; do
  f=Temp/Data/Pot_J/"$PIECE"_Surface_$st.xyz
  [ -f "$f" ] || { echo "NO SHEET $f"; tail -30 "$RUN/logs/mesh.log"; exit 13; }
done
md5sum Temp/Data/Pot_J/"$PIECE"_Surface_0.xyz Temp/Data/Pot_J/"$PIECE"_Surface_1.xyz | tee "$RUN/out/sheets.md5"
wc -l Temp/Data/Pot_J/"$PIECE"_Surface_0.xyz Temp/Data/Pot_J/"$PIECE"_Surface_1.xyz

say "edge stage at shipped defaults"
rm -f Dataset/Breaklines/Pot_J/*.pcd Dataset/Breaklines/Pot_J/*.xyz
"$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_J "$RUN/bin/EdgeLineExtractionHeadless" > "$RUN/logs/edge.log" 2>&1
echo "EDGE_EXIT=$?"
grep -E "SEED-287|FULL-263|CHAIN-END" "$RUN/logs/edge.log" | head -20 >> "$RUN/out/key_lines.txt"
for st in 0 1; do
  src=Dataset/Breaklines/Pot_J/"$PIECE"_Breakline_$st.pcd
  cp "$src" "$RUN/out/lane$st.pcd" || { echo "NO LANE $st"; exit 14; }
done
cp Temp/Data/Pot_J/"$PIECE"_Surface_0.xyz "$RUN/out/surface_0.xyz"
cp Temp/Data/Pot_J/"$PIECE"_Surface_1.xyz "$RUN/out/surface_1.xyz"
md5sum "$RUN/out/lane0.pcd" "$RUN/out/lane1.pcd" | tee "$RUN/out/lanes.md5"

# ---------- 5. determinism: the same sheets and cloud again, in a clean tree ----------
say "repeat the edge stage in a clean tree (same Temp/Data inputs)"
mkdir -p "$STAGE2/Dataset/Point/Pot_J" "$STAGE2/Dataset/Axes" "$STAGE2/Dataset/Breaklines/Pot_J" "$STAGE2/Temp/Data/Pot_J" "$STAGE2/Temp/Temp_edge/Pot_J"
ln -sfn "$POINT/Pot_J/"$PIECE"_Point.pcd" "$STAGE2/Dataset/Point/Pot_J/"$PIECE"_Point.pcd"
cp "$STAGE/Dataset/Axes/"$PIECE"_Axis.xyz" "$STAGE2/Dataset/Axes/"
cp "$STAGE/Dataset/Mesh/Pot_J/"$PIECE"_Mesh.obj" "$STAGE2/Temp/Data/Pot_J/"$PIECE"_Mesh.obj"
cp "$STAGE/Temp/Data/Pot_J/"$PIECE"_Surface_0.xyz" "$STAGE/Temp/Data/Pot_J/"$PIECE"_Surface_1.xyz" "$STAGE2/Temp/Data/Pot_J/"
cd "$STAGE2" || exit 9
"$APT" exec --bind /data:/data "$SIF" env POT_NAME=Pot_J "$RUN/bin/EdgeLineExtractionHeadless" > "$RUN/logs/edge2.log" 2>&1
echo "EDGE2_EXIT=$?"
md5sum "$STAGE2/Dataset/Breaklines/Pot_J/"*.pcd | tee "$RUN/out/lanes2.md5"
if [ "$(md5sum "$STAGE2/Dataset/Breaklines/Pot_J/"$PIECE"_Breakline_0.pcd" | cut -d' ' -f1)" = "$(md5sum "$RUN/out/lane0.pcd" | cut -d' ' -f1)" ] && [ "$(md5sum "$STAGE2/Dataset/Breaklines/Pot_J/"$PIECE"_Breakline_1.pcd" | cut -d' ' -f1)" = "$(md5sum "$RUN/out/lane1.pcd" | cut -d' ' -f1)" ]; then echo "repeat_identical_to_first=YES"; else echo "repeat_identical_to_first=NO"; fi | tee "$RUN/out/determinism.txt"
echo "edge2_seed287_lines=$(grep -c 'SEED-287' "$RUN/logs/edge2.log")" | tee -a "$RUN/out/determinism.txt"

# ---------- 6. score both lanes and draw the overlay ----------
say "score + picture"
"$PYC" "$RUN/score290.py" "$RUN" > "$RUN/logs/score290.log" 2>&1
SCORE_EXIT=$?
echo "SCORE_EXIT=$SCORE_EXIT"
cat "$RUN/logs/score290.log"

# ---------- 7. geometry dies with the ticket ----------
say "record then delete this run geometry"
{
  for f in "$RUN/out/lane0.pcd" "$RUN/out/lane1.pcd" "$RUN/out/surface_0.xyz" "$RUN/out/surface_1.xyz"; do
    [ -f "$f" ] && md5sum "$f"
  done
  echo "stage_files_total=$(find "$STAGE" "$STAGE2" "$PROBE" -type f | wc -l)"
} | tee "$RUN/out/geometry.md5"
{
  echo "Ticket 290 geometry deletion - $(date -u +%Y-%m-%dT%H:%M:%SZ) on $(hostname)"
  echo "Rule: geometry dies with its ticket (workspace AGENTS.md; conservator 2026-10-24)."
  echo "DELETED (md5 and size recorded in out/geometry.md5 immediately before deletion):"
  echo "  out/lane0.pcd out/lane1.pcd          this run two exported breaklines (the scored geometry)"
  echo "  out/surface_0.xyz out/surface_1.xyz  the kept faces (picture source)"
  echo "  stage/P09 stage/P09d2 probe/          staging trees, copied mesh, sheets and Temp products"
  echo "  $SCR  node-local build tree (binaries kept in bin/)"
  echo "KEPT (record): run.json, submit.sbatch, inv290.py, score290.py, logs/, out/*.txt, out/*.md5, out/png/, bin/"
  echo "NOT DELETED: the frozen input corpus $POINT (INPUT); the released Mesh/Axes (INPUT);"
  echo "  ticket 289 exported lanes under runs/20261024-2151_8e1e514_p289-p09 (ticket 289 owns them)."
} > "$RUN/out/GEOMETRY_DELETED.txt"
rm -f "$RUN/out/lane0.pcd" "$RUN/out/lane1.pcd" "$RUN/out/surface_0.xyz" "$RUN/out/surface_1.xyz"
rm -rf "$STAGE" "$STAGE2" "$PROBE"
rm -rf "$SCR"
echo "out_after_delete:"; ls -l "$RUN/out"
say "DONE"
