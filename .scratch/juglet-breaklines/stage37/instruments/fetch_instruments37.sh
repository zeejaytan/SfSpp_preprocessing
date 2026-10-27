#!/usr/bin/env bash
# ticket 37: put this ticket's instruments into a run directory FROM THE PUSHED COMMIT, and prove
# they are LF before a job is submitted.
#
# Why the commit and not the laptop: the committed blobs of this project's instruments carry
# carriage returns (git show <sha>:.../measure34.py has 890 of them), and two grids in this project
# already died on "set: pipefail: invalid option name" because a CR reached bash.  The bytes the
# job runs are therefore derived from the sha under test, normalised, and checked -- not copied
# from a platform that might have rewritten them.
#
# usage: fetch_instruments37.sh <commit_sha> <rundir>
set -uo pipefail
SHA=${1:?commit sha}
RUN=${2:?run dir}
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
SUB=.scratch/juglet-breaklines/stage37/instruments
if [ ! -d "$RUN" ]; then echo "[FETCH] FATAL no run dir $RUN"; exit 3; fi
mkdir -p "$RUN/instruments" "$RUN/out" "$RUN/logs"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/s37.XXXXXX") || exit 3
trap 'rm -rf "$TMP"' EXIT
if ! git -C "$CANON" cat-file -e "${SHA}^{commit}" 2>/dev/null; then
  echo "[FETCH] FATAL commit $SHA not in $CANON -- push the branch and let the checkout fetch first"
  exit 3
fi
git -C "$CANON" archive "$SHA" "$SUB" | tar -x -C "$TMP" || { echo "[FETCH] FATAL archive failed"; exit 3; }
SRC=$TMP/$SUB
[ -d "$SRC" ] || { echo "[FETCH] FATAL $SUB is not in $SHA"; exit 3; }
echo "[FETCH] sha=$SHA source=$SRC"
ls -la "$SRC"
cp -f "$SRC"/* "$RUN/instruments"/ || { echo "[FETCH] FATAL copy failed"; exit 3; }

# what the commit actually holds, before touching it
{
  printf "file\tbytes\tlines_with_cr\tmd5_as_committed\n"
  for f in "$RUN"/instruments/*; do
    [ -f "$f" ] || continue
    printf "%s\t%s\t%s\t%s\n" "$(basename "$f")" "$(stat -c %s "$f")" \
      "$(grep -cU $'\r' "$f")" "$(md5sum "$f" | cut -d' ' -f1)"
  done
} > "$RUN/out/instruments_as_committed.md5"
column -t "$RUN/out/instruments_as_committed.md5" 2>/dev/null || cat "$RUN/out/instruments_as_committed.md5"

# normalise, then prove it
for f in "$RUN"/instruments/*; do
  [ -f "$f" ] || continue
  if grep -qU $'\r' "$f"; then
    sed -i 's/\r$//' "$f"
    echo "[FETCH] converted CRLF -> LF: $(basename "$f")"
  fi
done
{
  printf "file\tbytes\tlines_with_cr\tmd5_lf\n"
  for f in "$RUN"/instruments/*; do
    [ -f "$f" ] || continue
    printf "%s\t%s\t%s\t%s\n" "$(basename "$f")" "$(stat -c %s "$f")" \
      "$(grep -cU $'\r' "$f")" "$(md5sum "$f" | cut -d' ' -f1)"
  done
} > "$RUN/out/instruments_lf.md5"
column -t "$RUN/out/instruments_lf.md5" 2>/dev/null || cat "$RUN/out/instruments_lf.md5"

BAD=$(grep -lU $'\r' "$RUN"/instruments/* 2>/dev/null)
if [ -n "$BAD" ]; then
  echo "[FETCH] FATAL carriage returns survived in:"
  echo "$BAD"
  exit 4
fi
for f in "$RUN"/instruments/*.sh; do
  bash -n "$f" || { echo "[FETCH] FATAL bash -n failed: $f"; exit 4; }
done
echo "[FETCH] all $(ls "$RUN"/instruments/* | wc -l) instrument files are LF; bash -n passes on every .sh"
