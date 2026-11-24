#!/usr/bin/env bash
# Ticket 06 pose-completeness gate.
#
# The assembler must export one pose per sherd before the scorer runs: a cell
# with a missing or empty T_<i>to_<i>.txt is not a result, it is a partial cell,
# and scoring it would report a shortfall the method did not make.
#
#   posecheck06.sh <result_dir> [n_pieces]   -> 0 only when all n files exist and are nonempty
#   posecheck06.sh --self-test               -> exercises 31/31 pass, 3-missing fail, empty fail
set -uo pipefail

check_dir() {
  local dir=$1 n=$2
  local ok=0 missing=0 empty=0 i f
  for ((i=0; i<n; i++)); do
    f="$dir/T_${i}to_${i}.txt"
    if [ ! -e "$f" ]; then
      echo "POSE-06 i=$i status=missing"
      missing=$((missing + 1))
    elif [ ! -s "$f" ]; then
      echo "POSE-06 i=$i status=empty"
      empty=$((empty + 1))
    else
      echo "POSE-06 i=$i status=ok"
      ok=$((ok + 1))
    fi
  done
  echo "POSE-06 summary ok=$ok missing=$missing empty=$empty require=$n dir=$dir"
  [ "$ok" -eq "$n" ]
}

self_test() {
  local tmp rc31=1 rc3=1 rce=1
  tmp=$(mktemp -d "${TMPDIR:-/tmp}/posecheck06.XXXXXX") || return 1
  local i
  for ((i=0; i<31; i++)); do
    printf '%s\n' "1 0 0 0  0 1 0 0  0 0 1 0" > "$tmp/T_${i}to_${i}.txt"
  done
  check_dir "$tmp" 31 > "$tmp/log31.txt" 2>&1; rc31=$?
  [ "$rc31" -eq 0 ] && echo "SELF-TEST 31/31 PASS" || echo "SELF-TEST 31/31 FAIL"

  rm -f "$tmp"/T_5to_5.txt "$tmp"/T_12to_12.txt "$tmp"/T_30to_30.txt
  check_dir "$tmp" 31 > "$tmp/log3.txt" 2>&1; rc3=$?
  [ "$rc3" -ne 0 ] && echo "SELF-TEST 3-missing FAIL" || echo "SELF-TEST 3-missing PASS"

  for ((i=0; i<31; i++)); do
    printf '%s\n' "1 0 0 0  0 1 0 0  0 0 1 0" > "$tmp/T_${i}to_${i}.txt"
  done
  : > "$tmp/T_7to_7.txt"
  check_dir "$tmp" 31 > "$tmp/loge.txt" 2>&1; rce=$?
  [ "$rce" -ne 0 ] && echo "SELF-TEST empty FAIL" || echo "SELF-TEST empty PASS"

  grep -h 'status=missing' "$tmp/log3.txt" | wc -l | sed 's/^/SELF-TEST missing-count=/'
  grep -h 'status=empty' "$tmp/loge.txt" | wc -l | sed 's/^/SELF-TEST empty-count=/'
  rm -rf "$tmp"
  [ "$rc31" -eq 0 ] && [ "$rc3" -ne 0 ] && [ "$rce" -ne 0 ]
}

if [ "${1:-}" = "--self-test" ]; then
  self_test
  exit $?
fi

DIR="${1:?usage: posecheck06.sh <result_dir> [n]}"
N="${2:-31}"
if [ ! -d "$DIR" ]; then
  echo "POSE-06 summary ok=0 missing=$N empty=0 require=$N dir=$DIR (no directory)"
  exit 2
fi
check_dir "$DIR" "$N"
