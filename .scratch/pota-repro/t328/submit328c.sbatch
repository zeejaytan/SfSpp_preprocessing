#!/bin/bash
#SBATCH --job-name=t328h
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=00:40:00
#
# Ticket 328, job C: the 326 correspondence harness on the CURED Juglet tree.
# Only the tree's surfaces and Breakline_0 change relative to the before tree (t325's
# trees/juglet_GT_r1, which 326's job 34671027 already scored: out/diag_jug_GT.txt).
# The pristine assembly objects come from 326's own build (job 34671027) -- hardlinked,
# not rebuilt -- and the SIF is sfs_main/sfs_pristine_assembly.sif, the one that carries
# /opt/sfs-pristine (job 34696906 died trying pcl_191_nurbs.sif, which does not).
set -uo pipefail
RUN=$SLURM_SUBMIT_DIR
WORK=$RUN/work
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
T325=$RUNS/20261110-1640_22151d0_t325-juglet
T326=$RUNS/20261110-1844_6925cb0_t326-diag
CELL=$RUNS/20261110-2205_123f2ca_t328-wallside-short/outgt_jug
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
cd "$RUN" || exit 1
mkdir -p logs out "$WORK/tools"
fail() { echo "[JOB] FATAL $*"; echo "$*" > RUN-FAILED.txt; exit 1; }
echo "[JOB] $(basename $RUN) job=$SLURM_JOB_ID start=$(date -u +%FT%TZ) sif_md5=$(md5sum $SIF | cut -d' ' -f1)"

# 1. tree: t325's GT skeleton (axes = answer key, meshes, T matrices, graph), then the
#    cured surfaces and breaklines replace the shipped ones. rm first: cp -al hardlinks.
TREE=$WORK/tree
cp -al "$T325/work/trees/juglet_GT_r1" "$TREE" || fail "cannot clone the GT tree"
rm -f "$TREE"/Surfaces/*.xyz "$TREE"/Breaklines/*.pcd
for k in 1 2 3 4 5 6 7 8 9; do
  for s in 0 1; do
    "$PY" - "$CELL/geom/Juglet_Piece_${k}.S${s}" "$TREE/Surfaces/Juglet_Piece_${k}_Surface_${s}.xyz" <<'PYEOF' || fail "ply->xyz piece $k face $s"
import sys
src, dst = sys.argv[1], sys.argv[2]
n = 0; hdr = True; rows = []
with open(src) as f:
    for line in f:
        if hdr:
            t = line.split()
            if t and t[0] == 'element' and t[1] == 'vertex': n = int(t[2])
            if t and t[0] == 'end_header': hdr = False
            continue
        if len(rows) < n:
            rows.append(' '.join(line.split()[:6]))
with open(dst, 'w') as f:
    f.write('\n'.join(rows) + '\n')
print('wrote %s rows=%d' % (dst, len(rows)))
PYEOF
  done
  cp "$CELL/geom/Juglet_Piece_${k}.Bl0" "$TREE/Breaklines/Juglet_Piece_${k}_Breakline_0.pcd" || fail "breakline 0 piece $k"
  cp "$CELL/geom/Juglet_Piece_${k}.Bl1" "$TREE/Breaklines/Juglet_Piece_${k}_Breakline_1.pcd" || fail "breakline 1 piece $k"
done
( cd "$TREE" && find . -type f -o -type l | sort | xargs md5sum 2>/dev/null ) > "$RUN/tree_cured.md5"
echo "[JOB] tree built: $(wc -l < "$RUN/tree_cured.md5") files"
head -2 "$TREE/Surfaces/Juglet_Piece_1_Surface_0.xyz"
head -12 "$TREE/Breaklines/Juglet_Piece_1_Breakline_0.pcd" | tail -3

# 2. harness sources + the pristine objects 326 already built
cp "$WORK/diag326_pairs.cpp" "$WORK/tools/diag326_pairs.cpp" || fail "no harness source"
md5sum "$WORK/tools/diag326_pairs.cpp"
cp -al "$T326/work/build" "$WORK/build" || fail "cannot clone the pristine build"
cp "$T326/out/diag_jug_GT.txt" "$RUN/out/diag_jug_before.txt" || echo "[JOB] WARN no before table to copy"

# 3. run it
export OMP_NUM_THREADS=2
$APT exec --writable-tmpfs --bind "$WORK":/panel --bind "$T325/work/inc_jug":/inc:ro \
  --bind "$TREE":/Dataset/SfS_pp:ro "$SIF" bash /panel/diag326.sh jug_cured /inc 20 -DJUGLET_ORIG \
  > "$RUN/out/diag_jug_cured.txt" 2>&1
echo "[JOB] diag rc=$?"
tail -3 "$RUN/out/diag_jug_cured.txt"
echo "[JOB] complete $(date -u +%FT%TZ)"
