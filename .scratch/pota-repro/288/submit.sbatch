#!/bin/bash
#SBATCH --job-name=p288commit
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=01:00:00

# Ticket 288: build EdgeLineExtractionHeadless from a clean git archive of the COMMITTED seed source
# (main 8e1e514) with the ticket-287 apptainer recipe, then re-run the eight surviving lanes at
# defaults and show they reproduce ticket 287's "after" column. No source change of any kind.
# No mesh stage runs: the frozen theta-3.4 sheets are copied verbatim and their md5 checked.
set -u
RUN=${RUN_DIR:?}
CANON=${CANONICAL:?}
COMMIT=${SOURCE_COMMIT:?}
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SCR=/data/gpfs/projects/punim2657/sfs-vote-248/p288-build-${SLURM_JOB_ID}
PHASE0=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-0408_1308298_p275-phase0/phase0
P280=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1604_d1b61cb_p280-extent/stage
R287=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2046_edf679c_p287-seed
mkdir -p "$RUN/logs" "$RUN/out" "$RUN/bin" "$SCR"
say() { echo "[$(date -u +%H:%M:%S)] $*"; }

say "job $SLURM_JOB_ID on $(hostname) RUN=$RUN"
echo "commit_requested=$COMMIT"
echo "commit_resolved=$(git -C "$CANON" rev-parse "$COMMIT")"
echo "commit_subject=$(git -C "$CANON" log -1 --format=%s "$COMMIT")"
ls -l "$SIF"
"$APT" --version 2>/dev/null | head -2 || true

# ---- Phase 1: build from the committed source, nothing overlaid -------------------------------
say "prepare archive of $COMMIT"
rm -rf "$SCR/src"; mkdir -p "$SCR/src"
git -C "$CANON" archive "$COMMIT" | tar -x -C "$SCR/src"
cp -a "$CANON/alglib" "$SCR/src/"
if [ -d "$CANON/original_nurbs_preprocessing/alglib" ]; then
  mkdir -p "$SCR/src/original_nurbs_preprocessing"
  cp -a "$CANON/original_nurbs_preprocessing/alglib" "$SCR/src/original_nurbs_preprocessing/"
fi
F="$SCR/src/edgeline_extraction_headless.cpp"
echo "source md5_raw=$(md5sum "$F" | cut -d' ' -f1)"
echo "source md5_lf=$(tr -d '\r' < "$F" | md5sum | cut -d' ' -f1)"
echo "source lines=$(wc -l < "$F")"
echo "source SEED287_count=$(grep -c 'SEED-287' "$F")"
echo "source md5 of the 287 after-arm file, for reference: f0dbfe7032d90a04412d15bd1699a703"
echo "archive file matches git blob: $(git -C "$CANON" show "$COMMIT:edgeline_extraction_headless.cpp" | tr -d '\r' | md5sum | cut -d' ' -f1)"
echo "tree clean of local edits: $(cd "$SCR/src" && find . -maxdepth 1 -newer "$SCR/src/CMakeLists.txt" -name '*.cpp' | wc -l) cpp newer than CMakeLists (0 expected)"

say "build from commit ..."
"$APT" exec --bind /data:/data "$SIF" /bin/bash -c "cmake -S '$SCR/src' -B '$SCR/src/build/edge-release' -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON && make -C '$SCR/src/build/edge-release' -j8 EdgeLineExtractionHeadless" > "$RUN/logs/build_commit.log" 2>&1
BE=$?
echo "BUILD_EXIT=$BE"
tail -3 "$RUN/logs/build_commit.log"
if [ "$BE" -ne 0 ]; then echo "=== FIRST COMPILER ERROR ==="; grep -m1 -E 'error:|Error [0-9]' "$RUN/logs/build_commit.log"; exit 1; fi
B="$SCR/src/build/edge-release/EdgeLineExtractionHeadless"
if [ ! -f "$B" ]; then echo "NO BINARY"; exit 1; fi
cp "$B" "$RUN/bin/EdgeLineExtractionHeadless_commit"
echo "binary $(md5sum "$RUN/bin/EdgeLineExtractionHeadless_commit")"
echo "binary_matches_287_after=a28d10afab2b50bbe750d599ee2b7214 -> $( [ "$(md5sum "$B" | cut -d' ' -f1)" = a28d10afab2b50bbe750d599ee2b7214 ] && echo IDENTICAL || echo DIFFERENT )"
for k in STOP-267 FULL-263 VOTE-247 SEED-287; do printf 'strings %s = %s\n' "$k" "$(strings -a "$B" | grep -c -- "$k")"; done
grep -E 'CMAKE_CXX_COMPILER:|CMAKE_CXX_FLAGS:' "$SCR/src/build/edge-release/CMakeCache.txt" 2>/dev/null
python3 - "$SCR/src/build/edge-release/compile_commands.json" "$RUN/logs/compile_cmd.txt" <<'PY'
import json, sys
cc = json.load(open(sys.argv[1]))
for e in cc:
    if e["file"].endswith("/edgeline_extraction_headless.cpp"):
        cmd = e.get("command") or " ".join(e.get("arguments") or [])
        open(sys.argv[2], "w").write("cwd=%s\n%s\n" % (e.get("directory", ""), cmd))
        print("compile_cmd recorded, %d chars" % len(cmd))
        break
PY

# ---- Phase 2: the eight surviving lanes, defaults only ---------------------------------------
run_lane() {
  local lab="$1" stem="$2" pot="$3" src="$4"
  local T="$SCR/run/${lab}_commit"
  local O="$RUN/out/${lab}_commit"
  mkdir -p "$SCR/run" "$O"
  if [ ! -d "$src/Temp/Data/$pot" ]; then echo "SOURCE MISSING [$lab] $src"; return 1; fi
  rm -rf "$T"; cp -a "$src" "$T"
  mkdir -p "$T/Dataset/Breaklines/$pot"
  rm -f "$T/Dataset/Breaklines/$pot"/*.pcd "$T/Dataset/Breaklines/$pot"/*.ply "$T/Dataset/Breaklines/$pot"/*.xyz 2>/dev/null
  rm -rf "$T/Temp/Temp_edge"
  md5sum "$T"/Temp/Data/"$pot"/*_Surface_*.xyz "$T"/Dataset/Axes/*.xyz > "$O/sheets_pre.md5" 2>/dev/null
  ( cd "$T" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$pot" "$RUN/bin/EdgeLineExtractionHeadless_commit" > "$O/edge.log" 2>&1 )
  echo "EDGE_EXIT[$lab]=$?" | tee "$O/exit.txt"
  md5sum "$T"/Temp/Data/"$pot"/*_Surface_*.xyz "$T"/Dataset/Axes/*.xyz > "$O/sheets_post.md5" 2>/dev/null
  if diff -q "$O/sheets_pre.md5" "$O/sheets_post.md5" > /dev/null; then echo "sheets unchanged [$lab]"; else echo "SHEETS CHANGED [$lab]"; fi
  cp "$T/Dataset/Breaklines/$pot"/* "$O"/ 2>/dev/null
  ls -l "$O"/*.pcd 2>/dev/null
  echo "--- $lab: SEED-287 / walk lines ---"
  grep -E 'SEED-287|FULL-263|STOP-267 BEGIN' "$O/edge.log" | head -6
}

say "=== eight lanes at defaults (POT_NAME only) ==="
run_lane H02 Pot_H_Piece_02 Pot_H "$P280/H02_norm"
run_lane H10 Pot_H_Piece_10 Pot_H "$P280/H10_norm"
run_lane C01 Pot_C_Piece_01 Pot_C "$PHASE0/Pot_C_Piece_01"
run_lane J01 Pot_J_Piece_01 Pot_J "$PHASE0/Pot_J_Piece_01"

say "=== scores vs authors, and vs ticket 287's after column ==="
OUT="$RUN/out" REF287="$R287/out" python3 "$RUN/score288.py" 2>&1 | tee "$RUN/out/score288.txt"

say "=== done; node-local build tree at $SCR ==="
