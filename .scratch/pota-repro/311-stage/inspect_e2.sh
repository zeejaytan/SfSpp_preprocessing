#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
"$SSH" -T -o BatchMode=yes -o ConnectTimeout=25 spartan '
R310E=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1407_1a6f16e_t310c2-E
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
LANES_E=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0445_9c5eec2_t305-lane-e2/out/geom
echo "=== Point/Pot_E files ==="
ls $CORP/Point/Pot_E_Piece_* 2>/dev/null | wc -l
ls $CORP/Point/Pot_E_Piece_* 2>/dev/null | tail -6
echo "=== LANES_E files ==="
ls $LANES_E/*.Bl0 | wc -l
ls $LANES_E/*.Bl0 | tail -6
echo "=== Breaklines point counts for 32,33,34 ==="
wc -l $CORP/Breaklines/Pot_E_Piece_32_* $CORP/Breaklines/Pot_E_Piece_33_* $CORP/Breaklines/Pot_E_Piece_34_*
echo "=== simple_graph lines/cols ==="
wc -l "$CORP/Ground Truth/Pot_E_simple_graph.txt"
head -1 "$CORP/Ground Truth/Pot_E_simple_graph.txt" | wc -w
echo "=== R310E/score files ==="
ls -la $R310E/score/
head -40 $R310E/score/MMR1.tsv $R310E/score/MMR2.tsv
echo "=== data_structure.cpp CountResult ==="
sed -n "965,1045p" /data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/class/data_structure.cpp
'
