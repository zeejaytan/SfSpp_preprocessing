#!/usr/bin/env bash
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --job-name=arm22-analysis
#SBATCH --time=00:40:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --output=logs/slurm-%j.out
#
# ticket 22, analysis of the arm grid: pair statistics for both pots, the defaults proof
# (new binary at defaults vs the pre-change main binary, with a second pass of the new
# binary as the run-to-run yardstick), the combined arm table, and one before/after figure.
# Nothing here is scored and no arm is chosen.
set -uo pipefail
RUN=__RUNDIR__
JUG=/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0336_d4f2187_juglet-armgrid22-rep2
POTA=/data/gpfs/projects/punim2657/SfSpp/runs/20261027-0336_d4f2187_pota-armgrid22-rep2
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
INSTR=$RUN/instruments
JUGP="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"
POTAP="Pot_A_Piece_01 Pot_A_Piece_02 Pot_A_Piece_03 Pot_A_Piece_04 Pot_A_Piece_05 Pot_A_Piece_06 Pot_A_Piece_07 Pot_A_Piece_08"
cd "$RUN" || exit 1
mkdir -p logs out/figures
say() { echo "[$(date +%H:%M:%S)] $*"; }

say "measure juglet"
"$PY" "$INSTR/measure_arm.py" "$JUG/out/cells" > out/measure_juglet.log 2>&1
say "  exit=$? $(tail -1 out/measure_juglet.log)"
say "measure pot A"
"$PY" "$INSTR/measure_arm.py" "$POTA/out/cells" > out/measure_pota.log 2>&1
say "  exit=$? $(tail -1 out/measure_pota.log)"

say "defaults proof juglet"
"$PY" "$INSTR/defaults_proof.py" "$JUG/out/cells" Juglet $JUGP > out/defaults_juglet.log 2>&1
say "  exit=$? $(tail -1 out/defaults_juglet.log)"
say "defaults proof pot A"
"$PY" "$INSTR/defaults_proof.py" "$POTA/out/cells" Pot_A $POTAP > out/defaults_pota.log 2>&1
say "  exit=$? $(tail -1 out/defaults_pota.log)"

cp -f "$JUG/out/cells/measure.tsv" out/measure_juglet.tsv
cp -f "$POTA/out/cells/measure.tsv" out/measure_pota.tsv
cp -f "$JUG/out/cells/defaults_proof.tsv" out/defaults_juglet.tsv
cp -f "$POTA/out/cells/defaults_proof.tsv" out/defaults_pota.tsv

say "arm table"
"$PY" "$INSTR/analyse_22.py" "$JUG/out/cells" "$POTA/out/cells" out > out/analyse.log 2>&1
say "  exit=$? $(tail -2 out/analyse.log | tr '\n' ' ')"
IFS=$'\t' read -r PIECE RULE DETAIL < out/render_choice.txt
say "render piece=$PIECE ($DETAIL)"

"$PY" "$INSTR/render_gap.py" \
  --before "$JUG/out/cells/A/Juglet/$PIECE" --after "$JUG/out/cells/D200/Juglet/$PIECE" \
  --piece "$PIECE" --out "out/figures/ticket22_wall_gap_$PIECE.png" \
  --zoom-mm 8 --v-window-mm 12 \
  --title "ticket 22: $PIECE, arm A (defaults) vs arm D200 (own + per-piece spacing + scaled counts)" \
  > out/render.log 2>&1
say "  exit=$? $(grep -c RENDER out/render.log) lines; $(tail -2 out/render.log | tr '\n' ' ')"

printf "%s\t%s\t%s\t%s\t\t\n" "$(basename "$RUN")" "${SLURM_JOB_ID:-local}" "d4f2187" "p22-analysis" >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
say "done: out/arm_table.tsv $(($(wc -l < out/arm_table.tsv) - 1)) rows, figures: $(ls out/figures | tr '\n' ' ')"
