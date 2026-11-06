#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
"$SSH" -T -o BatchMode=yes -o ConnectTimeout=25 spartan '
R310E=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1407_1a6f16e_t310c2-E
R310B3=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1215_1a6f16e_t310b3-timing
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
echo "=== arm_pieces_E.tsv ==="
cat $R310E/trees_m/arm_pieces_E.tsv
echo "=== axes310 Pot_E files ==="
ls $R310B3/out/axes310/Pot_E_Piece_*_Axis.xyz | wc -l
ls $R310B3/out/axes310/Pot_E_Piece_*_Axis.xyz
echo "=== CORP Axes Pot_E files ==="
ls $CORP/Axes/Pot_E_Piece_*_Axis.xyz
echo "=== CORP GT T Pot_E files ==="
ls "$CORP/Ground Truth"/Pot_E_Piece_*_T.txt
echo "=== data_path.h POT_E section ==="
grep -n -A 180 "ifdef POT_E" $R310E/work/inc_E/class/data_path.h | head -180
echo "=== score/acc.tsv of 310c2-E ==="
cat $R310E/score/acc.tsv
'
