#!/bin/bash
#SBATCH --job-name=p15b-p06
#SBATCH --partition=sapphire
#SBATCH --time=02:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --output=/data/gpfs/projects/punim2657/Temp/potsac-p15-run/p15b-%j.out
module load MATLAB/2025b
matlab -batch "run('/data/gpfs/projects/punim2657/Temp/potsac-p15-run/p15b_fit.m')"
