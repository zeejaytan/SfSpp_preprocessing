#!/bin/bash
#SBATCH --job-name=p17peel
#SBATCH --partition=sapphire
#SBATCH --time=03:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --output=/data/gpfs/projects/punim2657/Temp/potsac-p17-run/p17peel-%j.out
module load MATLAB/2025b
matlab -batch "addpath('/data/gpfs/projects/punim2657/Temp/potsac-p17-run'); p17_peel({'H',1:11;'G',[6 7];'D',[27 30];'A',7})"
