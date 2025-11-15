#!/usr/bin/env bash
set -euo pipefail

# Densify all Pot_A surfaces in Temp/Data to target counts.

BASE_DIR="$(pwd)"
IN_DIR="$BASE_DIR/original_nurbs_preprocessing/Temp/Data/Pot_A"
REF_DIR="$BASE_DIR/NURBS_Dataset_20250927_ProperCurvature/SfS_pp/Surfaces"

if [ ! -d "$IN_DIR" ]; then
  echo "Input directory not found: $IN_DIR" >&2
  exit 1
fi

python_bin="python3"
densify_py="$BASE_DIR/tools/densify_surface_simple.py"
if ! command -v "$python_bin" >/dev/null 2>&1; then
  echo "python3 not found in PATH" >&2
  exit 1
fi
if [ ! -f "$densify_py" ]; then
  echo "Densifier script missing: $densify_py" >&2
  exit 1
fi

# Build reference counts for pieces 01..08 from NURBS dataset if present
declare -A REF_COUNTS
if [ -d "$REF_DIR" ]; then
  for i in $(seq -w 01 08); do
    for s in 0 1; do
      f="$REF_DIR/Pot_A_Piece_${i}_Surface_${s}.xyz"
      if [ -f "$f" ]; then
        c=$(wc -l < "$f")
        key="${i}_${s}"
        REF_COUNTS[$key]="$c"
      fi
    done
  done
fi

echo "Found ${#REF_COUNTS[@]} NURBS reference counts"

# Densify all pieces 01..40, surfaces 0 and 1
for i in $(seq -w 01 40); do
  for s in 0 1; do
    in_file="$IN_DIR/Pot_A_Piece_${i}_Surface_${s}.xyz"
    if [ ! -f "$in_file" ]; then
      echo "[SKIP] missing: $in_file"
      continue
    fi
    cur=$(wc -l < "$in_file")
    key="${i}_${s}"
    if [ -n "${REF_COUNTS[$key]:-}" ]; then
      target="${REF_COUNTS[$key]}"
    else
      # Default target for non-ref pieces: match NURBS-like density (~20k points)
      target=20000
    fi

    tmp_out="$in_file.__dense_tmp__"
    bak_out="$in_file.__orig_backup__"

    echo "[DENSIFY] piece=$i surf=$s cur=$cur target=$target -> $in_file"
    # Backup once
    if [ ! -f "$bak_out" ]; then
      cp -p "$in_file" "$bak_out"
    fi

    # Run densifier
    "$python_bin" "$densify_py" "$in_file" "$tmp_out" "$target"
    mv -f "$tmp_out" "$in_file"
  done
done

echo "Densification complete. Backups kept alongside as __orig_backup__."
