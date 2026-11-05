#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH=/c/Windows/System32/OpenSSH/ssh.exe
SCP=/c/Windows/System32/OpenSSH/scp.exe
C=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
A=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0532_d330469_t308a-axes/out/pota
D=C:/PR/SfSpp_preprocessing/artifacts/pota310/inputs
mkdir -p "$D"
LT=$(cygpath -w /tmp)
"$SCP" "spartan:$C/Surfaces/Pot_A_Piece_08_Surface_0.xyz" "spartan:$C/Surfaces/Pot_A_Piece_08_Surface_1.xyz" "spartan:$C/Axes/Pot_A_Piece_08_Axis.xyz" "$D/"
"$SSH" spartan "cd $A && tar czf /tmp/p8seeds.tgz paper_s*/Pot_A_Piece_08_Axis.xyz && ls -l /tmp/p8seeds.tgz"
"$SCP" spartan:/tmp/p8seeds.tgz "$LT\\p8seeds.tgz"
cd "$D" && tar xzf /tmp/p8seeds.tgz && ls -1 && du -sh .