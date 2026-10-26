#!/usr/bin/env bash
# Ticket 301 -- ONE assembly arm of Pot D, staged and run.  bash p301-arm.sh <RUN_DIR> ctrl|swap [TARGET]
#
# Both arms hand the assembler the authors' corpus Surfaces + Breakline_0 (the "authb" bundle of ticket
# 298), the frozen corpus Mesh and the frozen corpus Ground Truth. The ONE difference:
#   ctrl  every piece gets the corpus Axes/<Piece>_Axis.xyz, symlinked, verbatim.
#   swap  every piece gets the corpus axis EXCEPT <TARGET>, which gets a REAL staged file whose
#         direction fields are +/- R_GT^T . a_world (p301_mkswap.py). The axis POINT columns, the line
#         count and the field order are untouched.
# Nothing else about the assembler, the image, its tolerances, the meshes, the breaklines or any
# tracked source file changes. The pot is selected by flipping the selector in a throwaway copy of the
# pinned tree inside /tmp (p301_inside.sh); the bundle is whatever is bind-mounted at /Dataset/SfS_pp.
set -uo pipefail

RUN=${1:?usage: p301-arm.sh <RUN_DIR> ctrl|swap [TARGET]}
ARM=${2:?usage: p301-arm.sh <RUN_DIR> ctrl|swap [TARGET]}
TARGET=${3:-}
POT=Pot_D
SHARD=29
ASM=/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker
SIF=/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
PY=${PY:-/data/gpfs/projects/punim2657/.conda/envs/graphify/bin/python3}
HERE=$(cd "$(dirname "$0")" && pwd)
DS=$RUN/dataset/SfS_pp
PIECES=$HERE/pieces.txt

case "$ARM" in
  ctrl|swap) ;;
  *) echo "[RUN] FATAL unknown ARM $ARM (ctrl or swap)"; exit 9 ;;
esac
if [ "$ARM" = "swap" ] && [ -z "$TARGET" ]; then echo "[RUN] FATAL swap needs a TARGET piece"; exit 9; fi

mkdir -p "$RUN/logs" "$RUN/out" "$RUN/scripts" "$DS/Breaklines" "$DS/Mesh" "$DS/Axes" \
         "$DS/Surfaces" "$DS/Ground Truth" "$DS/Result"
echo "[RUN] node=$(hostname) job=${SLURM_JOB_ID:-none} start=$(date -Is) pot=$POT arm=$ARM target=${TARGET:-none} shard=$SHARD"
echo "[RUN] pieces: $(wc -l < $PIECES)"
echo "[RUN] surface source: $CORP/Surfaces (the authors' corpus bundle, both arms)"
echo "[RUN] breakline source: $CORP/Breaklines (the authors' corpus bundle, both arms)"
echo "[RUN] SFS_ variables in this environment: $(env | grep -cE '^SFS_' || true) (0 expected)"

# ---------------------------------------------------------------- corpus integrity, before
md5sum "$CORP"/Axes/Pot_D_Piece_*_Axis.xyz | sort -k2 > "$RUN/out/corpus_axes_md5_before.txt"
echo "[RUN] corpus axis files md5ed before staging: $(wc -l < "$RUN/out/corpus_axes_md5_before.txt")"
if [ -n "$TARGET" ]; then
  md5sum "$CORP/Axes/${TARGET}_Axis.xyz" | awk '{print $1}' > "$RUN/out/corpus_target_md5_before.txt"
  echo "[RUN] corpus ${TARGET} axis md5 before: $(cat "$RUN/out/corpus_target_md5_before.txt")"
fi

link_into() { # link_into <target> <staged>
  if [ ! -e "$1" ]; then echo "[RUN] FATAL missing source $1"; exit 10; fi
  if [ -e "$2" ] && [ ! -L "$2" ]; then echo "[RUN] FATAL refusing to replace a real file $2"; exit 10; fi
  ln -sfn "$1" "$2"
  [ -L "$2" ] || { echo "[RUN] FATAL not a symlink $2"; exit 10; }
}

: > "$RUN/out/gt_missing.txt"
while read -r P; do
  [ -n "$P" ] || continue
  if [ -f "$CORP/Mesh/${P}_Mesh.obj" ]; then
    link_into "$CORP/Mesh/${P}_Mesh.obj" "$DS/Mesh/${P}_Mesh.obj"
  else
    link_into "$CORP/Mesh/${P}_Mesh_DS.obj" "$DS/Mesh/${P}_Mesh.obj"
  fi
  link_into "$CORP/Axes/${P}_Axis.xyz" "$DS/Axes/${P}_Axis.xyz"
  link_into "$CORP/Surfaces/${P}_Surface_0.xyz" "$DS/Surfaces/${P}_Surface_0.xyz"
  link_into "$CORP/Surfaces/${P}_Surface_1.xyz" "$DS/Surfaces/${P}_Surface_1.xyz"
  link_into "$CORP/Breaklines/${P}_Breakline_0.pcd" "$DS/Breaklines/${P}_Breakline_0.pcd"
  link_into "$CORP/Breaklines/${P}_Breakline_1.pcd" "$DS/Breaklines/${P}_Breakline_1.pcd"
  # the assembler names Pot_X_Piece_N_T.txt without zero padding
  i=$((10#${P##*_Piece_}))
  if [ -f "$CORP/Ground Truth/${POT}_Piece_${i}_T.txt" ]; then
    link_into "$CORP/Ground Truth/${POT}_Piece_${i}_T.txt" "$DS/Ground Truth/${POT}_Piece_${i}_T.txt"
  else
    printf "%s\t%d\tabsent in the corpus -- Trans::Read leaves the identity\n" "$P" "$i" >> "$RUN/out/gt_missing.txt"
  fi
done < "$PIECES"
link_into "$CORP/Ground Truth/${POT}_simple_graph.txt" "$DS/Ground Truth/${POT}_simple_graph.txt"

# ---------------------------------------------------------------- the one difference between arms
TA="$DS/Axes/${TARGET}_Axis.xyz"
if [ "$ARM" = "ctrl" ]; then
  # ctrl must be the corpus bytes themselves, resolved, with nothing staged over them
  RC=$(readlink -f "$TA")
  if [ "$RC" != "$CORP/Axes/${TARGET}_Axis.xyz" ]; then
    echo "[RUN] FATAL ctrl target axis resolves to $RC, not the corpus file"; exit 13
  fi
  echo "[RUN] ctrl: $(basename "$TA") -> $RC (corpus file, symlink, verbatim)"
  echo "$RC" > "$RUN/out/target_axis_source.txt"
else
  echo "[RUN] swap: replacing the staged symlink with a real file for ${TARGET}"
  rm -f "$TA"
  "$PY" "$HERE/p301_mkswap.py" --constants "$HERE/p301-constants.json" \
      --piece "$((10#${TARGET##*_Piece_}))" --corpus-axis "$CORP/Axes/${TARGET}_Axis.xyz" \
      --gt "$DS/Ground Truth/${POT}_Piece_$((10#${TARGET##*_Piece_}))_T.txt" \
      --out "$TA" --provenance "$RUN/out/swap_provenance.json" || { echo "[RUN] FATAL p301_mkswap.py failed"; exit 14; }
  if [ -L "$TA" ] || [ ! -f "$TA" ]; then echo "[RUN] FATAL $TA is not a real file after the swap"; exit 14; fi
  echo "staged real file $TA" > "$RUN/out/target_axis_source.txt"
fi

: > "$RUN/out/inputs.md5"
for f in "$DS/Mesh/"*.obj "$DS/Axes/"*.xyz "$DS/Surfaces/"*.xyz "$DS/Breaklines/"*.pcd "$DS/Ground Truth/"*; do
  printf "%s\t%s\t%s bytes\n" "$(md5sum "$f" | awk '{print $1}')" "$(readlink -f "$f")" "$(stat -c %s "$f")" >> "$RUN/out/inputs.md5"
done
printf "staged\tresolves to\n" > "$RUN/out/links.tsv"
for f in "$DS/Mesh/"*.obj "$DS/Surfaces/"*.xyz "$DS/Breaklines/"*.pcd; do printf "%s\t%s\n" "$f" "$(readlink -f "$f")" >> "$RUN/out/links.tsv"; done
echo "[RUN] inputs.md5 rows: $(wc -l < "$RUN/out/inputs.md5")"
echo "[RUN] ground-truth transforms absent: $(wc -l < "$RUN/out/gt_missing.txt")"
echo "[RUN] the assembler reads only Breakline_0; _1 is staged inert"

cp -f "$ASM/hpc/tools/main_pristine_batch.cpp" "$RUN/scripts/main_pristine_batch.cpp"
md5sum "$ASM/hpc/tools/main_pristine_batch.cpp" "$SIF" > "$RUN/out/assembler_inputs.md5"
{ for f in "$HERE"/p301-arm.sh "$HERE"/p301_inside.sh "$HERE"/p301_mkswap.py "$HERE"/p301-constants.json "$HERE"/pieces.txt; do
    [ -f "$f" ] && md5sum "$f"; done; } > "$RUN/out/harness_md5.txt"
echo "[RUN] harness md5s:"; cat "$RUN/out/harness_md5.txt"

"$APT" exec --bind /data:/data --bind "$RUN:/p301run" --bind "$ASM:/workspace:ro" --bind "$DS:/Dataset/SfS_pp" "$SIF" \
    env POT="$POT" SHARD="$SHARD" ARM="$ARM" TARGET="$TARGET" bash /p301run/scripts/p301_inside.sh 2>&1 | tee "$RUN/logs/container.log"
echo "[RUN] container pipeline exit ${PIPESTATUS[0]}"

# ---------------------------------------------------------------- corpus integrity, after
md5sum "$CORP"/Axes/Pot_D_Piece_*_Axis.xyz | sort -k2 > "$RUN/out/corpus_axes_md5_after.txt"
if diff -q "$RUN/out/corpus_axes_md5_before.txt" "$RUN/out/corpus_axes_md5_after.txt" > /dev/null; then
  echo "[RUN] corpus axis md5s unchanged by this arm ($(wc -l < "$RUN/out/corpus_axes_md5_after.txt") files)" | tee "$RUN/out/corpus_unchanged.txt"
else
  echo "[RUN] FATAL the corpus axis files changed during this arm" | tee "$RUN/out/corpus_unchanged.txt"; exit 15
fi
if [ -n "$TARGET" ]; then
  md5sum "$CORP/Axes/${TARGET}_Axis.xyz" | awk '{print $1}' > "$RUN/out/corpus_target_md5_after.txt"
  cmp -s "$RUN/out/corpus_target_md5_before.txt" "$RUN/out/corpus_target_md5_after.txt" \
    && echo "[RUN] corpus ${TARGET} axis md5 unchanged: $(cat "$RUN/out/corpus_target_md5_after.txt")" \
    || { echo "[RUN] FATAL corpus ${TARGET} axis changed"; exit 15; }
fi

# Surface_F.pcd is absent from the corpus by design and LoadSurface tolerates it (ticket 296);
# any OTHER unreadable input is a staging failure and must not be read as a seating result.
if grep "Could not open file" "$RUN/logs/assembly.log" 2>/dev/null | grep -qv "_Surface_F.pcd"; then
  echo "[RUN] FATAL the assembler could not open an input file:"
  grep "Could not open file" "$RUN/logs/assembly.log" | grep -v "_Surface_F.pcd" | head -5
  exit 11
fi
if ! grep -qE "Total number : [1-9]" "$RUN/logs/assembly.log" 2>/dev/null; then
  echo "[RUN] FATAL the assembler loaded 0 sherds -- see logs/assembly.log"
  exit 12
fi

mkdir -p "$RUN/out/Result"
cp -pr "$DS/Result/." "$RUN/out/Result/" 2>/dev/null || echo "[RUN] no Result directory to copy"
ls -la "$RUN/out/Result" > "$RUN/out/result_copy_ls.txt" 2>&1 || true
echo "==== $POT $ARM arm (target ${TARGET:-none}) ===="
cat "$RUN/out/summary.txt" 2>/dev/null || echo "[RUN] NO SUMMARY LINES"
echo "[RUN] done $(date -Is)"
