#!/bin/bash
# posecheck13.sh RESULT PIECES -- the Ticket 13 pose gate.
#
# PIECES is the comma-separated list of ELIGIBLE Pot J piece numbers (arm_pieces_J.tsv
# rows with on_off == on; piece 9 has no GT axis and is off, so 11 of 12).  The assembler
# writes one T_<p-1>to_<p-1>.txt per loaded piece into /Dataset/SfS_pp/Result; a cell is
# only scored when every eligible piece exported a NON-EMPTY pose, which is the same
# condition score305.py needs for its 11-piece / 21-join table.
#
# Exit 0 = every eligible pose present and non-empty; 1 = at least one missing or empty;
# 10 = bad arguments.  --self-test runs the three synthetic cases below and prints
# POSECHECK13-SELFTEST-OK / -FAIL (no cluster paths touched).
set -uo pipefail

usage() { echo "usage: posecheck13.sh RESULT PIECES|--self-test" >&2; }

check_dir() {
  local res=$1 pieces=$2 p f n=0 want=0 miss=""
  local IFS=,
  for p in $pieces; do
    [ -n "$p" ] || continue
    want=$((want + 1))
    f="$res/T_$((p - 1))to_$((p - 1)).txt"
    if [ -s "$f" ]; then n=$((n + 1)); else miss="$miss $p"; fi
  done
  if [ "$n" -eq "$want" ] && [ -z "$miss" ]; then
    echo "POSES $n/$want OK"
    return 0
  fi
  echo "POSES $n/$want MISSING:$miss"
  return 1
}

self_test() {
  local t rc=0 d
  t=$(mktemp -d) || exit 70
  d="$t/full"; mkdir -p "$d"
  for p in 1 2 3 5; do printf 'pose\n' > "$d/T_$((p - 1))to_$((p - 1)).txt"; done
  check_dir "$d" "1,2,3,5" > /dev/null || { echo "case full failed"; rc=1; }
  check_dir "$d" "1,2,3,4" > /dev/null && { echo "case missing accepted"; rc=1; }
  : > "$d/T_2to_2.txt"
  check_dir "$d" "1,2,3,5" > /dev/null && { echo "case empty accepted"; rc=1; }
  rm -rf "$t"
  if [ "$rc" -eq 0 ]; then echo "POSECHECK13-SELFTEST-OK"; else echo "POSECHECK13-SELFTEST-FAIL"; fi
  return "$rc"
}

[ $# -ge 1 ] || { usage; exit 10; }
if [ "$1" = "--self-test" ]; then self_test; exit $?; fi
[ $# -eq 2 ] || { usage; exit 10; }
[ -d "$1" ] || { echo "no such result dir: $1" >&2; exit 10; }
check_dir "$1" "$2"
