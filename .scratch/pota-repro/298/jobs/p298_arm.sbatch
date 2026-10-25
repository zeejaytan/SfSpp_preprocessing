#!/usr/bin/env bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --job-name=p298arm
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=logs/slurm-%j.out
#
# Ticket 298 assembly arm, one pot one arm per job. ARM=oursd: our Surfaces + our Breakline_0
# (from the p298-prep run of this pot). ARM=authb: the authors' corpus Surfaces + corpus
# Breakline_0. Mesh, axis and ground truth are the same frozen corpus files, symlinked, in both
# arms -- the only difference between the two arms is the bundle. The pinned assembler
# (/opt/sfs-pristine, upstream 9195c016) is NOT edited: the pot is chosen by flipping the
# selector in a throwaway copy of the pinned tree inside /tmp, and the arm is chosen by what is
# mounted at /Dataset/SfS_pp.
set -uo pipefail

: ${RUN_DIR:?RUN_DIR must be exported}
: ${POT:?POT must be exported}
: ${SHARD:?SHARD must be exported (SHARD_NUMBER of the pot block)}
: ${ARM:?ARM must be oursd or authb}
: ${PREP_RUN:?PREP_RUN must be exported: the p298-prep run dir of this pot}
RUN=$RUN_DIR
ASM=/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker
SIF=/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
GEOM=$PREP_RUN/out/geom
PIECES=$RUN/scripts/pieces.txt

case "$ARM" in
  oursd) SURFSRC=$GEOM ; BRKSRC=$GEOM ;;
  authb) SURFSRC=$CORP/Surfaces ; BRKSRC=$CORP/Breaklines ;;
  *) echo "[RUN] FATAL unknown ARM $ARM"; exit 9 ;;
esac

mkdir -p "$RUN/logs" "$RUN/out" "$RUN/scripts" "$RUN/dataset/SfS_pp/Breaklines" \
         "$RUN/dataset/SfS_pp/Mesh" "$RUN/dataset/SfS_pp/Axes" "$RUN/dataset/SfS_pp/Surfaces" \
         "$RUN/dataset/SfS_pp/Ground Truth" "$RUN/dataset/SfS_pp/Result"
DS=$RUN/dataset/SfS_pp
echo "[RUN] node=$(hostname) job=$SLURM_JOB_ID start=$(date -Is) pot=$POT arm=$ARM shard=$SHARD"
echo "[RUN] pieces: $(wc -l < $PIECES)"
echo "[RUN] surface source: $SURFSRC"
echo "[RUN] breakline source: $BRKSRC"
echo "[RUN] SFS_ variables in this environment: $(env | grep -cE '^SFS_') (0 expected)"

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
  if [ "$ARM" = "oursd" ]; then
    link_into "$SURFSRC/${P}.S0.xyz" "$DS/Surfaces/${P}_Surface_0.xyz"
    link_into "$SURFSRC/${P}.S1.xyz" "$DS/Surfaces/${P}_Surface_1.xyz"
  else
    link_into "$SURFSRC/${P}_Surface_0.xyz" "$DS/Surfaces/${P}_Surface_0.xyz"
    link_into "$SURFSRC/${P}_Surface_1.xyz" "$DS/Surfaces/${P}_Surface_1.xyz"
  fi
  if [ "$ARM" = "oursd" ]; then
    link_into "$BRKSRC/${P}.Bl0.pcd" "$DS/Breaklines/${P}_Breakline_0.pcd"
    link_into "$BRKSRC/${P}.Bl1.pcd" "$DS/Breaklines/${P}_Breakline_1.pcd"
  else
    link_into "$BRKSRC/${P}_Breakline_0.pcd" "$DS/Breaklines/${P}_Breakline_0.pcd"
    link_into "$BRKSRC/${P}_Breakline_1.pcd" "$DS/Breaklines/${P}_Breakline_1.pcd"
  fi
  # the assembler names Pot_X_Piece_N_T.txt with a single digit (no zero padding)
  i=$((10#${P##*_Piece_}))
  if [ -f "$CORP/Ground Truth/${POT}_Piece_${i}_T.txt" ]; then
    link_into "$CORP/Ground Truth/${POT}_Piece_${i}_T.txt" "$DS/Ground Truth/${POT}_Piece_${i}_T.txt"
  else
    printf "%s\t%d\tabsent in the corpus -- Trans::Read leaves the identity\n" "$P" "$i" >> "$RUN/out/gt_missing.txt"
  fi
done < $PIECES
link_into "$CORP/Ground Truth/${POT}_simple_graph.txt" "$DS/Ground Truth/${POT}_simple_graph.txt"

: > "$RUN/out/inputs.md5"
for f in "$DS/Mesh/"*.obj "$DS/Axes/"*.xyz "$DS/Surfaces/"*.xyz "$DS/Breaklines/"*.pcd "$DS/Ground Truth/"*; do
  printf "%s\t%s\t%s bytes\n" "$(md5sum "$f" | awk '{print $1}')" "$(readlink -f "$f")" "$(stat -c %s "$f")" >> "$RUN/out/inputs.md5"
done
printf "staged\tresolves to\n" > "$RUN/out/links.tsv"
for f in "$DS/Mesh/"*.obj "$DS/Surfaces/"*.xyz "$DS/Breaklines/"*.pcd; do printf "%s\t%s\n" "$f" "$(readlink -f "$f")" >> "$RUN/out/links.tsv"; done
echo "[RUN] inputs.md5 rows: $(wc -l < $RUN/out/inputs.md5)"
echo "[RUN] ground-truth transforms absent: $(wc -l < $RUN/out/gt_missing.txt)"
echo "[RUN] the assembler reads only Breakline_0; _1 is staged inert"

cp -f "$ASM/hpc/tools/main_pristine_batch.cpp" "$RUN/scripts/main_pristine_batch.cpp"
md5sum "$ASM/hpc/tools/main_pristine_batch.cpp" "$SIF" > "$RUN/out/assembler_inputs.md5"

"$APT" exec --bind /data:/data --bind "$RUN:/p298run" --bind "$ASM:/workspace:ro" --bind "$DS:/Dataset/SfS_pp" "$SIF" \
    env POT="$POT" SHARD="$SHARD" ARM="$ARM" bash /p298run/scripts/p298_inside.sh 2>&1 | tee "$RUN/logs/container.log"
echo "[RUN] container pipeline exit ${PIPESTATUS[0]}"

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
echo "==== $POT $ARM arm ===="
cat "$RUN/out/summary.txt" 2>/dev/null || echo "[RUN] NO SUMMARY LINES"
echo "[RUN] done $(date -Is)"
