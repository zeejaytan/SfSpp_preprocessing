#!/bin/bash
set -euo pipefail
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-1316_fe906ab_t313a-axes
mkdir -p "$RUN/out" "$RUN/logs" "$RUN/work"
cat << 'EOF' > "$RUN/run.json"
{
  "runid": "20261106-1316_fe906ab_t313a-axes",
  "ticket": "313",
  "stage": "A/B: distance-invariant axis optimization across 163 pieces",
  "commit": "fe906ab",
  "cap": 6,
  "seeds": 10,
  "step": 10,
  "normalized": true,
  "clearance_mm": [25.0, 105.0]
}
EOF
cp /data/gpfs/projects/punim2657/sfs_preprocessing/work_313/generate_axes313.py "$RUN/work/"
cp -r /data/gpfs/projects/punim2657/sfs_preprocessing/work_313/sfs_axes "$RUN/work/"
cd "$RUN"
/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3 work/generate_axes313.py --out out --jobs 16 --cap 6 --seeds 10 --step 10 > logs/generate_axes313.log 2>&1
echo "rc=$? files=$(ls out/axes313/*.xyz | wc -l) lines=$(cat out/axes313/*.xyz | wc -l)"
tail -20 logs/generate_axes313.log
