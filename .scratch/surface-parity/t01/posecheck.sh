#!/bin/bash
# posecheck.sh — the one documented missing-pose check for Ticket 01 cells.
#
# The pinned assembler writes one pose export per piece into the Result mount:
#   T_<i>to_<i>.txt   with i = 0..30 for the 31 Pot E pieces (0-based; the
#   pinned scorer reads the same names in score305.py). A cell is complete only
#   when all 31 of those files exist and are nonempty.
#
# check_poses <result-dir> [expected]
#   prints "POSE-OK <n>/<n>" and returns 0, or
#   prints "POSE-MISSING <have>/<n> pieces:<1-based ids>" and returns 1.
# Used by cell01.sbatch (fail 12) and exercised by fixtures_posecheck.sh on a
# complete fixture, a three-missing fixture and an empty-file fixture.
check_poses() {
  local d="${1:?result dir}"
  local n="${2:-31}"
  local i f miss="" have=0
  for ((i = 0; i < n; i++)); do
    f="$d/T_${i}to_${i}.txt"
    if [ -s "$f" ]; then
      have=$((have + 1))
    else
      miss="$miss $((i + 1))"
    fi
  done
  if [ "$have" -eq "$n" ]; then
    echo "POSE-OK $have/$n"
    return 0
  fi
  echo "POSE-MISSING $have/$n pieces:$miss"
  return 1
}
