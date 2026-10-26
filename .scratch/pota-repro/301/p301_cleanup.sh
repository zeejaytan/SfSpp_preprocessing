#!/usr/bin/env bash
# Ticket 301 -- remove the geometry, keep the record (workspace AGENTS.md rule 13).
#
# What the runs produced that is payload: the staged dataset (29 pieces x symlinks into the frozen corpus,
# plus one REAL swapped axis file per swap arm) and out/Result (the assembler's transforms and its exported
# edgelines, which are point clouds = geometry). What must survive: run.json, submit.sbatch, logs/, and in
# out/ the summary, the inputs md5, the links, the swap provenance, the corpus md5 before/after pairs and the
# staged axis file itself (7 KB of numbers, that IS the artefact under test, not geometry).
#
# Usage: bash p301_cleanup.sh <run dir> [<run dir> ...]
set -u
[ $# -ge 1 ] || { echo "usage: bash p301_cleanup.sh <run dir> [...]" >&2; exit 2; }
for RUN in "$@"; do
  [ -d "$RUN" ] || { echo "[CLEAN] skipping $RUN (not a directory)" >&2; continue; }
  REC=$RUN/out/cleanup-record.txt
  {
    echo "cleanup record -- ticket 301, AGENTS.md rule 13"
    echo "run dir : $RUN"
    echo "when    : $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    echo
  } > "$REC"

  AXR=
  for AX in "$RUN"/dataset/SfS_pp/Axes/*.xyz; do
    if [ -f "$AX" ] && [ ! -L "$AX" ]; then
      cp -p "$AX" "$RUN/out/staged_axis.final.xyz"
      AXR=$AX
    fi
  done

  for WHAT in dataset out/Result; do
    D=$RUN/$WHAT
    if [ -e "$D" ]; then
      N_FILES=$(find "$D" -type f | wc -l)
      N_LINKS=$(find "$D" -type l | wc -l)
      BYTES=$(du -sb "$D" | cut -f1)
      echo "removed  $WHAT : $N_FILES files, $N_LINKS symlinks, $BYTES bytes" >> "$REC"
      rm -rf "$D"
    else
      echo "removed  $WHAT : absent (nothing to remove)" >> "$REC"
    fi
  done

  KEPT_BYTES=$(du -sb "$RUN" | cut -f1)
  KEPT_FILES=$(find "$RUN" -type f | wc -l)
  {
    echo "kept     whole run dir now: $KEPT_FILES files, $KEPT_BYTES bytes"
    echo
    echo "kept on purpose:"
    echo "  run.json                   parameters, inputs, commit, job id"
    echo "  submit.sbatch / source.txt the exact script submitted and the checkout it built from"
    echo "  logs/                      slurm-%j.out, arm.log, container.log, assembly.log (text)"
    echo "  out/summary.txt            the assembler's own sherd/join counts"
    echo "  out/inputs.md5             every staged input, md5 + resolved path"
    echo "  out/swap_provenance.json   md5s, planted directions, read-back angles"
    echo "  out/corpus_axes_md5_before.txt / _after.txt / corpus_unchanged.txt"
    echo "  out/arm_exit.txt           the arm's exit code"
    if [ -n "$AXR" ]; then
      echo "  out/staged_axis.final.xyz  the swapped axis file, copied out of dataset/"
      md5sum "$RUN/out/staged_axis.final.xyz" | sed 's/^/                             /'
    fi
    echo
    echo "deleted payload is quoted in the ticket; the numbers it produced are in the ticket tables."
  } >> "$REC"
  echo "[CLEAN] $RUN -> $REC"
  head -6 "$REC" | sed 's/^/        /'
done