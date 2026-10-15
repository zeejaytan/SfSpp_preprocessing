#!/bin/bash
#SBATCH --job-name=p17type
#SBATCH --partition=sapphire
#SBATCH --time=01:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --output=/data/gpfs/projects/punim2657/Temp/potsac-p17-run/p17type-%j.out
module load MATLAB/2025b
matlab -batch "addpath('/data/gpfs/projects/punim2657/Temp/potsac-p17-run'); p17_type({'H',1:11;'G',[6 7];'D',[27 30];'A',[7 8]})"
