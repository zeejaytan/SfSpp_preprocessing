#!/bin/bash
#SBATCH --job-name=t323-conv
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-juglet/logs/convention_%j.out
# Ticket 323: which composition maps each piece's own axis into the assembled frame, for the pots'
# GT, the Juglet key, and the assembler's own output poses.
set -uo pipefail
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
C=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-juglet/work/convention.py
S=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
K=/data/gpfs/projects/punim2657/Dataset/Juglet_GT
RA=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-potA/out/A_K3R1
RJ=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-juglet/out/F20K3_r1
$PY $C "PotA GT T + GT axes" "$S/Ground Truth/Pot_A_Piece_%d_T.txt" "$S/Ground Truth Axes/Pot_A_Piece_%02d_Axis.xyz" 1 2 3 4 5 6 7 8
$PY $C "PotB GT T + GT axes" "$S/Ground Truth/Pot_B_Piece_%d_T.txt" "$S/Ground Truth Axes/Pot_B_Piece_%02d_Axis.xyz" 1 2 3 4 5 6 7 8 9
$PY $C "PotA asm T + GT axes" "$RA/T_%mto_%m.txt" "$S/Ground Truth Axes/Pot_A_Piece_%02d_Axis.xyz" 1 2 3 4 5 6 7 8
$PY $C "Juglet key T + key axes" "$K/Juglet_Piece_%d_T.txt" "$K/Juglet_Piece_%d_Axis.xyz" 1 2 3 4 5 6 7 8 9
$PY $C "Juglet key T, pair 1-8" "$K/Juglet_Piece_%d_T.txt" "$K/Juglet_Piece_%d_Axis.xyz" 1 8
$PY $C "Juglet key T, pair 1-2" "$K/Juglet_Piece_%d_T.txt" "$K/Juglet_Piece_%d_Axis.xyz" 1 2
$PY $C "Juglet asm T + key axes" "$RJ/T_%mto_%m.txt" "$K/Juglet_Piece_%d_Axis.xyz" 1 2 3 4 5 6 7 8
$PY $C "Juglet asm T, pair 1-8" "$RJ/T_%mto_%m.txt" "$K/Juglet_Piece_%d_Axis.xyz" 1 8
