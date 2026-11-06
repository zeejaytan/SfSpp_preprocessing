#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
"$SSH" -T -o BatchMode=yes -o ConnectTimeout=25 spartan '
R310E=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1407_1a6f16e_t310c2-E
echo "=== work/build contents ==="
ls -la $R310E/work/build/
echo "=== trees_m/E/MM contents ==="
ls -la $R310E/trees_m/E/MM/
echo "=== Does binary use OpenMP / threads? ==="
grep -rn "omp\|thread" /data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/class/ /data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/hpc/ 2>/dev/null | head -30
'
