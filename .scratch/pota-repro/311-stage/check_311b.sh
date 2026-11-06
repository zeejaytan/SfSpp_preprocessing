#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0454_3695976_t311b-kladder-E
RUN2=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0624_3695976_t311b2-kladder-K23
"$SSH" -T -o BatchMode=yes spartan "
squeue -j 34427816,34431689
if squeue -j 34427816 -h | grep -q R; then
  srun --jobid=34427816 --overlap /data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3 $RUN/work/throttle311b.py || true
fi
sacct -j 34427816,34431689 --format=JobID,State,ExitCode,Elapsed | grep -v '\.0\|\.1\|\.2\|\.3\|\.4\|\.5'
echo '--- 34427816 completed panel rows ---'
cat $RUN/logs/panel_*.row 2>/dev/null || true
echo '--- 34427816 completed acc rows ---'
cat $RUN/score/acc_*.row 2>/dev/null || true
echo '--- 34427816 binary_E_*.log progress ---'
for f in $RUN/work/logs/binary_E_*.log; do
  [ -f \"\$f\" ] || continue
  exp=\$(grep -c 'Expend' \"\$f\" || true)
  done_str=\$(grep -E 'Sherd accuracy|Edge accuracy|Result save finish' \"\$f\" | tr '\n' ' ' || true)
  echo \"\$(basename \$f): Expend=\$exp lines=\$(wc -l < \$f) \$done_str\"
done
echo '--- 34431689 binary_E_*.log progress ---'
for f in $RUN2/work/logs/binary_E_*.log; do
  [ -f \"\$f\" ] || continue
  exp=\$(grep -c 'Expend' \"\$f\" || true)
  done_str=\$(grep -E 'Sherd accuracy|Edge accuracy|Result save finish' \"\$f\" | tr '\n' ' ' || true)
  echo \"\$(basename \$f): Expend=\$exp lines=\$(wc -l < \$f) \$done_str\"
done
"
