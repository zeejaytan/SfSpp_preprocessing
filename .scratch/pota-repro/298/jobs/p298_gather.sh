#!/usr/bin/env bash
# Ticket 298 arm post-processing: classify the assembler's "Could not open file" lines, copy the
# Result directory, and extract the two accuracy lines. Called by p298_arm.sbatch, and usable on
# its own against a finished run (that is how Pot J was settled: the first gate was too strict).
#
# Why the classification exists. Upstream's own blocks produce unreadable paths that are NOT
# staging failures:
#   * Surfaces/..._Surface_F.pcd -- the corpus has no Surface_F file for ANY piece (0 hits in
#     164 pieces); LoadSurface tolerates the absence (ticket 296).
#   * an empty path -- POT_J declares SHARD_NUMBER 19 while its arrays hold 12 entries, so slots
#     12..18 carry "" and the loader still tries to open them.
#   * a piece the block itself switches off -- POT_J_Piece_09 has shard_on_off[8] = false, and we
#     deliberately stage only the active pieces, so its axis is absent.
# An unreadable input of an ACTIVE piece is a staging failure and still exits non-zero.
set -uo pipefail
RUN=$1
P=$RUN/scripts/pieces.txt
mkdir -p "$RUN/out/Result"
grep "Could not open file" "$RUN/logs/assembly.log" > "$RUN/out/open_missing.txt" 2>/dev/null || true
: > "$RUN/out/open_absent.tsv"
fatal=0
while IFS= read -r line; do
  mp=$(printf '%s' "$line" | sed 's/^Error: Could not open file *//')
  if [ -z "$mp" ]; then
    printf 'phantom-slot\t\tempty path in the block (SHARD_NUMBER exceeds the array entries)\n' >> "$RUN/out/open_absent.tsv"
    continue
  fi
  case "$mp" in
    *_Surface_F.pcd)
      printf 'surface-f\t%s\tthe corpus has no Surface_F.pcd for any piece\n' "$mp" >> "$RUN/out/open_absent.tsv"
      continue;;
  esac
  base=$(basename "$mp")
  piece=$(printf '%s' "$base" | sed -E 's/_(Axis|Surface_[01]|Surface_F|Breakline_[01]|Mesh)\.(xyz|pcd|obj)$//')
  if grep -qxF "$piece" "$P" 2>/dev/null; then
    echo "[GATHER] FATAL active piece input absent: $mp" >&2
    fatal=$((fatal + 1))
  else
    printf 'inactive-piece\t%s\tnot in the block active set (out/gt_missing.txt records absent transforms)\n' "$mp" >> "$RUN/out/open_absent.tsv"
  fi
done < "$RUN/out/open_missing.txt"
cp -pr "$RUN/dataset/SfS_pp/Result/." "$RUN/out/Result/" 2>/dev/null || echo "[GATHER] no Result directory to copy"
ls -la "$RUN/out/Result" > "$RUN/out/result_copy_ls.txt" 2>&1 || true
grep -E "Total number|Sherd accuracy|Edge accuracy" "$RUN/logs/assembly.log" > "$RUN/out/summary.txt" 2>/dev/null || true
printf 'fatal_open=%s\tabsent=%s\n' "$fatal" "$(wc -l < "$RUN/out/open_absent.tsv")" > "$RUN/out/gate.txt"
echo "[GATHER] $(cat "$RUN/out/gate.txt")"
exit "$fatal"
