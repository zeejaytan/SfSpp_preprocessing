#!/usr/bin/env bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe -T -o BatchMode=yes"
$SSH spartan '
R311=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0454_3695976_t311b-kladder-E
cat > $R311/work/wave_ctl.sh << '\''EOF'\''
#!/bin/bash
set -u
ORDER="Hierarchy-E_MOR1 Hierarchy-E_MOR2 Hierarchy-E_BASER2 Hierarchy-E_K1R2 Hierarchy-E_K1R1 Hierarchy-E_BASER1 Hierarchy-E_K2R2 Hierarchy-E_K2R1 Hierarchy-E_K3R1 Hierarchy-E_K3R2 Hierarchy-E_K6R1 Hierarchy-E_K6R2"
MAX_ACTIVE=4

# First stop all except the first 4
i=0
for name in $ORDER; do
  pid=$(pgrep -f "$name" | head -n 1 || true)
  if [ -n "$pid" ]; then
    i=$((i + 1))
    if [ "$i" -gt "$MAX_ACTIVE" ]; then
      kill -STOP "$pid" 2>/dev/null || true
      echo "[wave] STOP $name (pid=$pid)"
    else
      kill -CONT "$pid" 2>/dev/null || true
      echo "[wave] ACTIVE $name (pid=$pid)"
    fi
  fi
done

while true; do
  active=0
  total=0
  for name in $ORDER; do
    pid=$(pgrep -f "$name" | head -n 1 || true)
    if [ -n "$pid" ]; then
      total=$((total + 1))
      st=$(ps -o stat= -p "$pid" 2>/dev/null | tr -d " " || true)
      case "$st" in
        T*) ;;
        *) active=$((active + 1)) ;;
      esac
    fi
  done
  if [ "$total" -eq 0 ]; then
    echo "[wave] all Hierarchy processes finished at $(date -u +%FT%TZ)"
    exit 0
  fi
  if [ "$active" -lt "$MAX_ACTIVE" ]; then
    for name in $ORDER; do
      [ "$active" -ge "$MAX_ACTIVE" ] && break
      pid=$(pgrep -f "$name" | head -n 1 || true)
      if [ -n "$pid" ]; then
        st=$(ps -o stat= -p "$pid" 2>/dev/null | tr -d " " || true)
        case "$st" in
          T*)
            kill -CONT "$pid" 2>/dev/null || true
            active=$((active + 1))
            echo "[wave] CONT $name (pid=$pid) at $(date -u +%FT%TZ) -> active=$active"
            ;;
        esac
      fi
    done
  fi
  sleep 10
done
EOF
chmod +x $R311/work/wave_ctl.sh
srun --jobid=34427816 --overlap bash -c "nohup $R311/work/wave_ctl.sh > $R311/logs/wave_ctl.log 2>&1 < /dev/null & sleep 2 && cat $R311/logs/wave_ctl.log"
'
