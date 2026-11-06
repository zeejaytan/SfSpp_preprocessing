#!/usr/bin/env bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe -T -o BatchMode=yes"
$SSH spartan '
R310=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1407_1a6f16e_t310c2-E
head -n 40 $R310/submit.sbatch
grep -n "Initial alignment\|Expend\|Total time" $R310/work/logs/binary_MOR1.log | head -n 40
R311=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0454_3695976_t311b-kladder-E
grep -n "Initial alignment\|Expend\|Total time" $R311/work/logs/binary_E_MOR1.log | head -n 40
'
