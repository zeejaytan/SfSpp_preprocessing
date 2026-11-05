#!/bin/bash
# fetch_c2.sh POT... -- pull score/acc.tsv + logs/panel.tsv of each pot's 308b base
# run and its C2 run into artifacts/pota310/c2/{base,new}/<POT>/.
# NOTE: Windows scp.exe + MSYS_NO_PATHCONV=1 needs a WINDOWS-form local path (C:/...).
set -u
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SCP=/c/Windows/System32/OpenSSH/scp.exe
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
S=/c/PR/worktrees/sfs/310/.scratch/pota-repro/310-stage
DEST=C:/PR/SfSpp_preprocessing/artifacts/pota310/c2
pull() {  # pull REMOTEPATH LOCALPATH
  local i
  for i in $(seq 1 6); do
    if "$SCP" -o ConnectTimeout=25 "spartan:$1" "$2" 2>/tmp/scperr.txt; then
      [ -s "$2" ] && return 0
    fi
    case "$(cat /tmp/scperr.txt)" in *"No such file"*) echo "   MISS(remote) $1"; return 1;; esac
    sleep 5
  done
  echo "   MISS $1 :: $(tail -1 /tmp/scperr.txt)"
  return 1
}
for p in "$@"; do
  b=$(awk -v p="$p" '$1==p{print $2}' "$S/base308.tsv")
  n=$(awk -v p="$p" '$1==p{print $3}' /tmp/t310c2_jobs.txt)
  for pair in "base:$b" "new:$n"; do
    kind=${pair%%:*}; dir=${pair#*:}
    [ -z "$dir" ] && { echo "$p $kind: no run dir"; continue; }
    mkdir -p "$DEST/$kind/$p/score" "$DEST/$kind/$p/logs"
    pull "$RUNS/$dir/score/acc.tsv" "$DEST/$kind/$p/score/acc.tsv"
    pull "$RUNS/$dir/logs/panel.tsv" "$DEST/$kind/$p/logs/panel.tsv"
  done
  echo "$p base=$b new=$n"
done
