#!/bin/bash
#SBATCH --job-name=p289a2
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=00:40:00
#SBATCH --output=logs/p289a2_%j.out
# a289.py re-run only: job 33747182 built the pipeline, but the analysis died on a stage file
# the shipped binary never writes (boundary_S0.pcd). Nothing is recomputed; draw 1 is on disk.
set -u
: "$RUN_DIR"
RUN=$RUN_DIR
PY=/data/gpfs/projects/punim2657/.conda/envs/graphify/bin/python3
cd "$RUN" || exit 9
$PY -c "import numpy, matplotlib; print('numpy', numpy.__version__, 'mpl', matplotlib.__version__)" || exit 10
$PY a289.py "$RUN" 2>&1 | tee logs/a289_d1.log
echo "A289_EXIT=${PIPESTATUS[0]}"
$PY - "$RUN" <<'PY'
import struct, glob, os, sys
for p in sorted(glob.glob(os.path.join(sys.argv[1], "out/png/*.png"))):
    d = open(p, "rb").read(33)
    w, h = struct.unpack(">II", d[16:24])
    print("[PX] %s %dx%d %d bytes" % (os.path.basename(p), w, h, os.path.getsize(p)))
PY
echo DONE
