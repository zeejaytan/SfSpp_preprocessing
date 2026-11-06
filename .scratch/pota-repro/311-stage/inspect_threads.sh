#!/usr/bin/env bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe -T -o BatchMode=yes"
$SSH spartan '
grep -rn "num_threads\|omp_\|thread" /data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/hpc/ 2>/dev/null | head -n 30 || true
R311=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0454_3695976_t311b-kladder-E
for f in $R311/work/logs/binary_E_*.log; do
  echo "$(basename $f): Expend=$(grep -c Expend $f || true) lines=$(wc -l < $f)"
done
'
