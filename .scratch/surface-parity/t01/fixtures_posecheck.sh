#!/bin/bash
# fixtures_posecheck.sh — validate the documented pose check on small fixtures.
# Runs the SAME function cell01.sbatch sources (posecheck.sh), on:
#   good/   31 nonempty exports            -> expect POSE-OK 31/31, rc 0
#   short/  28 exports (17, 27, 30 absent) -> expect POSE-MISSING 28/31 pieces: 18 28 31, rc 1
#   empty/  31 names, one zero-byte        -> expect POSE-MISSING 30/31 pieces: 7, rc 1
# Writes a log when LOG is set; exit 0 only if all three expectations hold.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
. "$HERE/posecheck.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/good" "$TMP/short" "$TMP/empty"
for i in $(seq 0 30); do
  printf '%s\n' "1 0 0 0 0 1 0 0 0 0 1 0" > "$TMP/good/T_${i}to_${i}.txt"
done
for i in $(seq 0 30); do
  case " 17 27 30 " in *" $i "*) continue;; esac
  printf '%s\n' "1 0 0 0 0 1 0 0 0 0 1 0" > "$TMP/short/T_${i}to_${i}.txt"
done
for i in $(seq 0 30); do
  : > "$TMP/empty/T_${i}to_${i}.txt"
  printf '%s\n' "1 0 0 0 0 1 0 0 0 0 1 0" > "$TMP/empty/T_${i}to_${i}.txt"
done
: > "$TMP/empty/T_6to_6.txt"
rc=0
out=""
line=""
for case_name in good short empty; do
  line="$(check_poses "$TMP/$case_name")"
  got=$?
  want_word=POSE-OK
  [ "$case_name" = good ] || want_word=POSE-MISSING
  if [ "$got" -ne 0 ] && [ "$case_name" = good ]; then rc=1; fi
  if [ "$got" -eq 0 ] && [ "$case_name" != good ]; then rc=1; fi
  case "$line" in "$want_word"*) ;; *) rc=1;; esac
  case "$case_name" in
    good) case "$line" in "POSE-OK 31/31") ;; *) rc=1;; esac;;
    short) case "$line" in "POSE-MISSING 28/31 pieces: 18 28 31") ;; *) rc=1;; esac;;
    empty) case "$line" in "POSE-MISSING 30/31 pieces: 7") ;; *) rc=1;; esac;;
  esac
  out="$out$case_name\t$got\t$line\n"
done
if [ -n "${LOG:-}" ]; then printf "fixture\trc\tverdict\n$out" > "$LOG"; fi
printf "fixture\trc\tverdict\n$out" | column -t -s$'\t'
[ "$rc" -eq 0 ] && echo "FIXTURES-OK 3/3" || echo "FIXTURES-FAIL"
exit "$rc"
