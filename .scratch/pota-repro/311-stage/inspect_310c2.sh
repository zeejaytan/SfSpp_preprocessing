#!/usr/bin/env bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe -T -o BatchMode=yes"
$SSH spartan '
R310=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1407_1a6f16e_t310c2-E
wc -l $R310/work/logs/binary_*.log
grep -c "Expend" $R310/work/logs/binary_*.log
cat $R310/logs/panel.tsv
tail -n 30 $R310/submit.sbatch
'
