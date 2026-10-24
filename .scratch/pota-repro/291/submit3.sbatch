#!/usr/bin/env bash
#SBATCH --job-name=p291g3
#SBATCH --time=00:20:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --output=logs/slurm-%j.out
# Ticket 291, GATE3 re-judged with the corrected rule on freshly staged trees.
set -uo pipefail

RUN=${RUN_DIR:?}
CORPUS=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
SCRIPT=$RUN/stage_piece.sh
STAGE=$RUN/gate3fix
OUT=$RUN/out

rm -rf "$STAGE"; mkdir -p "$STAGE"

bash "$SCRIPT" "$STAGE/J09" Pot_J Pot_J_Piece_09  > "$OUT/stage_J09.log" 2>&1; echo "STAGE_EXIT[J09]=$?"
bash "$SCRIPT" "$STAGE/H02" Pot_H Pot_H_Piece_02  > "$OUT/stage_H02.log" 2>&1; echo "STAGE_EXIT[H02]=$?"
tail -1 "$OUT/stage_J09.log"; tail -1 "$OUT/stage_H02.log"

/data/gpfs/projects/punim2657/.conda/envs/graphify/bin/python3 "$RUN/gate3fix2.py" "$CORPUS" "$STAGE/J09" "$STAGE/H02" > "$OUT/gate3_fixed.txt" 2>&1
echo "GATE3FIX_EXIT=$?"
cat "$OUT/gate3_fixed.txt"

# census before deleting, so the "no geometry, only symlinks" claim is recorded per tree
: > "$OUT/gate3_census.txt"
for d in J09 H02; do
  echo "--- $d" >> "$OUT/gate3_census.txt"
  find "$STAGE/$d" -type f -size +1M | wc -l >> "$OUT/gate3_census.txt"
  find "$STAGE/$d" -type l | wc -l >> "$OUT/gate3_census.txt"
  find "$STAGE/$d" -type f -size +1M | sed "s|$STAGE/||" >> "$OUT/gate3_census.txt"
  du -sh "$STAGE/$d" >> "$OUT/gate3_census.txt"
done
cat "$OUT/gate3_census.txt"

rm -rf "$STAGE"
echo "GEOMETRY_DELETED" > "$OUT/GEOMETRY_DELETED3.txt"
echo "deleted: $STAGE (two staged trees, each mesh+cloud symlinks and one 108-byte axis copy)" >> "$OUT/GEOMETRY_DELETED3.txt"
echo "kept: run.json submit*.sbatch stage_piece.sh gate3fix2.py logs/ out/*.txt out/*.md5 out/*.pcd bin/" >> "$OUT/GEOMETRY_DELETED3.txt"
echo "not deleted (input corpus): $CORPUS" >> "$OUT/GEOMETRY_DELETED3.txt"
echo "STAGE_DIRS_REMAINING=$(find "$STAGE" -maxdepth 1 -type d 2>/dev/null | wc -l)"

echo "DONE"
