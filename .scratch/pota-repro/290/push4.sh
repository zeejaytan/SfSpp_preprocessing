#!/bin/bash
set -eu
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-2328_d36a33e_p290-corpus
cp /tmp/p290/finish290.py "$RUN/"
python3 -c "import ast; ast.parse(open('/tmp/p290/finish290.py').read()); print('py ok')"
export RUN_DIR="$RUN"
python3 "$RUN/finish290.py"
echo "==OUT"
ls "$RUN/out"
echo "==CURV"
cat "$RUN/out/curvature_column.txt"
echo "==DELTAIL"
tail -4 "$RUN/out/GEOMETRY_DELETED.txt"
