#!/usr/bin/env bash
set -uo pipefail
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261025-0340_0f8a4a4_p294-pictures
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
echo "=== manifest.log ==="; cat $RUN/out/manifest.log
echo "=== ls RUN ==="; ls -1 $RUN
echo "=== ls scripts ==="; ls -1 $RUN/scripts
echo "=== build.json ==="; cat $RUN/out/build.json
"$PY" "$RUN/scripts/manifest294.py" "$RUN" /data/gpfs/projects/punim2657/SfSpp/runs/20261025-0134_787c149_p292-rescore > $RUN/out/manifest.log 2>&1
echo "=== rerun exit=$? ==="
tail -20 $RUN/out/manifest.log
