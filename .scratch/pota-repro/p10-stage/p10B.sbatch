#!/bin/bash
#SBATCH --job-name=p10B
#SBATCH --partition=sapphire
#SBATCH --time=02:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --output=/data/gpfs/projects/punim2657/Temp/potsac-p10-run/p10B-%j.out
module load MATLAB/2025b
matlab -batch "addpath('/data/gpfs/projects/punim2657/Temp/potsac-p10-run'); p10_run('B', 1:9)"