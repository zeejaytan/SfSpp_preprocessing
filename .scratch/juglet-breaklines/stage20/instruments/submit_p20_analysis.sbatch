#!/bin/bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --output=logs/slurm-%j.out
#
# ticket 20 -- analysis job (job 3 of at most 6).
# Runs offline on a compute node: replay of growPaper234 / mergePaper234 /
# classifyAndOrderPaper234 from the segmentation input the sweep harvested, direct
# mesh measurements, and the two required renders. No geometry is copied and no
# corpus file is written; the only build tree is a git archive of tracked source,
# deleted at the end.
#
#   RUN_DIR    this job's run directory
#   SWEEP_DIR  the sweep job's run directory (out/variants.tsv, out/boot, out/axes)
#   STAMP      the sweep job's directory stamp prefix
#   COMMIT_SHA the ticket commit to take the instruments from

set -uo pipefail

test -n "${RUN_DIR:-}"   || { echo "[RUN] FATAL RUN_DIR unset"; exit 9; }
test -n "${SWEEP_DIR:-}" || { echo "[RUN] FATAL SWEEP_DIR unset"; exit 9; }
test -n "${STAMP:-}"     || { echo "[RUN] FATAL STAMP unset"; exit 9; }
test -n "${COMMIT_SHA:-}" || { echo "[RUN] FATAL COMMIT_SHA unset"; exit 9; }

CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
DSET=$CANON/Dataset
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
BUILDROOT=/data/gpfs/projects/punim2657/sfs-vote-20

cd "$RUN_DIR" || exit 9
mkdir -p logs out out/renders

echo "[RUN] host=$(hostname) job=${SLURM_JOB_ID:-none} start=$(date -Is)"
test -s "$SWEEP_DIR/out/variants.tsv" || { echo "[RUN] FATAL no $SWEEP_DIR/out/variants.tsv"; exit 7; }

BT=$BUILDROOT/p20-an-build-${SLURM_JOB_ID:-x}
rm -rf "$BT"; mkdir -p "$BT/src"
git -C "$CANON" cat-file -e "${COMMIT_SHA}^{commit}" || { echo "[RUN] FATAL commit $COMMIT_SHA missing in $CANON"; exit 5; }
git -C "$CANON" archive "$COMMIT_SHA" | tar -x -C "$BT/src" || { echo "[RUN] FATAL archive"; exit 5; }
INSTR=$BT/src/.scratch/juglet-breaklines/stage20/instruments
test -s "$INSTR/replay_analysis.py" || { echo "[RUN] FATAL no replay_analysis.py in the archive"; exit 5; }
md5sum "$INSTR"/*.py "$INSTR"/*.sh > out/instruments.md5

"$PY" "$INSTR/replay_analysis.py" \
  --runs-root /data/gpfs/projects/punim2657/SfSpp/runs \
  --stamp "$STAMP" \
  --out "$RUN_DIR/out" \
  --dset "$DSET" \
  --corpus "$CORP" \
  --axes "$SWEEP_DIR/out" \
  --variants "$SWEEP_DIR/out/variants.tsv" \
  --renders "$RUN_DIR/out/renders" 2>&1 | tee logs/analysis.log
ANEXIT=${PIPESTATUS[0]}
echo "ANALYSIS_EXIT=$ANEXIT"

{
  echo "# ticket 20 analysis job -- geometry accounting"
  echo "# nothing was staged, copied or rendered from the corpus into this run directory:"
  echo "# the analysis reads the segmentation PLYs the sweep job harvested and the frozen"
  echo "# corpus meshes in place, and writes only TSV/MD/PNG text and pictures."
  printf "class\tcount\tbytes\n"
  NB=$(du -sb "$BT" 2>/dev/null | awk '{print $1}')
  NF=$(find "$BT" -type f 2>/dev/null | wc -l)
  printf "source_build_tree_git_archive\t%s\t%s\n" "$NF" "${NB:-0}"
  printf "geometry_deleted\t0\t0\n"
  echo "# du_before: ${NB:-0} bytes (build tree only)"
} > out/GEOMETRY_DELETED.txt
rm -rf "$BT"
DUAF=$(find "$RUN_DIR" -type f | wc -l)
echo "# du_after: $(du -sb "$RUN_DIR" | awk '{print $1}') bytes in $DUAF files kept (this job run dir: TSVs, renders, logs)" >> out/GEOMETRY_DELETED.txt
echo "[RUN] end=$(date -Is)"
exit "$ANEXIT"
