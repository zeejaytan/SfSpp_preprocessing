#!/bin/bash
#SBATCH --job-name=p287seed
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00

# Ticket 287 reduced gate: build BEFORE (edf679c as pushed) and AFTER (same archive + the one
# changed edgeline_extraction_headless.cpp from $RUN/after/), then run the eight lanes whose
# frozen theta-3.4 sheet pairs still exist, then score with the project scorer.
# No mesh stage runs here: the sheets are copied verbatim and their md5 is checked before/after.
set -u
RUN=${RUN_DIR:?}
CANON=${CANONICAL:?}
COMMIT=${SOURCE_COMMIT:?}
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SCR=/data/gpfs/projects/punim2657/sfs-vote-248/p287-build-${SLURM_JOB_ID}
PHASE0=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-0408_1308298_p275-phase0/phase0
P280=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1604_d1b61cb_p280-extent/stage
mkdir -p "$RUN/logs" "$RUN/out" "$RUN/bin" "$SCR"
say() { echo "[$(date -u +%H:%M:%S)] $*"; }

say "job $SLURM_JOB_ID on $(hostname) RUN=$RUN"
echo "commit_resolved=$(git -C "$CANON" rev-parse "$COMMIT")"
ls -l "$SIF"
"$APT" --version 2>/dev/null | head -2 || true

prepare() {
  local tag="$1"
  rm -rf "$SCR/$tag"; mkdir -p "$SCR/$tag"
  git -C "$CANON" archive "$COMMIT" | tar -x -C "$SCR/$tag"
  cp -a "$CANON/alglib" "$SCR/$tag/"
  if [ -d "$CANON/original_nurbs_preprocessing/alglib" ]; then
    mkdir -p "$SCR/$tag/original_nurbs_preprocessing"
    cp -a "$CANON/original_nurbs_preprocessing/alglib" "$SCR/$tag/original_nurbs_preprocessing/"
  else
    echo "note: no original_nurbs_preprocessing/alglib (p280's second cp is a no-op; the legacy source is not built here)"
  fi
  if [ "$tag" = after ]; then
    cp -f "$RUN/after/edgeline_extraction_headless.cpp" "$SCR/$tag/edgeline_extraction_headless.cpp"
  fi
  local f="$SCR/$tag/edgeline_extraction_headless.cpp"
  say "source[$tag] md5_raw=$(md5sum "$f" | cut -d' ' -f1) md5_lf=$(tr -d '\r' < "$f" | md5sum | cut -d' ' -f1) lines=$(wc -l < "$f") SEED287_count=$(grep -c 'SEED-287' "$f")"
}

build() {
  local tag="$1"
  say "build $tag ..."
  "$APT" exec --bind /data:/data "$SIF" /bin/bash -c "cmake -S '$SCR/$tag' -B '$SCR/$tag/build/edge-release' -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON && make -C '$SCR/$tag/build/edge-release' -j8 EdgeLineExtractionHeadless" > "$RUN/logs/build_$tag.log" 2>&1
  echo "BUILD_EXIT[$tag]=$?"
  tail -3 "$RUN/logs/build_$tag.log"
  local B="$SCR/$tag/build/edge-release/EdgeLineExtractionHeadless"
  if [ ! -f "$B" ]; then echo "NO BINARY [$tag]"; return 1; fi
  cp "$B" "$RUN/bin/EdgeLineExtractionHeadless_$tag"
  echo "binary[$tag] $(md5sum "$RUN/bin/EdgeLineExtractionHeadless_$tag")"
  for k in STOP-267 FULL-263 VOTE-247 SEED-287; do printf 'strings %s = %s\n' "$k" "$(strings -a "$B" | grep -c -- "$k")"; done
  grep -E 'CMAKE_CXX_COMPILER:|CMAKE_CXX_FLAGS:' "$SCR/$tag/build/edge-release/CMakeCache.txt" 2>/dev/null
  python3 - "$SCR/$tag/build/edge-release/compile_commands.json" "$RUN/logs/compile_cmd_$tag.txt" <<'PY'
import json, sys
cc = json.load(open(sys.argv[1]))
for e in cc:
    if e["file"].endswith("/edgeline_extraction_headless.cpp"):
        cmd = e.get("command") or " ".join(e.get("arguments") or [])
        open(sys.argv[2], "w").write("cwd=%s\n%s\n" % (e.get("directory", ""), cmd))
        print("compile_cmd[$tag] recorded, %d chars" % len(cmd))
        break
PY
}

run_lane() {
  local lab="$1" stem="$2" pot="$3" src="$4" arm="$5"
  local T="$SCR/run/${lab}_${arm}"
  local O="$RUN/out/${lab}_${arm}"
  mkdir -p "$O"
  if [ ! -d "$src/Temp/Data/$pot" ]; then echo "SOURCE MISSING [$lab] $src"; return 1; fi
  rm -rf "$T"; cp -a "$src" "$T"
  mkdir -p "$T/Dataset/Breaklines/$pot"
  rm -f "$T/Dataset/Breaklines/$pot"/*.pcd "$T/Dataset/Breaklines/$pot"/*.ply "$T/Dataset/Breaklines/$pot"/*.xyz 2>/dev/null
  rm -rf "$T/Temp/Temp_edge"
  md5sum "$T"/Temp/Data/"$pot"/*_Surface_*.xyz "$T"/Dataset/Axes/*.xyz > "$O/sheets_pre.md5" 2>/dev/null
  ( cd "$T" && "$APT" exec --bind /data:/data "$SIF" env POT_NAME="$pot" "$RUN/bin/EdgeLineExtractionHeadless_$arm" > "$O/edge.log" 2>&1 )
  echo "EDGE_EXIT[$lab $arm]=$?" | tee "$O/exit.txt"
  md5sum "$T"/Temp/Data/"$pot"/*_Surface_*.xyz "$T"/Dataset/Axes/*.xyz > "$O/sheets_post.md5" 2>/dev/null
  if diff -q "$O/sheets_pre.md5" "$O/sheets_post.md5" > /dev/null; then echo "sheets unchanged [$lab $arm]"; else echo "SHEETS CHANGED [$lab $arm]"; fi
  cat "$O/sheets_pre.md5"
  cp "$T/Dataset/Breaklines/$pot"/* "$O"/ 2>/dev/null
  ls -l "$O"/*.pcd 2>/dev/null
  echo "--- $lab $arm: seed / walk lines ---"
  grep -E 'FULL-263|SEED-287|STOP-267 BEGIN|VOTE-247' "$O/edge.log" | head -8
}

for arm in before after; do
  prepare "$arm" || exit 1
  build "$arm" || exit 1
done

say "=== eight lanes (before, after) ==="
for arm in before after; do
  run_lane H02 Pot_H_Piece_02 Pot_H "$P280/H02_norm" "$arm"
  run_lane H10 Pot_H_Piece_10 Pot_H "$P280/H10_norm" "$arm"
  run_lane C01 Pot_C_Piece_01 Pot_C "$PHASE0/Pot_C_Piece_01" "$arm"
  run_lane J01 Pot_J_Piece_01 Pot_J "$PHASE0/Pot_J_Piece_01" "$arm"
done

say "=== scores ==="
OUT="$RUN/out" python3 "$RUN/score287.py" 2>&1 | tee "$RUN/out/score287.txt"

say "=== done; scratch left at $SCR (node-local build tree) ==="
