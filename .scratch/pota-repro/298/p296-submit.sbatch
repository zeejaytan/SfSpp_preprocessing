#!/usr/bin/env bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --job-name=p296arm
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=logs/slurm-%j.out
#
# Ticket 296 assembly arm. One arm per job: ARM=ceiling (the authors' own Breakline_0 files) or
# ARM=test (this ticket's Breakline_0, from run p296-prep). Everything else in the dataset is the
# frozen corpus, symlinked -- mesh, axis, both surfaces, ground truth -- so the only difference
# between the two arms is the eight _0 breaklines the assembler reads.
set -uo pipefail

: ${RUN_DIR:?RUN_DIR must be exported}
: ${ARM:?ARM must be ceiling or test}
RUN=$RUN_DIR
ARM=$ARM
ASM=/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker
SIF=/data/gpfs/projects/punim2657/sfs_main/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp

case "$ARM" in
  ceiling) SRC=$CORP/Breaklines ;;
  test)    SRC=${PREP_RUN:?PREP_RUN must be exported for ARM=test}/out/geom ;;
  *) echo "[RUN] FATAL unknown ARM $ARM"; exit 9 ;;
esac

mkdir -p "$RUN/logs" "$RUN/out" "$RUN/scripts" "$RUN/dataset/SfS_pp/Breaklines" \
         "$RUN/dataset/SfS_pp/Mesh" "$RUN/dataset/SfS_pp/Axes" "$RUN/dataset/SfS_pp/Surfaces" \
         "$RUN/dataset/SfS_pp/Ground Truth" "$RUN/dataset/SfS_pp/Result"
DS=$RUN/dataset/SfS_pp
echo "[RUN] node=$(hostname) job=$SLURM_JOB_ID start=$(date -Is) arm=$ARM"
echo "[RUN] SFS_ variables in this environment: $(env | grep -cE '^SFS_') (0 expected)"
echo "[RUN] breakline source: $SRC"

link_into() { # link_into <target> <staged>
  if [ -e "$2" ] && [ ! -L "$2" ]; then echo "[RUN] FATAL refusing to replace a real file $2"; exit 10; fi
  ln -sfn "$1" "$2"
  [ -L "$2" ] || { echo "[RUN] FATAL not a symlink $2"; exit 10; }
}

i=1
for P in Pot_A_Piece_01 Pot_A_Piece_02 Pot_A_Piece_03 Pot_A_Piece_04 Pot_A_Piece_05 Pot_A_Piece_06 Pot_A_Piece_07 Pot_A_Piece_08; do
  link_into "$CORP/Mesh/${P}_Mesh.obj"                  "$DS/Mesh/${P}_Mesh.obj"
  link_into "$CORP/Axes/${P}_Axis.xyz"                  "$DS/Axes/${P}_Axis.xyz"
  link_into "$CORP/Surfaces/${P}_Surface_0.xyz"         "$DS/Surfaces/${P}_Surface_0.xyz"
  link_into "$CORP/Surfaces/${P}_Surface_1.xyz"         "$DS/Surfaces/${P}_Surface_1.xyz"
  link_into "$CORP/Ground Truth/Pot_A_Piece_${i}_T.txt" "$DS/Ground Truth/Pot_A_Piece_${i}_T.txt"
  if [ "$ARM" = "ceiling" ]; then
    link_into "$CORP/Breaklines/${P}_Breakline_0.pcd"   "$DS/Breaklines/${P}_Breakline_0.pcd"
    link_into "$CORP/Breaklines/${P}_Breakline_1.pcd"   "$DS/Breaklines/${P}_Breakline_1.pcd"
  else
    link_into "$SRC/${P}.Bl0.pcd"                       "$DS/Breaklines/${P}_Breakline_0.pcd"
    link_into "$SRC/${P}.Bl1.pcd"                       "$DS/Breaklines/${P}_Breakline_1.pcd"
  fi
  i=$((i + 1))
done
link_into "$CORP/Ground Truth/Pot_A_simple_graph.txt" "$DS/Ground Truth/Pot_A_simple_graph.txt"

: > "$RUN/out/inputs.md5"
for f in "$DS/Mesh/"*.obj "$DS/Axes/"*.xyz "$DS/Surfaces/"*.xyz "$DS/Breaklines/"*.pcd "$DS/Ground Truth/"*; do
  printf "%s\t%s\t%s bytes\n" "$(md5sum "$f" | awk '{print $1}')" "$(readlink -f "$f")" "$(stat -c %s "$f")" >> "$RUN/out/inputs.md5"
done
printf "staged breakline\tresolves to\n" > "$RUN/out/links.tsv"
for f in "$DS/Breaklines/"*.pcd; do printf "%s\t%s\n" "$f" "$(readlink -f "$f")" >> "$RUN/out/links.tsv"; done
echo "[RUN] inputs.md5 rows: $(wc -l < $RUN/out/inputs.md5)"
echo "[RUN] the assembler reads only Breakline_0 (class/data_path.h POT_A block); _1 is staged inert"

cp -f "$ASM/hpc/tools/main_pristine_batch.cpp" "$RUN/scripts/main_pristine_batch.cpp"
md5sum "$ASM/hpc/tools/main_pristine_batch.cpp" "$SIF" > "$RUN/out/assembler_inputs.md5"

"$APT" exec --bind /data:/data --bind "$RUN:/p296run" --bind "$ASM:/workspace:ro" --bind "$DS:/Dataset/SfS_pp" "$SIF" \
    bash /p296run/scripts/p296_inside.sh 2>&1 | tee "$RUN/logs/container.log"
echo "[RUN] container pipeline exit ${PIPESTATUS[0]}"

# The dataset directory holds symlinks into /data; a bind that does not resolve them makes the
# assembler load no axis and no points and then segfault -- that must never read as a seating result.
# Surface_F.pcd is absent from the corpus by design and LoadSurface tolerates it (ticket 296 recon);
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
echo "==== $ARM arm ===="
cat "$RUN/out/summary.txt" 2>/dev/null || echo "[RUN] NO SUMMARY LINES"
echo "[RUN] done $(date -Is)"
