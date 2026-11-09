#!/bin/bash
#SBATCH --job-name=t322-small2
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=logs/small2-%j.out
#SBATCH --error=logs/small2-%j.err
# Ticket 322: (1) Pot F 06 profile probe; (2) --paper-chain identity, committed potsac.py vs working tree.
set -uo pipefail
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0415_d628fc0_t322-axes
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SURF=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces
export OMP_NUM_THREADS=4
cd "$R/work" || exit 1
$PY f06_probe.py ../out/basins_all.json ../out/profile_rank.json ../out/jugkey Pot_F_Piece_06 > ../out/f06_probe.txt 2>&1
echo "f06 rc=$?"

rm -rf "$R/pc/head" "$R/pc/wt"; mkdir -p "$R/pc/head" "$R/pc/wt" "$R/pc/out_head" "$R/pc/out_wt"
cp -r "$R/impl/sfs_axes" "$R/pc/wt/"
cp -r "$R/impl/sfs_axes" "$R/pc/head/"
cp "$R/pc/potsac_HEAD.py" "$R/pc/head/sfs_axes/potsac.py"
md5sum "$R"/pc/{head,wt}/sfs_axes/potsac.py
for T in head wt; do
  for P in A:1-8 F:1-7; do
    ( cd "$R/pc/$T" && $PY -m sfs_axes.cli extract-pot-a --surfaces "$SURF" --out "$R/pc/out_$T" \
        --pot "${P%%:*}" --pieces "${P##*:}" --seed 0 --paper-chain ) > "$R/pc/log_${T}_${P%%:*}.txt" 2>&1
    echo "$T ${P%%:*} rc=$?"
  done
done
n=$(ls "$R/pc/out_head" | wc -l)
if diff -r "$R/pc/out_head" "$R/pc/out_wt" > "$R/pc/diff.txt"; then echo "PAPER-CHAIN-IDENTICAL files=$n"; else echo "PAPER-CHAIN-DIFFERS files=$n"; fi
md5sum "$R"/pc/out_head/* | head -3
