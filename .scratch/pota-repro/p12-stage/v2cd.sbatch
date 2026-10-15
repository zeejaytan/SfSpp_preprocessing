#!/bin/bash
#SBATCH --job-name=p12-v2cd
#SBATCH --partition=sapphire
#SBATCH --time=01:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=2
#SBATCH --output=/data/gpfs/projects/punim2657/Temp/potsac-p12-run/v2cd-%j.out
module load MATLAB/2025b
matlab -batch "run('/data/gpfs/projects/punim2657/Temp/potsac-p12-run/v2c_diag.m')"
