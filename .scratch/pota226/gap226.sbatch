#!/bin/bash
#SBATCH --job-name=pota226-gap
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --time=00:30:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=/data/gpfs/projects/punim2657/sfs-fix-226/gap226_%j.out
#SBATCH --error=/data/gpfs/projects/punim2657/sfs-fix-226/gap226_%j.err
set -uo pipefail
echo "candidate surfaces:"; md5sum /data/gpfs/projects/punim2657/pota221_ladder/thr_10/Pot_D_Piece_25_Surface_*.xyz /data/gpfs/projects/punim2657/pota221_ladder/thr_8/Pot_D_Piece_25_Surface_*.xyz /data/gpfs/projects/punim2657/pota221_ladder/thr_4p5/Pot_D_Piece_25_Surface_*.xyz /data/gpfs/projects/punim2657/pota221_ladder/thr_8/Pot_D_Piece_27_Surface_*.xyz
/data/gpfs/projects/punim2657/MILo/envs/milo/bin/python /data/gpfs/projects/punim2657/sfs-fix-226/gap226sym.py
